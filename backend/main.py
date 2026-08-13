import os
import time
import subprocess
import threading
import cv2
import numpy as np
import psutil
from fastapi import FastAPI, Response
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

CAM_ID = int(os.getenv("CAMERA_INDEX", "0"))
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace/student_data")


def generate_siemens_star_fallback():
    """Generates a synthetic Siemens Star pattern for hardware testing fallback."""
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
    
    cv2.putText(img, "HFU AI-LAB - CAMERA FALLBACK (DEMO MODE)", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)
    return img


def check_camera_index_with_timeout(idx):
    """Runs an isolated 2-second subprocess to check if camera index works without hanging."""
    test_script = f"""
import cv2, numpy as np, sys
try:
    cap = cv2.VideoCapture({idx}, cv2.CAP_V4L2)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None and np.mean(frame) > 2.0:
            sys.exit(0)
except Exception:
    pass
sys.exit(1)
"""
    try:
        res = subprocess.run(["python3", "-c", test_script], timeout=2.0, capture_output=True)
        return res.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[CAMERA] Index {idx} timed out (CSI/Driver hanging node skipped).")
        return False


# Subprocess-Protected Non-Blocking Camera Manager
class CameraManager:
    def __init__(self):
        self.cap = None
        self.active_index = -1
        self.is_real = False
        self.current_frame = generate_siemens_star_fallback()
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _try_open_camera(self):
        indices_to_try = [CAM_ID] + [i for i in range(4) if i != CAM_ID]
        for idx in indices_to_try:
            device_path = f"/dev/video{idx}"
            if os.path.exists(device_path):
                # Verify index with timeout first so OpenCV never hangs the server
                if check_camera_index_with_timeout(idx):
                    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        ret, frame = cap.read()
                        if ret and frame is not None and np.mean(frame) > 2.0:
                            self.cap = cap
                            self.active_index = idx
                            self.is_real = True
                            print(f"[CAMERA] Successfully opened USB webcam on {device_path}")
                            return True
                        cap.release()

        self.is_real = False
        self.cap = None
        return False

    def _update_loop(self):
        """Dedicated background thread reading V4L2 device safely."""
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if not self._try_open_camera():
                    with self.lock:
                        self.current_frame = generate_siemens_star_fallback()
                        self.is_real = False
                    time.sleep(2.0)
                    continue

            ret, frame = self.cap.read()
            if ret and frame is not None and np.mean(frame) > 2.0:
                with self.lock:
                    self.current_frame = frame
                    self.is_real = True
            else:
                if self.cap:
                    self.cap.release()
                    self.cap = None
                with self.lock:
                    self.current_frame = generate_siemens_star_fallback()
                    self.is_real = False
                time.sleep(1.0)

            time.sleep(0.04) # ~25 FPS

    def get_latest_frame(self):
        with self.lock:
            return self.current_frame.copy(), self.is_real

camera_mgr = CameraManager()


def mjpeg_stream_generator():
    """MJPEG stream generator serving multiple client tabs smoothly."""
    while True:
        frame, is_real_cam = camera_mgr.get_latest_frame()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_text = f"CAM: ONLINE (/dev/video{camera_mgr.active_index})" if is_real_cam else "CAM: SIMULATED (DEMO)"
        color = (0, 200, 0) if is_real_cam else (0, 165, 255)
        
        cv2.putText(frame, f"{status_text} | {timestamp}", (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.04) # ~25 FPS


@app.get("/api/stream")
@app.head("/api/stream")
def video_feed():
    """Live MJPEG Camera Stream Endpoint."""
    return StreamingResponse(mjpeg_stream_generator(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/status")
def system_status():
    """Comprehensive Hardware & Environment Status Endpoint."""
    cam_online = camera_mgr.is_real

    # Get RAM & CPU
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=None)

    # Check SSID / Hostapd
    ssid = "AI-LAB-ORIN-01"
    try:
        if os.path.exists("config/ap_ssid.txt"):
            with open("config/ap_ssid.txt", "r") as f:
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
            "device": f"/dev/video{camera_mgr.active_index}" if cam_online else "/dev/video0",
            "mode": f"Real USB Webcam (/dev/video{camera_mgr.active_index})" if cam_online else "Siemens Star Fallback"
        },
        "wlan": {
            "ssid": ssid,
            "ip": "192.168.4.1",
            "active": True
        },
        "docker": {
            "frontend": "running",
            "backend": "running",
            "jupyter": "running"
        },
        "system": {
            "cpu_percent": cpu_percent,
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "ram_percent": mem.percent
        }
    })


@app.post("/api/export-usb")
def export_to_usb():
    """Trigger student USB export script."""
    try:
        res = subprocess.run(["bash", "scripts/export_to_usb.sh"], capture_output=True, text=True)
        return JSONResponse({
            "success": res.returncode == 0,
            "output": res.stdout,
            "error": res.stderr
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/reset")
def reset_workspace():
    """Trigger student workspace reset script."""
    try:
        res = subprocess.run(["bash", "scripts/reset_session.sh"], capture_output=True, text=True)
        return JSONResponse({
            "success": res.returncode == 0,
            "output": res.stdout,
            "error": res.stderr
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
