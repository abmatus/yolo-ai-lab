"""
HFU AI-LAB Backend – UGREEN USB Webcam Streaming Server
Fixes applied:
  - JPEG encoded ONCE in background thread, not per-client
  - Async stream generator (no blocking of FastAPI event loop)
  - cap.read() without extra sleep (V4L2 driver throttles itself)
  - latest_jpeg stored as bytes, no numpy copy per client
"""
import asyncio
import os
import subprocess
import threading
import time
from typing import Optional

import cv2
import numpy as np
import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI(title="HFU AI-LAB Jetson Orin Nano API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UGREEN UVC Webcam confirmed on /dev/video0 (Jetson Orin Nano, L4T r39.2)
CAM_INDEX   = int(os.getenv("CAMERA_INDEX", "0"))
TARGET_FPS  = 25
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace/student_data")


# ---------------------------------------------------------------------------
# Siemens Star fallback frame
# ---------------------------------------------------------------------------
def _make_siemens_star(msg: str = "DEMO MODE") -> bytes:
    img = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cx, cy, r = 320, 240, 200
    for i in range(36):
        if i % 2 == 0:
            a1 = np.deg2rad(i * 10)
            a2 = np.deg2rad((i + 1) * 10)
            pts = np.array([
                [cx, cy],
                [int(cx + r * np.cos(a1)), int(cy + r * np.sin(a1))],
                [int(cx + r * np.cos(a2)), int(cy + r * np.sin(a2))],
            ], dtype=np.int32)
            cv2.fillPoly(img, [pts], (0, 0, 0))
    cv2.putText(img, f"HFU AI-LAB | {msg}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 2)
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return buf.tobytes()


# ---------------------------------------------------------------------------
# StreamEngine
# ---------------------------------------------------------------------------
class StreamEngine:
    """
    Single background thread:
      1. Opens /dev/video{CAM_INDEX} ONCE with V4L2 + MJPG (LED stays ON)
      2. Reads frames at native camera FPS (cap.read() blocks until frame ready)
      3. Encodes to JPEG once per frame (NOT per client connection)
      4. Stores encoded bytes in self._jpeg behind a threading.Event

    Clients call get_latest_jpeg() which returns the pre-encoded bytes instantly.
    No numpy copy, no per-client JPEG encoding.
    """

    def __init__(self):
        self._jpeg: bytes = _make_siemens_star("Starting camera…")
        self._lock = threading.Lock()
        self._frame_event = threading.Event()  # set when new JPEG is ready
        self.is_real = False
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="cam-reader")
        self._thread.start()

    # ------------------------------------------------------------------
    def _open(self) -> Optional[cv2.VideoCapture]:
        print(f"[CAM] Opening /dev/video{CAM_INDEX} …")
        cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"[CAM] ❌ Cannot open /dev/video{CAM_INDEX}")
            return None

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)

        # Drain stale buffer frames — UVC cameras queue old frames on open
        for _ in range(8):
            cap.grab()

        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            print(f"[CAM] ✅ /dev/video{CAM_INDEX} ready — LED ON")
            return cap

        print(f"[CAM] ❌ /dev/video{CAM_INDEX} opened but returned no frame")
        cap.release()
        return None

    # ------------------------------------------------------------------
    def _loop(self):
        consecutive_failures = 0

        while self._running:
            # ---- (Re-)open camera if needed --------------------------
            if self._cap is None:
                self._cap = self._open()
                if self._cap is None:
                    with self._lock:
                        self._jpeg = _make_siemens_star(f"Camera unavailable (/dev/video{CAM_INDEX})")
                        self.is_real = False
                    self._frame_event.set()
                    time.sleep(3.0)
                    continue
                consecutive_failures = 0

            # ---- Read frame (V4L2 blocks until a frame is ready) -----
            ret, frame = self._cap.read()

            if ret and frame is not None and frame.size > 0:
                consecutive_failures = 0
                ts = time.strftime("%H:%M:%S")
                cv2.putText(frame, f"/dev/video{CAM_INDEX} | {ts}",
                            (10, frame.shape[0] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 0), 1, cv2.LINE_AA)
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                with self._lock:
                    self._jpeg = buf.tobytes()
                    self.is_real = True
                self._frame_event.set()
            else:
                consecutive_failures += 1
                if consecutive_failures >= 30:
                    print("[CAM] ⚠️  Stream lost — releasing and reconnecting …")
                    self._cap.release()
                    self._cap = None
                    consecutive_failures = 0
                    with self._lock:
                        self._jpeg = _make_siemens_star("Reconnecting…")
                        self.is_real = False
                    self._frame_event.set()
                    time.sleep(1.0)
                # no sleep here — let cap.read() block naturally

    # ------------------------------------------------------------------
    def get_latest_jpeg(self) -> bytes:
        """Return the latest pre-encoded JPEG bytes (no copy overhead)."""
        with self._lock:
            return self._jpeg

    def get_status(self) -> bool:
        return self.is_real


stream_engine = StreamEngine()


# ---------------------------------------------------------------------------
# ASYNC MJPEG stream generator — does NOT block the FastAPI event loop
# ---------------------------------------------------------------------------
async def _mjpeg_gen():
    interval = 1.0 / TARGET_FPS
    while True:
        jpeg = stream_engine.get_latest_jpeg()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg +
            b"\r\n"
        )
        await asyncio.sleep(interval)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/stream")
@app.head("/api/stream")
async def video_feed():
    return StreamingResponse(
        _mjpeg_gen(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/status")
def system_status():
    cam_online = stream_engine.get_status()
    mem = psutil.virtual_memory()
    ssid = "AI-LAB-ORIN-01"
    try:
        with open("config/ap_ssid.txt") as f:
            for line in f:
                if "ssid=" in line:
                    ssid = line.split("=", 1)[1].strip()
    except Exception:
        pass

    return JSONResponse({
        "status": "online",
        "station": "HFU Jetson Orin Nano AI-Workstation",
        "camera": {
            "online": cam_online,
            "device": f"/dev/video{CAM_INDEX}",
            "mode": f"UGREEN UVC (/dev/video{CAM_INDEX})" if cam_online else "Siemens Star Fallback",
        },
        "wlan":   {"ssid": ssid, "ip": "192.168.4.1", "active": True},
        "docker": {"frontend": "running", "backend": "running", "jupyter": "running"},
        "system": {
            "cpu_percent":  psutil.cpu_percent(interval=None),
            "ram_used_gb":  round(mem.used  / 1024**3, 2),
            "ram_total_gb": round(mem.total / 1024**3, 2),
            "ram_percent":  mem.percent,
        },
    })


@app.post("/api/export-usb")
def export_to_usb():
    try:
        res = subprocess.run(["bash", "scripts/export_to_usb.sh"],
                             capture_output=True, text=True)
        return JSONResponse({"success": res.returncode == 0,
                             "output": res.stdout, "error": res.stderr})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/reset")
def reset_workspace():
    try:
        res = subprocess.run(["bash", "scripts/reset_session.sh"],
                             capture_output=True, text=True)
        return JSONResponse({"success": res.returncode == 0,
                             "output": res.stdout, "error": res.stderr})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
