import os
import time
import subprocess
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

# Persistent Camera Manager
class CameraManager:
    def __init__(self):
        self.cap = None
        self.active_index = -1
        self.last_frame = None
        self.is_real = False

    def find_and_open_camera(self):
        """Scans video indices 0, 1, 2, 3 to find any working USB webcam."""
        indices_to_try = [CAM_ID] + [i for i in range(4) if i != CAM_ID]
        for idx in indices_to_try:
            device_path = f"/dev/video{idx}"
            if os.path.exists(device_path):
                cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        self.cap = cap
                        self.active_index = idx
                        self.is_real = True
                        print(f"[CAMERA] Successfully opened USB webcam on {device_path}")
                        return True
                    cap.release()
        
        self.is_real = False
        return False

    def get_frame(self):
        """Gets a frame from the active USB camera or returns Siemens Star fallback."""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.last_frame = frame
                return frame, True

        # Try to reconnect camera
        if self.find_and_open_camera():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.last_frame = frame
                return frame, True

        return generate_siemens_star_fallback(), False

camera_mgr = CameraManager()


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


def mjpeg_stream_generator():
    """MJPEG stream generator for live camera view."""
    while True:
        frame, is_real_cam = camera_mgr.get_frame()
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
    frame, cam_online = camera_mgr.get_frame()

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
