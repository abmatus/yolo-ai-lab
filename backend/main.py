"""
HFU AI-LAB Backend – Complete API Server
Python 3.8 compatible (ultralytics >= 8.3 for YOLO11 support)
"""
import asyncio
import glob
import json
import os
import shutil
import subprocess
import threading
import time
import uuid
import zipfile
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import psutil
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (FileResponse, JSONResponse, StreamingResponse)
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CAM_INDEX     = int(os.getenv("CAMERA_INDEX", "0"))
CAM_PATH      = f"/dev/video{CAM_INDEX}"
TARGET_FPS    = 25
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace/student_data")
IMAGES_DIR    = os.path.join(WORKSPACE_DIR, "images")
LABELS_DIR    = os.path.join(WORKSPACE_DIR, "labels")
MODELS_DIR    = os.path.join(WORKSPACE_DIR, "models")
EXPORTS_DIR   = os.path.join(WORKSPACE_DIR, "exports")
CLASSES_FILE  = os.path.join(WORKSPACE_DIR, "classes.txt")
CONFIG_DIR    = "/app/config"
ADMIN_PIN_FILE = os.path.join(CONFIG_DIR, "admin_pin.txt")
DEFAULT_CLASSES = ["Objekt_A", "Objekt_B", "Objekt_C"]

for _d in [IMAGES_DIR, LABELS_DIR, MODELS_DIR, EXPORTS_DIR, CONFIG_DIR]:
    os.makedirs(_d, exist_ok=True)

if not os.path.exists(CLASSES_FILE):
    with open(CLASSES_FILE, "w") as _f:
        _f.write("\n".join(DEFAULT_CLASSES))

if not os.path.exists(ADMIN_PIN_FILE):
    with open(ADMIN_PIN_FILE, "w") as _f:
        _f.write("1234")

app = FastAPI(title="HFU AI-LAB API", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------------------
# Siemens Star fallback frame
# ---------------------------------------------------------------------------
def _make_siemens_star(msg: str = "DEMO MODE") -> bytes:
    img = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cx, cy, r = 320, 240, 200
    for i in range(36):
        if i % 2 == 0:
            a1, a2 = np.deg2rad(i * 10), np.deg2rad((i + 1) * 10)
            pts = np.array([[cx, cy],
                            [int(cx + r * np.cos(a1)), int(cy + r * np.sin(a1))],
                            [int(cx + r * np.cos(a2)), int(cy + r * np.sin(a2))]],
                           dtype=np.int32)
            cv2.fillPoly(img, [pts], (0, 0, 0))
    cv2.putText(img, f"HFU AI-LAB | {msg}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 2)
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return buf.tobytes()


# ---------------------------------------------------------------------------
# StreamEngine – persistent USB webcam capture
# ---------------------------------------------------------------------------
class StreamEngine:
    def __init__(self):
        self._jpeg: bytes = _make_siemens_star("Starting camera…")
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self.is_real = False
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = True
        threading.Thread(target=self._loop, daemon=True, name="cam-reader").start()

    def _open(self) -> Optional[cv2.VideoCapture]:
        print(f"[CAM] Opening {CAM_PATH}…")
        cap = cv2.VideoCapture(CAM_PATH, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"[CAM] ❌ Cannot open {CAM_PATH}")
            return None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        for attempt in range(30):
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                print(f"[CAM] ✅ {CAM_PATH} ready (brightness: {np.mean(frame):.1f})")
                return cap
            time.sleep(0.05)
        cap.release()
        return None

    def _loop(self):
        failures = 0
        while self._running:
            if self._cap is None:
                self._cap = self._open()
                if self._cap is None:
                    with self._lock:
                        self._jpeg = _make_siemens_star(f"Camera unavailable ({CAM_PATH})")
                        self.is_real = False
                    time.sleep(3.0)
                    continue
                failures = 0
            ret, frame = self._cap.read()
            if ret and frame is not None and frame.size > 0:
                failures = 0
                ts = time.strftime("%H:%M:%S")
                cv2.putText(frame, f"{CAM_PATH} | {ts}",
                            (10, frame.shape[0] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 0), 1)
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                with self._lock:
                    self._jpeg = buf.tobytes()
                    self._frame = frame.copy()
                    self.is_real = True
            else:
                failures += 1
                if failures >= 60:
                    self._cap.release()
                    self._cap = None
                    failures = 0
                    with self._lock:
                        self._jpeg = _make_siemens_star("Reconnecting…")
                        self.is_real = False
                    time.sleep(2.0)

    def get_latest_jpeg(self) -> bytes:
        with self._lock:
            return self._jpeg

    def get_latest_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def get_status(self) -> bool:
        return self.is_real


stream_engine = StreamEngine()


# ---------------------------------------------------------------------------
# InferenceEngine – YOLO live inference
# ---------------------------------------------------------------------------
BUILTIN_MODELS = ["yolo11n", "yolo11s", "yolo11m", "yolov8n", "yolov8s"]

class InferenceEngine:
    def __init__(self):
        self._model = None
        self.model_name = "yolo11n"
        self.conf = 0.45
        self.show_boxes = True
        self._loading = False
        self._lock = threading.Lock()
        self._fps_times: List[float] = []
        self._last_ms = 0.0
        self._last_dets: List[Dict] = []
        threading.Thread(target=lambda: self._load("yolo11n"), daemon=True).start()

    def _load(self, name: str):
        try:
            self._loading = True
            from ultralytics import YOLO  # type: ignore
            path = os.path.join(MODELS_DIR, name) if not name.endswith(".pt") else name
            if not os.path.exists(path):
                path = name + ".pt" if not name.endswith(".pt") else name
            mdl = YOLO(path)
            with self._lock:
                self._model = mdl
                self.model_name = name
        except Exception as e:
            print(f"[INFER] Load error: {e}")
        finally:
            self._loading = False

    def set_config(self, model: Optional[str], conf: Optional[float], show_boxes: Optional[bool]):
        if model and model != self.model_name:
            threading.Thread(target=lambda: self._load(model), daemon=True).start()
        with self._lock:
            if conf is not None:
                self.conf = conf
            if show_boxes is not None:
                self.show_boxes = show_boxes

    def infer(self, frame: np.ndarray):
        t0 = time.time()
        with self._lock:
            if self._model is None:
                cv2.putText(frame, "Loading YOLO model…", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
                return frame, []
            model, conf, show = self._model, self.conf, self.show_boxes

        results = model.predict(frame, conf=conf, verbose=False)
        dets: List[Dict] = []
        if show and results:
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    c = float(box.conf[0])
                    dets.append({"class": cls_name, "confidence": round(c, 2), "class_id": cls_id})
                    color = _class_color(cls_id)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    lbl = f"{cls_name} {c:.2f}"
                    (tw, th), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
                    cv2.putText(frame, lbl, (x1 + 3, y1 - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        ms = (time.time() - t0) * 1000
        with self._lock:
            self._last_ms = ms
            self._last_dets = dets
            now = time.time()
            self._fps_times = [t for t in self._fps_times if now - t < 2.0]
            self._fps_times.append(now)
        return frame, dets

    def get_stats(self) -> Dict:
        with self._lock:
            fps = len(self._fps_times) / 2.0
            return {
                "fps": round(fps, 1),
                "infer_ms": round(self._last_ms, 1),
                "model": self.model_name,
                "loading": self._loading,
                "detections": self._last_dets[:15],
            }


def _class_color(cls_id: int):
    colors = [(0,255,0),(255,128,0),(0,128,255),(255,0,128),(128,255,0),
              (0,255,128),(255,255,0),(0,0,255),(255,0,0),(128,0,255)]
    return colors[cls_id % len(colors)]


infer_engine = InferenceEngine()


# ---------------------------------------------------------------------------
# Training State
# ---------------------------------------------------------------------------
training_state: Dict[str, Any] = {
    "status": "idle",   # idle | running | done | error
    "epoch": 0,
    "total_epochs": 0,
    "train_loss": 0.0,
    "val_mAP": 0.0,
    "log": "",
    "model_path": None,
    "job_id": None,
    "server_url": "",
}
training_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _read_classes() -> List[str]:
    try:
        with open(CLASSES_FILE) as f:
            return [ln.strip() for ln in f if ln.strip()]
    except Exception:
        return DEFAULT_CLASSES


def _write_classes(classes: List[str]):
    with open(CLASSES_FILE, "w") as f:
        f.write("\n".join(classes))


def _image_path(image_id: str) -> str:
    return os.path.join(IMAGES_DIR, f"{image_id}.jpg")


def _label_path(image_id: str) -> str:
    return os.path.join(LABELS_DIR, f"{image_id}.txt")


def _list_images() -> List[Dict]:
    images = []
    for p in sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")), reverse=True):
        img_id = os.path.splitext(os.path.basename(p))[0]
        has_label = os.path.exists(_label_path(img_id))
        images.append({
            "id": img_id,
            "filename": os.path.basename(p),
            "size": os.path.getsize(p),
            "annotated": has_label,
            "created": os.path.getmtime(p),
        })
    return images


def _read_admin_pin() -> str:
    try:
        with open(ADMIN_PIN_FILE) as f:
            return f.read().strip()
    except Exception:
        return "1234"


# ---------------------------------------------------------------------------
# Async generators for MJPEG streams
# ---------------------------------------------------------------------------
async def _raw_stream_gen():
    interval = 1.0 / TARGET_FPS
    while True:
        jpeg = stream_engine.get_latest_jpeg()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
        await asyncio.sleep(interval)


async def _infer_stream_gen():
    """MJPEG stream with YOLO inference overlay."""
    while True:
        frame = stream_engine.get_latest_frame()
        if frame is not None:
            annotated, _ = infer_engine.infer(frame)
            _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            jpeg = buf.tobytes()
        else:
            jpeg = stream_engine.get_latest_jpeg()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
        await asyncio.sleep(0.1)   # ~10 FPS for inference stream (CPU limited)


# ===========================================================================
# ROUTES
# ===========================================================================

# --- Raw camera stream -------------------------------------------------------
@app.get("/api/stream")
@app.head("/api/stream")
async def video_feed():
    return StreamingResponse(_raw_stream_gen(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


# --- Focus score -------------------------------------------------------------
@app.get("/api/focus-score")
def focus_score():
    frame = stream_engine.get_latest_frame()
    if frame is None or not stream_engine.get_status():
        return JSONResponse({"score": 0, "raw_variance": 0.0,
                             "label": "no_camera", "label_de": "Keine Kamera", "color": "#6b7280"})
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    rw, rh = int(w * 0.4), int(h * 0.4)
    roi = frame[cy - rh//2:cy + rh//2, cx - rw//2:cx + rw//2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < 50:    score = int(lap_var / 50 * 20)
    elif lap_var < 200: score = 20 + int((lap_var - 50) / 150 * 30)
    elif lap_var < 800: score = 50 + int((lap_var - 200) / 600 * 30)
    elif lap_var < 2000:score = 80 + int((lap_var - 800) / 1200 * 15)
    else:               score = min(100, 95 + int((lap_var - 2000) / 1000 * 5))
    if score < 30:   label, label_de, color = "blurry", "Unscharf",    "#ef4444"
    elif score < 60: label, label_de, color = "ok",     "Mittelmäßig", "#f59e0b"
    elif score < 85: label, label_de, color = "good",   "Gut",         "#84cc16"
    else:            label, label_de, color = "sharp",  "Scharf ✓",    "#22c55e"
    return JSONResponse({"score": score, "raw_variance": round(lap_var, 1),
                         "label": label, "label_de": label_de, "color": color})


# --- YOLO inference stream & config ------------------------------------------
@app.get("/api/infer-stream")
async def infer_stream():
    return StreamingResponse(_infer_stream_gen(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


class InferConfig(BaseModel):
    model: Optional[str] = None
    confidence: Optional[float] = None
    show_boxes: Optional[bool] = None


@app.post("/api/infer-config")
def set_infer_config(cfg: InferConfig):
    infer_engine.set_config(cfg.model, cfg.confidence, cfg.show_boxes)
    return JSONResponse({"ok": True})


@app.get("/api/infer-stats")
def get_infer_stats():
    return JSONResponse(infer_engine.get_stats())


@app.get("/api/models")
def list_models():
    custom = [os.path.splitext(f)[0]
              for f in os.listdir(MODELS_DIR) if f.endswith(".pt")]
    return JSONResponse({"builtin": BUILTIN_MODELS, "custom": custom,
                         "current": infer_engine.model_name})


@app.post("/api/models/upload")
async def upload_model(file: UploadFile = File(...)):
    if not file.filename.endswith(".pt"):
        raise HTTPException(400, "Only .pt model files accepted")
    dest = os.path.join(MODELS_DIR, file.filename)
    with open(dest, "wb") as f:
        f.write(await file.read())
    return JSONResponse({"ok": True, "name": os.path.splitext(file.filename)[0]})


# --- Image capture & management ----------------------------------------------
@app.post("/api/capture")
def capture_image():
    frame = stream_engine.get_latest_frame()
    if frame is None:
        raise HTTPException(503, "Camera not available")
    img_id = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:4]
    path = _image_path(img_id)
    cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return JSONResponse({"id": img_id, "filename": os.path.basename(path)})


@app.get("/api/images")
def list_images_route():
    return JSONResponse({"images": _list_images(), "total": len(_list_images())})


@app.get("/api/images/{image_id}")
def get_image(image_id: str):
    path = _image_path(image_id)
    if not os.path.exists(path):
        raise HTTPException(404, "Image not found")
    return FileResponse(path, media_type="image/jpeg")


@app.delete("/api/images/{image_id}")
def delete_image(image_id: str):
    for p in [_image_path(image_id), _label_path(image_id)]:
        if os.path.exists(p):
            os.remove(p)
    return JSONResponse({"ok": True})


# --- Annotations & Labels ----------------------------------------------------
@app.get("/api/labels")
def get_labels():
    return JSONResponse({"classes": _read_classes()})


class LabelsBody(BaseModel):
    classes: List[str]


@app.post("/api/labels")
def save_labels_route(body: LabelsBody):
    _write_classes(body.classes)
    return JSONResponse({"ok": True})


@app.get("/api/annotations/{image_id}")
def get_annotations(image_id: str):
    path = _label_path(image_id)
    if not os.path.exists(path):
        return JSONResponse({"annotations": []})
    annotations = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                annotations.append({
                    "class_id": int(parts[0]),
                    "cx": float(parts[1]),
                    "cy": float(parts[2]),
                    "w": float(parts[3]),
                    "h": float(parts[4]),
                })
    return JSONResponse({"annotations": annotations})


class AnnotationBox(BaseModel):
    class_id: int
    cx: float
    cy: float
    w: float
    h: float


class AnnotationsBody(BaseModel):
    annotations: List[AnnotationBox]


@app.post("/api/annotations/{image_id}")
def save_annotations(image_id: str, body: AnnotationsBody):
    path = _label_path(image_id)
    with open(path, "w") as f:
        for box in body.annotations:
            f.write(f"{box.class_id} {box.cx:.6f} {box.cy:.6f} {box.w:.6f} {box.h:.6f}\n")
    return JSONResponse({"ok": True})


@app.post("/api/assisted-label/{image_id}")
def assisted_label(image_id: str):
    """Run YOLO inference on a saved image and return suggested bounding boxes."""
    img_path = _image_path(image_id)
    if not os.path.exists(img_path):
        raise HTTPException(404, "Image not found")
    with infer_engine._lock:
        model = infer_engine._model
        conf = infer_engine.conf
    if model is None:
        raise HTTPException(503, "YOLO model not loaded yet")
    frame = cv2.imread(img_path)
    h, w = frame.shape[:2]
    results = model.predict(frame, conf=conf, verbose=False)
    boxes = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes.append({
                "class_id": int(box.cls[0]),
                "cx": round(((x1 + x2) / 2) / w, 6),
                "cy": round(((y1 + y2) / 2) / h, 6),
                "w": round((x2 - x1) / w, 6),
                "h": round((y2 - y1) / h, 6),
                "confidence": round(float(box.conf[0]), 3),
            })
    return JSONResponse({"annotations": boxes, "model": infer_engine.model_name})


@app.get("/api/annotation-stats")
def annotation_stats():
    images = _list_images()
    annotated = sum(1 for img in images if img["annotated"])
    return JSONResponse({"total": len(images), "annotated": annotated,
                         "pending": len(images) - annotated})


# --- Training ----------------------------------------------------------------
class TrainingConfig(BaseModel):
    server_url: str = ""
    model: str = "yolo11n"
    epochs: int = 50
    batch: int = 8
    lr: float = 0.001
    local: bool = False   # run locally on Jetson (slow)


def _build_dataset_yaml() -> str:
    """Generate a YOLO dataset.yaml from current images/labels."""
    classes = _read_classes()
    yaml_path = os.path.join(WORKSPACE_DIR, "dataset.yaml")
    content = (
        f"path: {WORKSPACE_DIR}\n"
        f"train: images\n"
        f"val: images\n"
        f"nc: {len(classes)}\n"
        f"names: {classes}\n"
    )
    with open(yaml_path, "w") as f:
        f.write(content)
    return yaml_path


def _local_training_thread(cfg: TrainingConfig):
    global training_state
    try:
        yaml_path = _build_dataset_yaml()
        from ultralytics import YOLO  # type: ignore
        model = YOLO(f"{cfg.model}.pt")
        with training_lock:
            training_state["status"] = "running"
            training_state["total_epochs"] = cfg.epochs
            training_state["log"] = "Local training started on Jetson...\n"

        def on_epoch_end(trainer):
            with training_lock:
                training_state["epoch"] = trainer.epoch + 1
                training_state["train_loss"] = round(float(trainer.loss), 4)
                training_state["log"] += f"Epoch {trainer.epoch+1}/{cfg.epochs} loss={trainer.loss:.4f}\n"

        model.add_callback("on_train_epoch_end", on_epoch_end)
        results = model.train(data=yaml_path, epochs=cfg.epochs,
                              batch=cfg.batch, lr0=cfg.lr, device="cpu",
                              project=EXPORTS_DIR, name="training")
        best_pt = os.path.join(EXPORTS_DIR, "training", "weights", "best.pt")
        with training_lock:
            training_state["status"] = "done"
            training_state["model_path"] = best_pt if os.path.exists(best_pt) else None
            training_state["log"] += "Training complete!\n"
    except Exception as e:
        with training_lock:
            training_state["status"] = "error"
            training_state["log"] += f"Error: {e}\n"


def _remote_training_thread(cfg: TrainingConfig):
    import urllib.request, urllib.error
    global training_state
    try:
        # Package dataset as zip
        zip_path = os.path.join(EXPORTS_DIR, "dataset.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for img_f in glob.glob(os.path.join(IMAGES_DIR, "*.jpg")):
                zf.write(img_f, os.path.join("images", os.path.basename(img_f)))
            for lbl_f in glob.glob(os.path.join(LABELS_DIR, "*.txt")):
                zf.write(lbl_f, os.path.join("labels", os.path.basename(lbl_f)))
            classes_f = CLASSES_FILE
            if os.path.exists(classes_f):
                zf.write(classes_f, "classes.txt")

        with training_lock:
            training_state["status"] = "running"
            training_state["log"] = f"Uploading dataset to {cfg.server_url}...\n"

        # Upload dataset zip
        with open(zip_path, "rb") as f:
            dataset_bytes = f.read()

        import urllib.request
        req = urllib.request.Request(
            f"{cfg.server_url.rstrip('/')}/api/train",
            data=json.dumps({
                "model": cfg.model, "epochs": cfg.epochs,
                "batch": cfg.batch, "lr": cfg.lr,
                "dataset": dataset_bytes.hex()[:100] + "..."  # placeholder
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            job_id = result.get("job_id", "unknown")

        with training_lock:
            training_state["job_id"] = job_id
            training_state["log"] += f"Job started: {job_id}\n"

        # Poll status
        while True:
            time.sleep(5)
            try:
                with urllib.request.urlopen(
                        f"{cfg.server_url.rstrip('/')}/api/train/{job_id}/status",
                        timeout=10) as resp:
                    status = json.loads(resp.read())
                    with training_lock:
                        training_state.update({
                            "epoch": status.get("epoch", 0),
                            "total_epochs": status.get("total_epochs", cfg.epochs),
                            "train_loss": status.get("train_loss", 0),
                            "val_mAP": status.get("val_mAP", 0),
                            "log": training_state["log"] + status.get("last_log", ""),
                        })
                    if status.get("status") in ("done", "error"):
                        with training_lock:
                            training_state["status"] = status["status"]
                        break
            except Exception as e:
                with training_lock:
                    training_state["log"] += f"Poll error: {e}\n"
                break

    except Exception as e:
        with training_lock:
            training_state["status"] = "error"
            training_state["log"] += f"Training error: {e}\n"


@app.post("/api/training/start")
def start_training(cfg: TrainingConfig):
    with training_lock:
        if training_state["status"] == "running":
            return JSONResponse({"error": "Training already running"}, status_code=409)
        training_state.update({"status": "idle", "epoch": 0, "log": "",
                               "val_mAP": 0, "train_loss": 0, "model_path": None})
        training_state["server_url"] = cfg.server_url

    if cfg.local or not cfg.server_url:
        threading.Thread(target=_local_training_thread, args=(cfg,), daemon=True).start()
    else:
        threading.Thread(target=_remote_training_thread, args=(cfg,), daemon=True).start()
    return JSONResponse({"ok": True, "mode": "local" if cfg.local else "remote"})


@app.get("/api/training/status")
def get_training_status():
    with training_lock:
        return JSONResponse(dict(training_state))


@app.post("/api/training/stop")
def stop_training():
    with training_lock:
        training_state["status"] = "idle"
        training_state["log"] += "\nStopped by user.\n"
    return JSONResponse({"ok": True})


# --- Evaluation & Report -----------------------------------------------------
@app.post("/api/evaluation/run")
def run_evaluation():
    """Simple evaluation: run model on all labeled images and compute stats."""
    with infer_engine._lock:
        model = infer_engine._model
    if model is None:
        raise HTTPException(503, "YOLO model not loaded")
    images = _list_images()
    labeled = [img for img in images if img["annotated"]]
    if not labeled:
        return JSONResponse({"error": "No annotated images for evaluation"})
    # Quick pass – count TP/FP/FN per class
    tp, fp, fn = 0, 0, 0
    for img in labeled[:50]:   # max 50 images
        frame = cv2.imread(_image_path(img["id"]))
        if frame is None:
            continue
        results = model.predict(frame, conf=infer_engine.conf, verbose=False)
        preds = len(results[0].boxes) if results else 0
        with open(_label_path(img["id"])) as f:
            gt = len([l for l in f if l.strip()])
        # Simplified: approximate TP as min(pred, gt)
        t = min(preds, gt)
        tp += t
        fp += max(0, preds - gt)
        fn += max(0, gt - preds)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return JSONResponse({
        "images_evaluated": len(labeled),
        "precision": round(precision, 3),
        "recall":    round(recall, 3),
        "f1":        round(f1, 3),
        "mAP50_approx": round((precision + recall) / 2, 3),
        "model": infer_engine.model_name,
    })


@app.post("/api/report/generate")
def generate_report():
    """Generate a PDF lab report with reportlab."""
    try:
        from reportlab.pdfgen import canvas as pdfcanvas  # type: ignore
        from reportlab.lib.pagesizes import A4
        report_path = os.path.join(EXPORTS_DIR, "Praktikum_Bericht.pdf")
        c = pdfcanvas.Canvas(report_path, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 20)
        c.drawString(60, h - 80, "HFU AI-LAB – Praktikumsprotokoll")
        c.setFont("Helvetica", 12)
        c.drawString(60, h - 110, f"Erstellt: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        images = _list_images()
        annotated = sum(1 for img in images if img["annotated"])
        c.drawString(60, h - 150, f"Bilder erfasst: {len(images)}")
        c.drawString(60, h - 170, f"Bilder annotiert: {annotated}")
        c.drawString(60, h - 190, f"Klassen: {', '.join(_read_classes())}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, h - 240, "Trainingsstatus")
        c.setFont("Helvetica", 12)
        with training_lock:
            ts = training_state
        c.drawString(60, h - 260, f"Status: {ts['status']}")
        c.drawString(60, h - 278, f"Modell: {infer_engine.model_name}")
        c.drawString(60, h - 296, f"Epochen: {ts['epoch']} / {ts['total_epochs']}")
        c.drawString(60, h - 314, f"Val mAP: {ts['val_mAP']}")
        c.save()
        return FileResponse(report_path, media_type="application/pdf",
                            filename="Praktikum_Bericht.pdf")
    except Exception as e:
        raise HTTPException(500, f"PDF generation failed: {e}")


@app.get("/api/export/zip")
def export_zip():
    """Export all student data as ZIP."""
    zip_path = os.path.join(EXPORTS_DIR, "export_all.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(WORKSPACE_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, WORKSPACE_DIR)
                zf.write(abs_path, rel_path)
    return FileResponse(zip_path, media_type="application/zip",
                        filename="HFU_AI_LAB_Export.zip")


# --- Status ------------------------------------------------------------------
@app.get("/api/status")
def system_status():
    cam_online = stream_engine.get_status()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(WORKSPACE_DIR)
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
        "camera": {"online": cam_online, "device": CAM_PATH,
                   "mode": f"UGREEN UVC ({CAM_PATH})" if cam_online else "Siemens Star"},
        "wlan":   {"ssid": ssid, "ip": "192.168.4.1", "active": True},
        "docker": {"frontend": "running", "backend": "running", "jupyter": "running"},
        "system": {
            "cpu_percent":   psutil.cpu_percent(interval=None),
            "ram_used_gb":   round(mem.used  / 1024**3, 2),
            "ram_total_gb":  round(mem.total / 1024**3, 2),
            "ram_percent":   mem.percent,
            "disk_used_gb":  round(disk.used  / 1024**3, 2),
            "disk_total_gb": round(disk.total / 1024**3, 2),
            "disk_percent":  disk.percent,
        },
    })


# --- Admin -------------------------------------------------------------------
class PinBody(BaseModel):
    pin: str


@app.post("/api/admin/verify-pin")
def verify_pin(body: PinBody):
    correct = _read_admin_pin()
    return JSONResponse({"ok": body.pin == correct})


class ChangePinBody(BaseModel):
    old_pin: str
    new_pin: str


@app.post("/api/admin/change-pin")
def change_pin(body: ChangePinBody):
    if body.old_pin != _read_admin_pin():
        raise HTTPException(403, "Wrong PIN")
    with open(ADMIN_PIN_FILE, "w") as f:
        f.write(body.new_pin)
    return JSONResponse({"ok": True})


@app.post("/api/admin/update")
def system_update():
    try:
        result = subprocess.run(
            ["bash", "-c", "cd /app && git pull origin main 2>&1"],
            capture_output=True, text=True, timeout=60
        )
        return JSONResponse({"ok": True, "output": result.stdout + result.stderr})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/admin/network")
def get_network():
    """Read current network configuration files."""
    info: Dict[str, Any] = {"mode": "unknown", "ap_ssid": "", "station_ssid": ""}
    try:
        ap_conf = "/etc/hostapd/hostapd.conf"
        if os.path.exists(ap_conf):
            with open(ap_conf) as f:
                for line in f:
                    if line.startswith("ssid="):
                        info["ap_ssid"] = line.split("=", 1)[1].strip()
            info["mode"] = "ap"
    except Exception:
        pass
    try:
        wpa = "/etc/wpa_supplicant/wpa_supplicant.conf"
        if os.path.exists(wpa):
            with open(wpa) as f:
                content = f.read()
                import re
                m = re.search(r'ssid="([^"]+)"', content)
                if m:
                    info["station_ssid"] = m.group(1)
    except Exception:
        pass
    return JSONResponse(info)


class NetworkBody(BaseModel):
    mode: str           # "ap" | "station"
    ssid: str = ""
    password: str = ""


@app.post("/api/admin/network")
def set_network(body: NetworkBody):
    """Write network config – requires restart to take effect."""
    try:
        if body.mode == "ap" and body.ssid:
            conf_path = "/etc/hostapd/hostapd.conf"
            if os.path.exists(conf_path):
                with open(conf_path) as f:
                    content = f.read()
                import re
                content = re.sub(r"ssid=.*", f"ssid={body.ssid}", content)
                if body.password:
                    content = re.sub(r"wpa_passphrase=.*", f"wpa_passphrase={body.password}", content)
                with open(conf_path, "w") as f:
                    f.write(content)
        elif body.mode == "station" and body.ssid:
            entry = (f'\nnetwork={{\n    ssid="{body.ssid}"\n'
                     f'    psk="{body.password}"\n    key_mgmt=WPA-PSK\n}}\n')
            wpa = "/etc/wpa_supplicant/wpa_supplicant.conf"
            with open(wpa, "a") as f:
                f.write(entry)
        return JSONResponse({"ok": True, "note": "Reboot required to apply network changes"})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# --- Legacy endpoints --------------------------------------------------------
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
