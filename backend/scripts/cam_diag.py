#!/usr/bin/env python3
"""
HFU AI-LAB Camera Diagnostic Tool
Scans all /dev/video* devices and prints their V4L2 capabilities.
Run inside the backend container:
  docker exec hfu_ai_backend python3 /app/scripts/cam_diag.py
"""
import subprocess
import os
import cv2
import numpy as np

print("=" * 60)
print("HFU AI-LAB Camera Diagnostic")
print("=" * 60)

# Step 1: List all /dev/video* devices
devices = sorted([f for f in os.listdir("/dev") if f.startswith("video")])
print(f"\n[1] Found /dev/video* devices: {['/dev/' + d for d in devices]}\n")

# Step 2: Use v4l2-ctl to check card name (distinguishes CSI vs USB)
print("[2] Device details (v4l2-ctl):")
for dev in devices:
    path = f"/dev/{dev}"
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--device", path, "--info"],
            capture_output=True, text=True, timeout=2
        )
        lines = [l.strip() for l in result.stdout.splitlines() if "Card" in l or "Bus" in l or "Driver" in l]
        print(f"  {path}: {' | '.join(lines) if lines else 'No info'}")
    except Exception as e:
        print(f"  {path}: Error - {e}")

# Step 3: Try opening each device with OpenCV and read frames
print("\n[3] OpenCV VideoCapture test (V4L2 backend):")
for dev in devices:
    idx = int(dev.replace("video", ""))
    path = f"/dev/{dev}"
    try:
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        opened = cap.isOpened()
        frame_ok = False
        brightness = 0
        if opened:
            for _ in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    frame_ok = True
                    brightness = float(np.mean(frame))
        cap.release()
        print(f"  /dev/video{idx}: opened={opened}, frame_ok={frame_ok}, brightness={brightness:.1f}")
    except Exception as e:
        print(f"  /dev/video{idx}: Exception - {e}")

print("\n" + "=" * 60)
print("Diagnostic complete. Look for device with frame_ok=True and brightness > 2")
print("=" * 60)
