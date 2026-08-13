import os
import time
import subprocess
import threading
import cv2
import numpy as np
import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI(title="HFU AI-LAB Jetson Orin Nano API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UGREEN Camera confirmed at /dev/video0 on this Jetson setup
CAM_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace/student_data")


def generate_siemens_star_fallback(msg="DEMO MODE"):
    size = (480, 640, 3)
    img = np.ones(size, dtype=np.uint8) * 255
    center = (320, 240)
    radius = 200
    for i in range(36):
        if i % 2 == 0:
            a1 = i * (360 / 36) * np.pi / 180
            a2 = (i + 1) * (360 / 36) * np.pi / 180
            p1 = (int(center[0] + radius * np.cos(a1)), int(center[1] + radius * np.sin(a1)))
            p2 = (int(center[0] + radius * np.cos(a2)), int(center[1] + radius * np.sin(a2)))
            cv2.fillPoly(img, [np.array([center, p1, p2], np.int32)], (0, 0, 0))
    cv2.putText(img, f"HFU AI-LAB | {msg}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 2)
    return img


class StreamEngine:
    """
    Opens /dev/video0 (UGREEN UVC webcam) ONCE and keeps it open continuously.
    LED stays solid ON. Auto-reconnects if unplugged.
    """
    def __init__(self):
        self.cap = None
        self.is_real = False
        self.current_frame = generate_siemens_star_fallback("Starting camera...")
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _open_camera(self):
        """Open the UVC webcam at CAM_INDEX (0 = /dev/video0 UGREEN)."""
        try:
            cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
            if not cap.isOpened():
                print(f"[CAMERA] Could not open /dev/video{CAM_INDEX}")
                return None

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 30)

            # Drain the buffer with warmup frames (UVC cameras need this)
            print(f"[CAMERA] Warming up /dev/video{CAM_INDEX}...")
            for _ in range(10):
                cap.grab()
                time.sleep(0.05)

            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                print(f"[CAMERA] ✅ /dev/video{CAM_INDEX} (UGREEN) opened successfully - LED ON")
                return cap
            else:
                print(f"[CAMERA] ❌ /dev/video{CAM_INDEX} opened but no frames returned")
                cap.release()
                return None
        except Exception as e:
            print(f"[CAMERA] Exception opening /dev/video{CAM_INDEX}: {e}")
            return None

    def _loop(self):
        failures = 0
        while self.running:
            # Open camera if not yet open
            if self.cap is None:
                self.cap = self._open_camera()
                if self.cap is None:
                    with self.lock:
                        self.current_frame = generate_siemens_star_fallback(
                            f"Camera not ready (/dev/video{CAM_INDEX})"
                        )
                        self.is_real = False
                    time.sleep(2.0)
                    continue

            # Read frames continuously from the already-open camera
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                failures = 0
                with self.lock:
                    self.current_frame = frame.copy()
                    self.is_real = True
            else:
                failures += 1
                if failures > 20:
                    print("[CAMERA] ⚠️ Stream lost. Releasing and reconnecting...")
                    self.cap.release()
                    self.cap = None
                    failures = 0
                    with self.lock:
                        self.current_frame = generate_siemens_star_fallback("Reconnecting...")
                        self.is_real = False
                    time.sleep(1.0)

            time.sleep(0.033)  # ~30 FPS

    def get_frame(self):
        with self.lock:
            return self.current_frame.copy(), self.is_real


stream_engine = StreamEngine()


def mjpeg_stream_generator():
    while True:
        frame, is_real = stream_engine.get_frame()
        ts = time.strftime("%H:%M:%S")
        label = f"CAM /dev/video{CAM_INDEX} | {ts}" if is_real else f"DEMO MODE | {ts}"
        color = (0, 200, 0) if is_real else (0, 100, 255)
        cv2.putText(frame, label, (10, frame.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.033)


@app.get("/api/stream")
@app.head("/api/stream")
def video_feed():
    return StreamingResponse(mjpeg_stream_generator(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/status")
def system_status():
    _, cam_online = stream_engine.get_frame()
    mem = psutil.virtual_memory()
    ssid = "AI-LAB-ORIN-01"
    try:
        if os.path.exists("config/ap_ssid.txt"):
            with open("config/ap_ssid.txt") as f:
                for line in f:
                    if "ssid=" in line:
                        ssid = line.split("=")[1].strip()
    except Exception:
        pass

    return JSONResponse({
        "status": "online",
        "station": "HFU Jetson Orin Nano AI-Workstation",
        "camera": {
            "online": cam_online,
            "device": f"/dev/video{CAM_INDEX}",
            "mode": f"UGREEN USB Webcam (/dev/video{CAM_INDEX})" if cam_online else "Siemens Star Fallback"
        },
        "wlan": {"ssid": ssid, "ip": "192.168.4.1", "active": True},
        "docker": {"frontend": "running", "backend": "running", "jupyter": "running"},
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "ram_percent": mem.percent
        }
    })


@app.post("/api/export-usb")
def export_to_usb():
    try:
        res = subprocess.run(["bash", "scripts/export_to_usb.sh"], capture_output=True, text=True)
        return JSONResponse({"success": res.returncode == 0, "output": res.stdout, "error": res.stderr})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/reset")
def reset_workspace():
    try:
        res = subprocess.run(["bash", "scripts/reset_session.sh"], capture_output=True, text=True)
        return JSONResponse({"success": res.returncode == 0, "output": res.stdout, "error": res.stderr})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
