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

CAM_ID = int(os.getenv("CAMERA_INDEX", "-1"))  # -1 = auto-detect
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace/student_data")


def generate_siemens_star_fallback(message="NO CAMERA - DEMO MODE"):
    """Generates a synthetic Siemens Star test pattern."""
    size = (480, 640, 3)
    img = np.ones(size, dtype=np.uint8) * 255
    center = (320, 240)
    radius = 200
    num_spokes = 36
    for i in range(num_spokes):
        if i % 2 == 0:
            angle1 = i * (360 / num_spokes) * np.pi / 180
            angle2 = (i + 1) * (360 / num_spokes) * np.pi / 180
            pt1 = (int(center[0] + radius * np.cos(angle1)), int(center[1] + radius * np.sin(angle1)))
            pt2 = (int(center[0] + radius * np.cos(angle2)), int(center[1] + radius * np.sin(angle2)))
            pts = np.array([center, pt1, pt2], np.int32)
            cv2.fillPoly(img, [pts], (0, 0, 0))
    cv2.putText(img, f"HFU AI-LAB | {message}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 2)
    return img


def detect_usb_webcam_index():
    """
    Uses v4l2-ctl to detect ONLY real USB webcam nodes (skips Jetson CSI driver nodes).
    Returns the index of the first working USB webcam, or -1 if none found.
    """
    all_video_devs = sorted([
        int(f.replace("video", ""))
        for f in os.listdir("/dev")
        if f.startswith("video") and f[5:].isdigit()
    ])

    for idx in all_video_devs:
        path = f"/dev/video{idx}"
        try:
            # Use v4l2-ctl to read device info - CSI nodes show 'tegra' in bus_info
            res = subprocess.run(
                ["v4l2-ctl", "--device", path, "--info"],
                capture_output=True, text=True, timeout=1.5
            )
            info = res.stdout.lower()

            # Skip Jetson-internal CSI/tegra driver nodes
            if "tegra" in info or "nvcsi" in info or "vivid" in info:
                print(f"[CAMERA] Skipping CSI/internal node: {path}")
                continue

            # Quick OpenCV test - only 2 warmup frames, no re-open
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if not cap.isOpened():
                cap.release()
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            found = False
            for _ in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    found = True
                    break
                time.sleep(0.05)

            cap.release()
            if found:
                print(f"[CAMERA] ✅ USB Webcam detected at {path}")
                return idx
            else:
                print(f"[CAMERA] {path} opened but no frames received.")

        except subprocess.TimeoutExpired:
            print(f"[CAMERA] v4l2-ctl timeout on {path}, skipping.")
        except Exception as e:
            print(f"[CAMERA] Error checking {path}: {e}")

    return -1


class StreamEngine:
    """
    Robust persistent stream engine:
    - Opens the USB webcam exactly ONCE (LED stays solid ON)
    - Continuously reads frames in a background thread
    - Falls back to Siemens Star if no camera found
    - Auto-reconnects if camera is unplugged/replugged
    """
    def __init__(self):
        self.cap = None
        self.active_index = -1
        self.is_real = False
        self.current_frame = generate_siemens_star_fallback("Scanning for camera...")
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _try_open(self, idx):
        """Open camera at index persistently with MJPG and buffered read."""
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if not cap.isOpened():
                return None

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 30)

            # Drain buffer with 5 warmup frames
            for _ in range(5):
                cap.read()
                time.sleep(0.03)

            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                print(f"[CAMERA] ✅ Persistent stream opened on /dev/video{idx} (LED ON)")
                return cap
            cap.release()
        except Exception as e:
            print(f"[CAMERA] Open error on /dev/video{idx}: {e}")
        return None

    def _update_loop(self):
        failures = 0
        while self.running:
            # Open camera if not already open
            if self.cap is None:
                # First try CAM_ID env, then auto-detect
                idx = CAM_ID if CAM_ID >= 0 else detect_usb_webcam_index()
                if idx >= 0:
                    self.cap = self._try_open(idx)
                    if self.cap:
                        self.active_index = idx
                        self.is_real = True
                        failures = 0
                    else:
                        with self.lock:
                            self.current_frame = generate_siemens_star_fallback(f"Camera open failed on /dev/video{idx}")
                        time.sleep(2.0)
                        continue
                else:
                    with self.lock:
                        self.current_frame = generate_siemens_star_fallback("No USB webcam found")
                        self.is_real = False
                        self.active_index = -1
                    time.sleep(3.0)
                    continue

            # Read frame from persistent open camera
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                failures = 0
                with self.lock:
                    self.current_frame = frame
                    self.is_real = True
            else:
                failures += 1
                if failures > 15:
                    print("[CAMERA] ⚠️ Lost connection. Releasing and reconnecting...")
                    self.cap.release()
                    self.cap = None
                    self.active_index = -1
                    with self.lock:
                        self.current_frame = generate_siemens_star_fallback("Reconnecting...")
                        self.is_real = False
                    failures = 0
                    time.sleep(1.0)

            time.sleep(0.033)  # ~30 FPS

    def get_frame(self):
        with self.lock:
            return self.current_frame.copy(), self.is_real, self.active_index


stream_engine = StreamEngine()


def mjpeg_stream_generator():
    while True:
        frame, is_real_cam, active_idx = stream_engine.get_frame()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status = f"CAM ONLINE /dev/video{active_idx}" if is_real_cam else "DEMO MODE - No Camera"
        color = (0, 200, 0) if is_real_cam else (0, 100, 255)
        cv2.putText(frame, f"{status} | {timestamp}", (10, frame.shape[0] - 12),
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
    _, cam_online, active_idx = stream_engine.get_frame()
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
            "device": f"/dev/video{active_idx}" if cam_online else "none",
            "mode": f"Real USB Webcam (/dev/video{active_idx})" if cam_online else "Siemens Star Fallback"
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
