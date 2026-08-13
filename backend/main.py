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


def grab_frame_subprocess(idx):
    """Isolated 1.5s subprocess trying MJPG, YUYV & default formats on camera index."""
    script = f"""
import cv2, numpy as np, sys

def try_cap(backend, fourcc=None):
    try:
        cap = cv2.VideoCapture({idx}, backend) if backend is not None else cv2.VideoCapture({idx})
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            if fourcc:
                cap.set(cv2.CAP_PROP_FOURCC, fourcc)
            
            # Read up to 3 frames for camera warmup
            frame = None
            for _ in range(3):
                ret, f = cap.read()
                if ret and f is not None and f.size > 0:
                    frame = f
            cap.release()
            
            if frame is not None and np.mean(frame) > 0.5:
                ret_bytes, jpg = cv2.imencode('.jpg', frame)
                if ret_bytes:
                    sys.stdout.buffer.write(jpg.tobytes())
                    sys.exit(0)
    except Exception:
        pass

# 1. Try V4L2 + MJPG
try_cap(cv2.CAP_V4L2, cv2.VideoWriter_fourcc(*'MJPG'))
# 2. Try V4L2 default format
try_cap(cv2.CAP_V4L2, None)
# 3. Try default OpenCV backend
try_cap(None, None)

sys.exit(1)
"""
    try:
        res = subprocess.run(["python3", "-c", script], timeout=1.5, capture_output=True)
        if res.returncode == 0 and len(res.stdout) > 500:
            frame = cv2.imdecode(np.frombuffer(res.stdout, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                return frame, True
    except subprocess.TimeoutExpired:
        pass
    return None, False


# Non-Blocking Background Stream Engine
class StreamEngine:
    def __init__(self):
        self.current_frame = generate_siemens_star_fallback()
        self.is_real = False
        self.active_index = -1
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while self.running:
            found = False
            # Check indices 0, 1, 2, 3
            indices_to_try = [CAM_ID] + [i for i in range(4) if i != CAM_ID]
            for idx in indices_to_try:
                if os.path.exists(f"/dev/video{idx}"):
                    frame, is_real = grab_frame_subprocess(idx)
                    if is_real and frame is not None:
                        with self.lock:
                            self.current_frame = frame
                            self.is_real = True
                            self.active_index = idx
                        found = True
                        break

            if not found:
                with self.lock:
                    self.current_frame = generate_siemens_star_fallback()
                    self.is_real = False
                    self.active_index = -1
                time.sleep(1.0)
            else:
                time.sleep(0.04) # ~25 FPS

    def get_frame(self):
        with self.lock:
            return self.current_frame.copy(), self.is_real, self.active_index

stream_engine = StreamEngine()


def mjpeg_stream_generator():
    """MJPEG stream generator serving multiple client tabs smoothly."""
    while True:
        frame, is_real_cam, active_idx = stream_engine.get_frame()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_text = f"CAM: ONLINE (/dev/video{active_idx})" if is_real_cam else "CAM: SIMULATED (DEMO)"
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
    frame, cam_online, active_idx = stream_engine.get_frame()

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
            "device": f"/dev/video{active_idx}" if cam_online else "/dev/video0",
            "mode": f"Real USB Webcam (/dev/video{active_idx})" if cam_online else "Siemens Star Fallback"
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
