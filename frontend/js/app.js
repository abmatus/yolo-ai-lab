/* ==============================================================================
   HFU AI-LAB: Frontend Application JavaScript
   ============================================================================== */

const i18n = {
  de: {
    stationTitle: "HFU KI-Praktikumsstation",
    subtitle: "Autarke Objekterkennung mit YOLOv11 & NVIDIA Jetson Orin Nano",
    tabDashboard: "Dashboard",
    camStatus: "Kamera",
    wlanStatus: "WLAN AP",
    dockerStatus: "System",
    welcomeTitle: "Willkommen zum Objekterkennungs-Praktikum",
    welcomeText: "Diese autarke KI-Workstation ermöglicht das vollständige Training und die Evaluierung eines modernen YOLOv11 Neuronalen Netzes direkt auf der NVIDIA Jetson Orin Nano GPU.",
    stepsTitle: "Praktikumsablauf",
    step1: "1. Fokus",
    dashStep1: "1. Kamera & Fokus",
    dashStep1Desc: "Siemensstern fokussieren und Messwerte prüfen.",
    step2: "2. COCO Live",
    dashStep2: "2. COCO Exploration",
    dashStep2Desc: "Inferenz mit vortrainierten Modellen testen.",
    step3: "3. Aufnahme",
    dashStep3: "3. Bilder aufnehmen",
    dashStep3Desc: "Datensatz vom gewünschten Bauteil erstellen.",
    step4: "4. Labeling",
    dashStep4: "4. Labeling",
    dashStep4Desc: "Bilder annotieren und Klassen zuweisen.",
    step5: "5. Training",
    dashStep5: "5. KI Training",
    dashStep5Desc: "Transfer-Learning des YOLO-Modells starten.",
    step6: "6. Evaluation",
    dashStep6: "6. Evaluation",
    dashStep6Desc: "mAP Metriken berechnen & Protokoll erstellen.",
    focusTitle: "Live-Kamerabild & Fokus-Messung (Siemensstern)",
    focusDesc: "Stellen Sie den manuellen Fokusring ein, bis die Linien scharf sind.",
    focusMeasArea: "Messbereich",
    focusVarRow: "Laplace-Varianz",
    zoneBlurry: "Unscharf",
    zoneOk: "Mittel",
    zoneGood: "Gut",
    zoneSharp: "Scharf",
    btnPrev: "⬅ Zurück",
    btnNext: "Weiter ➡",
    cocoTitle: "Live YOLO Inferenz (COCO Exploration)",
    cocoSelectModel: "Modell auswählen",
    cocoUploadModel: "Eigenes Modell hochladen (.pt)",
    cocoShowBoxes: "Bounding Boxes anzeigen",
    cocoLiveStats: "Live Statistik",
    captureTitle: "Bilderfassung",
    captureBtn: "Bild aufnehmen",
    captureGallery: "Galerie",
    labelingTitle: "Assisted Labeling",
    labelingImages: "Bilder",
    labelingBatchBtn: "🤖 Batch Assisted Labeling",
    labelingClasses: "Klassen",
    labelingBoxes: "Boxes (Aktuelles Bild)",
    trainingTitle: "KI Training",
    trainServer: "Trainingsserver URL (leer für Jetson lokal)",
    trainEpochs: "Epochen",
    trainModel: "Start-Modell",
    trainStart: "▶ Training starten",
    trainStop: "⏹ Stoppen",
    trainEpoch: "Epoche:",
    evalTitle: "Evaluation & Protokoll",
    evalRun: "📊 Evaluation ausführen",
    evalHint: "Klicken Sie auf Ausführen, um das aktuelle Modell gegen alle annotierten Bilder zu testen.",
    evalPdf: "📄 PDF Protokoll",
    evalZip: "📦 ZIP Export",
    batchLabelTitle: "Batch Assisted Labeling",
    batchLabelDesc: "Wählt ungelabelte Bilder aus und verwendet das YOLO Modell, um automatisch Bounding Boxes vorzuschlagen.",
    batchLabelModel: "Modell für Labeling:"
  },
  en: {
    stationTitle: "HFU AI Lab Workstation",
    subtitle: "Autonomous Object Detection with YOLOv11 & NVIDIA Jetson Orin Nano",
    tabDashboard: "Dashboard",
    camStatus: "Camera",
    wlanStatus: "WLAN AP",
    dockerStatus: "System",
    welcomeTitle: "Welcome to the Object Detection Lab",
    welcomeText: "This autonomous AI workstation enables end-to-end training and evaluation of a modern YOLOv11 Neural Network.",
    stepsTitle: "Lab Workflow",
    step1: "1. Focus",
    dashStep1: "1. Camera & Focus",
    dashStep1Desc: "Focus Siemens star and check metrics.",
    step2: "2. COCO Live",
    dashStep2: "2. COCO Exploration",
    dashStep2Desc: "Test inference with pre-trained models.",
    step3: "3. Capture",
    dashStep3: "3. Capture Images",
    dashStep3Desc: "Create dataset of your component.",
    step4: "4. Labeling",
    dashStep4: "4. Labeling",
    dashStep4Desc: "Annotate images and assign classes.",
    step5: "5. Training",
    dashStep5: "5. AI Training",
    dashStep5Desc: "Start YOLO transfer learning.",
    step6: "6. Evaluation",
    dashStep6: "6. Evaluation",
    dashStep6Desc: "Calculate mAP metrics & create report.",
    focusTitle: "Live Camera View & Focus Measurement",
    focusDesc: "Adjust the manual focus ring until the lines are sharp.",
    focusMeasArea: "Measurement Zone",
    focusVarRow: "Laplacian Variance",
    zoneBlurry: "Blurry",
    zoneOk: "Moderate",
    zoneGood: "Good",
    zoneSharp: "Sharp",
    btnPrev: "⬅ Back",
    btnNext: "Next ➡",
    cocoTitle: "Live YOLO Inference (COCO Exploration)",
    cocoSelectModel: "Select Model",
    cocoUploadModel: "Upload Custom Model (.pt)",
    cocoShowBoxes: "Show Bounding Boxes",
    cocoLiveStats: "Live Statistics",
    captureTitle: "Image Capture",
    captureBtn: "Capture Image",
    captureGallery: "Gallery",
    labelingTitle: "Assisted Labeling",
    labelingImages: "Images",
    labelingBatchBtn: "🤖 Batch Assisted Labeling",
    labelingClasses: "Classes",
    labelingBoxes: "Boxes (Current Image)",
    trainingTitle: "AI Training",
    trainServer: "Training Server URL (empty for local)",
    trainEpochs: "Epochs",
    trainModel: "Start Model",
    trainStart: "▶ Start Training",
    trainStop: "⏹ Stop",
    trainEpoch: "Epoch:",
    evalTitle: "Evaluation & Report",
    evalRun: "📊 Run Evaluation",
    evalHint: "Click run to test the current model against all annotated images.",
    evalPdf: "📄 PDF Report",
    evalZip: "📦 ZIP Export",
    batchLabelTitle: "Batch Assisted Labeling",
    batchLabelDesc: "Selects unlabeled images and uses the YOLO model to automatically propose bounding boxes.",
    batchLabelModel: "Model for Labeling:"
  }
};

let currentLang = "de";
let focusInterval = null;
let trainInterval = null;
let isAdmin = false;

// Chart.js instance for Inference
let inferChart = null;
let inferTimeData = [];
let inferFpsData = [];
let inferLabels = [];

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  initDynamicLinks();
  startStatusPolling();
  initChart();
  
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.getAttribute("data-tab")));
  });

  fetchModels();
  fetchGallery();
  fetchClasses();
});

function initDynamicLinks() {
  const host = window.location.hostname || "localhost";
  const jupyterBtn = document.getElementById("btn-jupyter-link");
  if (jupyterBtn) jupyterBtn.href = `http://${host}:8888`;

  const streamUrl = `http://${host}:8000/api/stream`;
  const inferUrl = `http://${host}:8000/api/infer-stream`;
  
  const imgMain = document.getElementById("cam-stream-main");
  const imgCapture = document.getElementById("cam-stream-capture");
  const imgInfer = document.getElementById("cam-stream-infer");
  
  if (imgMain) imgMain.src = streamUrl;
  if (imgCapture) imgCapture.src = streamUrl;
  if (imgInfer) imgInfer.src = inferUrl;
}

function initTheme() {
  const themeBtn = document.getElementById("theme-toggle");
  const savedTheme = localStorage.getItem("hfu_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  themeBtn.textContent = savedTheme === "dark" ? "☀️ Light" : "🌙 Dark";
  
  themeBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("hfu_theme", next);
    themeBtn.textContent = next === "dark" ? "☀️ Light" : "🌙 Dark";
  });
}

function initLanguage() {
  const langBtn = document.getElementById("lang-toggle");
  langBtn.addEventListener("click", () => {
    currentLang = currentLang === "de" ? "en" : "de";
    langBtn.textContent = currentLang.toUpperCase();
    applyLanguage();
  });
  applyLanguage();
}

function applyLanguage() {
  const dict = i18n[currentLang];
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      if (el.tagName === "INPUT" && el.hasAttribute("placeholder")) {
        el.placeholder = dict[key];
      } else {
        el.textContent = dict[key];
      }
    }
  });
}

function switchTab(target) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
  
  const btn = document.querySelector(`.tab-btn[data-tab="${target}"]`);
  if(btn) btn.classList.add("active");
  const tab = document.getElementById(`tab-${target}`);
  if(tab) tab.classList.add("active");

  if (target === "kiosk") startFocusPolling(); else stopFocusPolling();
  if (target === "coco") startInferPolling(); else stopInferPolling();
  if (target === "capture") fetchGallery();
  if (target === "labeling") { fetchGalleryForLabeling(); fetchClasses(); }
  if (target === "training") startTrainPolling(); else stopTrainPolling();
  
  window.scrollTo(0,0);
}

function startStatusPolling() {
  setInterval(async () => {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        updateDot("dot-cam", data.camera.online);
        updateDot("dot-wlan", data.wlan.active);
        updateDot("dot-docker", data.status === "online");
        const ssidEl = document.getElementById("ssid-display");
        if(ssidEl) ssidEl.textContent = data.wlan.ssid;
      }
    } catch (e) {
      updateDot("dot-cam", false);
      updateDot("dot-wlan", false);
      updateDot("dot-docker", false);
    }
  }, 3000);
}

function updateDot(id, isOnline) {
  const dot = document.getElementById(id);
  if (dot) dot.classList.toggle("online", isOnline);
}

// ------------------------------------------------------------------
// Tab 2: Focus
async function fetchFocusScore() {
  try {
    const res  = await fetch("/api/focus-score");
    if (!res.ok) return;
    const d = await res.json();

    const scoreEl = document.getElementById("focus-score-num");
    const gaugeEl = document.getElementById("focus-gauge-fill");
    const badgeEl = document.getElementById("focus-label-badge");
    const rawEl   = document.getElementById("focus-raw-var");

    if (scoreEl) { scoreEl.textContent = d.score; scoreEl.style.color = d.color; }
    if (gaugeEl) gaugeEl.style.width = d.score + "%";
    if (badgeEl) {
      badgeEl.textContent = currentLang === 'de' ? d.label_de : d.label;
      badgeEl.style.background = d.color + "22";
      badgeEl.style.color      = d.color;
    }
    if (rawEl) rawEl.textContent = d.raw_variance.toFixed(1);
  } catch (e) {}
}

function startFocusPolling() { if (!focusInterval) focusInterval = setInterval(fetchFocusScore, 500); }
function stopFocusPolling() { if (focusInterval) { clearInterval(focusInterval); focusInterval = null; } }


// ------------------------------------------------------------------
// Tab 3: COCO Live Inference
function initChart() {
  const ctx = document.getElementById('inferChart');
  if(!ctx) return;
  inferChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: inferLabels,
      datasets: [
        { label: 'Infer ms', data: inferTimeData, borderColor: '#ef4444', borderWidth: 2, yAxisID: 'y' },
        { label: 'FPS', data: inferFpsData, borderColor: '#3b82f6', borderWidth: 2, yAxisID: 'y1' }
      ]
    },
    options: {
      responsive: true,
      animation: false,
      scales: {
        x: { display: false },
        y: { type: 'linear', display: true, position: 'left', min: 0 },
        y1: { type: 'linear', display: true, position: 'right', min: 0, grid: {drawOnChartArea: false} }
      },
      plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 10, font: {size: 10} } } }
    }
  });
}

let inferInterval = null;
async function fetchModels() {
  const res = await fetch("/api/models");
  const data = await res.json();
  const sel = document.getElementById("coco-model-select");
  const selBatch = document.getElementById("batch-model-select");
  
  if(sel) sel.innerHTML = "";
  if(selBatch) selBatch.innerHTML = "";
  
  data.builtin.forEach(m => {
    sel?.add(new Option(m, m));
    selBatch?.add(new Option(m, m));
  });
  data.custom.forEach(m => {
    sel?.add(new Option("Custom: " + m, m));
    selBatch?.add(new Option("Custom: " + m, m));
  });
  
  if(sel) sel.value = data.current;
}

async function uploadModel(inputElement, isBatch=false) {
  if(!inputElement.files.length) return;
  const file = inputElement.files[0];
  const formData = new FormData();
  formData.append("file", file);
  
  alert("Upload startet...");
  const res = await fetch("/api/models/upload", { method: "POST", body: formData });
  if(res.ok) {
    await fetchModels();
    const data = await res.json();
    if(isBatch) {
      document.getElementById("batch-model-select").value = data.name;
    } else {
      document.getElementById("coco-model-select").value = data.name;
      updateInferConfig();
    }
    alert("Upload erfolgreich!");
  } else {
    alert("Upload Fehler.");
  }
}

async function updateInferConfig() {
  const m = document.getElementById("coco-model-select").value;
  const c = document.getElementById("coco-conf").value;
  const s = document.getElementById("coco-show-boxes").checked;
  document.getElementById("conf-val").textContent = c;
  await fetch("/api/infer-config", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({model: m, confidence: parseFloat(c), show_boxes: s})
  });
}

function startInferPolling() {
  if(!inferInterval) inferInterval = setInterval(async () => {
    const res = await fetch("/api/infer-stats");
    const d = await res.json();
    
    document.getElementById("infer-fps").textContent = d.fps;
    document.getElementById("infer-ms").textContent = d.infer_ms;
    
    // Update Chart
    const maxPoints = 20;
    if(inferLabels.length >= maxPoints) { inferLabels.shift(); inferTimeData.shift(); inferFpsData.shift(); }
    inferLabels.push('');
    inferTimeData.push(d.infer_ms);
    inferFpsData.push(d.fps);
    if(inferChart) inferChart.update();

  }, 1000);
}
function stopInferPolling() { if(inferInterval) { clearInterval(inferInterval); inferInterval=null; } }


// ------------------------------------------------------------------
// Tab 4: Capture
let currentGalleryList = [];
let currentLightboxIndex = -1;

async function captureImage() {
  const res = await fetch("/api/capture", {method:"POST"});
  if (res.ok) fetchGallery();
}

async function fetchGallery() {
  const res = await fetch("/api/images");
  const data = await res.json();
  currentGalleryList = data.images;
  document.getElementById("gallery-count").textContent = data.total;
  const grid = document.getElementById("gallery-grid");
  if(!grid) return;
  grid.innerHTML = data.images.map((img, idx) => `
    <div class="gallery-item" onclick="openLightbox(${idx})">
      <img src="/api/images/${img.id}" loading="lazy">
      ${img.annotated ? '<span class="badge-success" style="position:absolute; bottom:5px; left:5px; background:rgba(34,197,94,0.9); padding:2px 6px; border-radius:4px; font-size:12px;">Labeled</span>' : ''}
      <button class="btn-del-gallery" onclick="event.stopPropagation(); deleteSpecificImage('${img.id}')">❌</button>
    </div>
  `).join("");
}

function openLightbox(idx) {
  if(idx < 0 || idx >= currentGalleryList.length) return;
  currentLightboxIndex = idx;
  const id = currentGalleryList[idx].id;
  document.getElementById("lightbox-img").src = `/api/images/${id}`;
  document.getElementById("lightbox-modal").style.display = "flex";
}

function navLightbox(direction) {
  openLightbox(currentLightboxIndex + direction);
}

async function deleteCurrentImage() {
  if(currentLightboxIndex === -1) return;
  const id = currentGalleryList[currentLightboxIndex].id;
  await fetch(`/api/images/${id}`, {method:"DELETE"});
  document.getElementById("lightbox-modal").style.display = "none";
  fetchGallery();
  fetchGalleryForLabeling();
}

async function deleteSpecificImage(id) {
  await fetch(`/api/images/${id}`, {method:"DELETE"});
  fetchGallery();
  fetchGalleryForLabeling();
}

function showInfo(tabId) {
  const titles = {
    kiosk: "Info: Hardware & Fokus",
    coco: "Info: COCO Exploration",
    capture: "Info: Bilderfassung",
    labeling: "Info: Labeling",
    training: "Info: KI Training",
    eval: "Info: Evaluation"
  };
  const texts = {
    kiosk: "<p>Hier richten wir die Kamera optimal ein. Der <strong>Siemensstern</strong> wird verwendet, um den Fokus manuell über den Objektiv-Ring einzustellen. Die <em>Laplace-Varianz</em> berechnet den Kantenkontrast – je höher der Wert, desto schärfer das Bild. Ein Wert > 85 gilt als scharf.</p>",
    coco: "<p>Dies ist ein Sandkasten-Modus, um die Fähigkeiten eines vortrainierten YOLO-Modells zu testen. <strong>YOLO (You Only Look Once)</strong> erkennt Objekte in Echtzeit (Live-Inferenz). Verstelle die <em>Confidence</em> (Schwellenwert), um zu sehen, ab wann die KI unsicher wird. Das Modell kennt 80 Standard-Klassen aus dem COCO-Datensatz (z.B. Person, Auto, Tasse).</p>",
    capture: "<p>Wir beginnen nun mit dem Aufbau eines eigenen Datensatzes. Positioniere das gewünschte Bauteil in verschiedenen Winkeln und Lichtverhältnissen und nimm Bilder auf. Für ein robustes Modell werden mind. 30-50 Bilder empfohlen.</p>",
    labeling: "<p>Jedes Bild muss annotiert (gelabelt) werden. Die KI muss lernen, wie das Bauteil aussieht (Features) und wo es sich befindet (Bounding Box).<br><br><strong>Assisted Labeling:</strong> Nutzt das Basis-Modell, um bereits bekannte Objekte vorzuschlagen, was dir viel Handarbeit spart. Füge oben rechts eigene Klassen (z.B. 'Zahnrad') hinzu und rahme sie auf dem Canvas ein.</p>",
    training: "<p>Wir nutzen <strong>Transfer Learning</strong>. Das neuronale Netz hat durch das Pre-Training auf Millionen von Bildern bereits gelernt, Kanten und Formen zu erkennen. Wir trainieren nun nur die letzte Schicht (Klassifikation) auf deine neuen Bauteile um. Dies ist effizient und läuft direkt auf der NVIDIA GPU des Jetsons (CUDA).<br><br>Die <em>Loss</em>-Kurve sollte im Laufe der Epochen sinken.</p>",
    eval: "<p>Nach dem Training wird das Modell gegen die Test-Bilder geprüft, die nicht beim Training verwendet wurden. Die wichtigsten Metriken sind <strong>Precision</strong> (Genauigkeit: Wie viele gefundene Objekte sind wirklich korrekt?) und <strong>Recall</strong> (Trefferquote: Wie viele der tatsächlich vorhandenen Objekte wurden gefunden?).<br>Der <strong>mAP</strong> (mean Average Precision) fasst die Leistung über alle Klassen zusammen.</p>"
  };
  
  document.getElementById("info-modal-title").innerHTML = titles[tabId] || "Info";
  document.getElementById("info-modal-body").innerHTML = texts[tabId] || "Keine Information verfügbar.";
  document.getElementById("info-modal").style.display = "flex";
}

// Lightbox keyboard navigation
document.addEventListener("keydown", e => {
  const modal = document.getElementById("lightbox-modal");
  if(modal && modal.style.display === "flex") {
    if(e.key === "ArrowLeft") navLightbox(-1);
    if(e.key === "ArrowRight") navLightbox(1);
    if(e.key === "Escape") modal.style.display = "none";
  }
});


// ------------------------------------------------------------------
// Tab 5: Labeling
let labelingImages = [];
let activeImageId = null;
let activeImageObj = null;
let annotations = [];
let classes = [];
let selectedClassIdx = 0;
let isDrawing = false;
let startX, startY;

const canvas = document.getElementById("annotator-canvas");
let ctx = canvas ? canvas.getContext("2d") : null;

async function fetchClasses() {
  const res = await fetch("/api/labels");
  const data = await res.json();
  classes = data.classes;
  renderClassList();
}
async function addClass() {
  const name = document.getElementById("new-class-name").value.trim();
  if(!name) return;
  classes.push(name);
  await saveClasses();
  document.getElementById("new-class-name").value = "";
  renderClassList();
}
async function deleteClass(idx) {
  classes.splice(idx, 1);
  if(selectedClassIdx >= classes.length) selectedClassIdx = Math.max(0, classes.length-1);
  await saveClasses();
  renderClassList();
}
async function saveClasses() {
  await fetch("/api/labels", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({classes})});
}

function renderClassList() {
  const cl = document.getElementById("class-list");
  if(!cl) return;
  cl.innerHTML = classes.map((c, i) => `
    <div class="class-item ${i===selectedClassIdx?'active':''}" onclick="selectedClassIdx=${i}; renderClassList();" style="border-left:4px solid ${getColor(i)}">
      <span>${i}: ${c}</span>
      <button class="btn-del-class" onclick="event.stopPropagation(); deleteClass(${i})">❌</button>
    </div>
  `).join("");
}

async function fetchGalleryForLabeling() {
  const res = await fetch("/api/images");
  const data = await res.json();
  labelingImages = data.images;
  const list = document.getElementById("labeling-image-list");
  if(!list) return;
  list.innerHTML = labelingImages.map(img => `
    <div class="img-list-item ${img.id===activeImageId?'active':''}" onclick="selectImageForLabeling('${img.id}')">
      ${img.annotated ? '✅' : '⚪'} ${img.filename}
    </div>
  `).join("");
}

async function selectImageForLabeling(id) {
  activeImageId = id;
  fetchGalleryForLabeling();
  
  const res = await fetch(`/api/annotations/${id}`);
  const data = await res.json();
  annotations = data.annotations;

  const img = new Image();
  img.crossOrigin = "anonymous";
  img.onload = () => {
    activeImageObj = img;
    canvas.width = img.width;
    canvas.height = img.height;
    drawCanvas();
  };
  img.src = `/api/images/${id}`;
}

function drawCanvas() {
  if(!ctx || !activeImageObj) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(activeImageObj, 0, 0);
  
  annotations.forEach((box, i) => {
    const x = (box.cx - box.w/2) * canvas.width;
    const y = (box.cy - box.h/2) * canvas.height;
    const w = box.w * canvas.width;
    const h = box.h * canvas.height;
    ctx.strokeStyle = getColor(box.class_id);
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = getColor(box.class_id);
    ctx.font = "16px sans-serif";
    ctx.fillText(`${classes[box.class_id]}`, x, y-5);
  });
  renderBoxList();
}

function renderBoxList() {
  const bl = document.getElementById("box-list");
  if(!bl) return;
  bl.innerHTML = annotations.map((box, i) => `
    <div class="box-item">
      <span>${classes[box.class_id]}</span>
      <button onclick="deleteBox(${i})" style="background:transparent; border:none; cursor:pointer;">🗑️</button>
    </div>
  `).join("");
}

function deleteBox(idx) {
  annotations.splice(idx, 1);
  drawCanvas();
  saveAnnotationsSilently();
}

if(canvas) {
  canvas.addEventListener("mousedown", e => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    startX = (e.clientX - rect.left) * scaleX;
    startY = (e.clientY - rect.top) * scaleY;
  });
  canvas.addEventListener("mousemove", e => {
    if(!isDrawing) return;
    drawCanvas();
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const currentX = (e.clientX - rect.left) * scaleX;
    const currentY = (e.clientY - rect.top) * scaleY;
    ctx.strokeStyle = getColor(selectedClassIdx);
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(startX, startY, currentX-startX, currentY-startY);
    ctx.setLineDash([]);
  });
  canvas.addEventListener("mouseup", e => {
    if(!isDrawing) return;
    isDrawing = false;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const endX = (e.clientX - rect.left) * scaleX;
    const endY = (e.clientY - rect.top) * scaleY;
    
    const w = Math.abs(endX - startX) / canvas.width;
    const h = Math.abs(endY - startY) / canvas.height;
    if(w > 0.01 && h > 0.01) {
      const cx = (Math.min(startX, endX) / canvas.width) + w/2;
      const cy = (Math.min(startY, endY) / canvas.height) + h/2;
      annotations.push({class_id: selectedClassIdx, cx, cy, w, h});
      saveAnnotationsSilently();
    }
    drawCanvas();
  });
}

function getColor(idx) {
  const colors = ["#22c55e", "#f97316", "#3b82f6", "#ec4899", "#84cc16", "#14b8a6", "#eab308"];
  return colors[idx % colors.length];
}

async function saveAnnotationsSilently() {
  if(!activeImageId) return;
  await fetch(`/api/annotations/${activeImageId}`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({annotations})
  });
  fetchGalleryForLabeling(); // updates the tick
  showSaveIndicator();
}

function showSaveIndicator() {
  const ind = document.getElementById("save-indicator");
  if(ind) {
    ind.style.display = "block";
    setTimeout(() => { ind.style.display = "none"; }, 1500);
  }
}

function openBatchAssistedModal() {
  document.getElementById("batch-label-modal").style.display = "flex";
}

async function startBatchLabeling() {
  const model = document.getElementById("batch-model-select").value;
  // Set lower confidence for assisted labeling to catch more objects
  await fetch("/api/infer-config", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({model: model, confidence: 0.25})
  });
  
  document.getElementById("batch-label-modal").style.display = "none";
  alert("Batch Labeling gestartet. Dies kann einen Moment dauern...");
  
  // Loop over unlabeled images
  let count = 0;
  for (let img of labelingImages) {
    if (!img.annotated) {
      const res = await fetch(`/api/assisted-label/${img.id}`, {method:"POST"});
      if(res.ok) {
        const data = await res.json();
        const mapped = data.annotations.map(a => ({
          class_id: Math.min(a.class_id, classes.length-1),
          cx: a.cx, cy: a.cy, w: a.w, h: a.h
        }));
        await fetch(`/api/annotations/${img.id}`, {
          method: "POST", headers: {"Content-Type":"application/json"},
          body: JSON.stringify({annotations: mapped})
        });
        count++;
      }
    }
  }
  alert(`Fertig! ${count} Bilder wurden assistiert gelabelt.`);
  fetchGalleryForLabeling();
  if(activeImageId) selectImageForLabeling(activeImageId);
}

// ------------------------------------------------------------------
// Tab 6: Training
async function startTraining() {
  const url = document.getElementById("train-url").value;
  const epochs = parseInt(document.getElementById("train-epochs").value);
  const model = document.getElementById("train-model").value;
  const res = await fetch("/api/training/start", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({server_url: url, epochs, model, local: !url})
  });
  if(res.ok) {
    startTrainPolling();
    document.getElementById("btn-train-start").style.display = "none";
    document.getElementById("btn-train-stop").style.display = "inline-block";
  }
}

async function stopTraining() {
  await fetch("/api/training/stop", {method:"POST"});
  document.getElementById("btn-train-start").style.display = "inline-block";
  document.getElementById("btn-train-stop").style.display = "none";
}

function startTrainPolling() {
  if(!trainInterval) trainInterval = setInterval(async () => {
    const res = await fetch("/api/training/status");
    const d = await res.json();
    document.getElementById("train-status-badge").textContent = d.status;
    document.getElementById("train-epoch").textContent = d.epoch;
    document.getElementById("train-total").textContent = d.total_epochs;
    document.getElementById("train-loss").textContent = d.train_loss;
    document.getElementById("train-log").textContent = d.log;
    document.getElementById("train-log").scrollTop = document.getElementById("train-log").scrollHeight;
    
    if(d.total_epochs > 0) {
      document.getElementById("train-progress").style.width = `${(d.epoch / d.total_epochs)*100}%`;
    }
    if(d.status === "done" || d.status === "error") {
      stopTrainPolling();
      document.getElementById("btn-train-start").style.display = "inline-block";
      document.getElementById("btn-train-stop").style.display = "none";
    }
  }, 2000);
}
function stopTrainPolling() { if(trainInterval) { clearInterval(trainInterval); trainInterval = null; } }

// ------------------------------------------------------------------
// Tab 7: Eval
async function runEvaluation() {
  const out = document.getElementById("eval-results");
  out.innerHTML = `<p>Läuft... bitte warten.</p>`;
  const res = await fetch("/api/evaluation/run", {method:"POST"});
  const d = await res.json();
  if(d.error) {
    out.innerHTML = `<p style="color:red;">${d.error}</p>`;
  } else {
    out.innerHTML = `
      <h3>Ergebnisse:</h3>
      <p><strong>Bilder evaluiert:</strong> ${d.images_evaluated}</p>
      <p><strong>Precision:</strong> ${d.precision}</p>
      <p><strong>Recall:</strong> ${d.recall}</p>
      <p><strong>mAP50 (approx):</strong> ${d.mAP50_approx}</p>
    `;
  }
}
async function generateReport() {
  window.open("/api/report/generate", "_blank");
}

// ------------------------------------------------------------------
// Tab 8: Admin
function showAdminLogin() {
  if(isAdmin) { switchTab('admin'); return; }
  document.getElementById('admin-modal').style.display='flex';
}
async function verifyAdmin() {
  const pin = document.getElementById('admin-pin').value;
  const res = await fetch("/api/admin/verify-pin", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({pin})
  });
  const d = await res.json();
  if(d.ok) {
    isAdmin = true;
    document.getElementById('admin-modal').style.display='none';
    document.getElementById('nav-admin').style.display='block';
    switchTab('admin');
  } else {
    alert("Falscher PIN");
  }
}
async function saveNetwork() {
  const mode = document.getElementById('admin-wifi-mode').value;
  const ssid = document.getElementById('admin-wifi-ssid').value;
  const password = document.getElementById('admin-wifi-pass').value;
  const res = await fetch("/api/admin/network", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({mode, ssid, password})
  });
  alert("Gespeichert. Bitte Gerät neustarten, damit die Änderungen wirksam werden.");
}
async function systemUpdate() {
  alert("System-Update (Git Pull) kann aus dem Docker-Container heraus fehlschlagen.\n\nBitte öffne ein Terminal auf dem Jetson und führe aus:\n\ncd ~/yolo-ai-lab && git pull && sudo docker-compose up -d --build");
}
async function resetWorkspace() {
  if(confirm("Alle Praktikumsdaten wirklich löschen?")) {
    await fetch("/api/reset", {method:"POST"});
    alert("Workspace zurückgesetzt!");
    location.reload();
  }
}
