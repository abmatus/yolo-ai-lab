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
    step1Desc: "Siemensstern Schärfeeinstellung.",
    step2: "2. COCO Live",
    step2Desc: "Vertrautheits-Test YOLOv11.",
    step3: "3. Aufnahme",
    step3Desc: "Aufnahmen vom Bauteil.",
    step4: "4. Labeling",
    step4Desc: "KI-unterstützte Annotation.",
    step5: "5. Training",
    step5Desc: "Transfer Learning auf Jetson.",
    step6: "6. Evaluation",
    step6Desc: "mAP & PDF-Protokoll.",
    focusTitle: "Live-Kamerabild & Fokus-Messung (Siemensstern)",
    focusDesc: "Stellen Sie den manuellen Fokusring ein, bis die Linien scharf sind.",
    focusMeasArea: "Messbereich",
    focusScoreUnit: "/ 100",
    focusAlgoRow: "Algorithmus",
    focusAreaRow: "Messbereich",
    focusVarRow: "Laplace-Varianz",
    focusAreaValue: "Zentrum 40%",
    focusAlgoValue: "Laplacian σ²",
    focusHintDefault: "🎯 Platzieren Sie den Siemensstern im Messbereich und drehen Sie am Fokusring.",
    focusHintSharp: "✅ Optimaler Fokus erreicht!",
    focusHintGood: "🔄 Sehr gut! Noch etwas am Fokusring drehen.",
    focusHintOk: "🔄 Mittelmäßig. Score sollte steigen.",
    focusHintBlurry: "⚠️ Unscharf. Fokusring drehen.",
    zoneBlurry: "Unscharf",
    zoneOk: "Mittel",
    zoneGood: "Gut",
    zoneSharp: "Scharf"
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
    step1Desc: "Siemens star sharpness alignment.",
    step2: "2. COCO Live",
    step2Desc: "Familiarization test.",
    step3: "3. Capture",
    step3Desc: "Acquire component images.",
    step4: "4. Labeling",
    step4Desc: "AI-assisted annotation.",
    step5: "5. Training",
    step5Desc: "Transfer learning on Jetson.",
    step6: "6. Evaluation",
    step6Desc: "mAP & PDF report.",
    focusTitle: "Live Camera View & Focus Measurement",
    focusDesc: "Adjust the manual focus ring until the lines are sharp.",
    focusMeasArea: "Measurement Zone",
    focusScoreUnit: "/ 100",
    focusAlgoRow: "Algorithm",
    focusAreaRow: "Meas. Zone",
    focusVarRow: "Laplacian Variance",
    focusAreaValue: "Center 40%",
    focusAlgoValue: "Laplacian σ²",
    focusHintDefault: "🎯 Place the Siemens star in the measurement zone and rotate the focus ring.",
    focusHintSharp: "✅ Optimal focus achieved!",
    focusHintGood: "🔄 Very good! Rotate the focus ring a little more.",
    focusHintOk: "🔄 Moderate. The score should increase.",
    focusHintBlurry: "⚠️ Blurry. Rotate the focus ring.",
    zoneBlurry: "Blurry",
    zoneOk: "Moderate",
    zoneGood: "Good",
    zoneSharp: "Sharp"
  }
};

let currentLang = "de";
let focusInterval = null;
let trainInterval = null;
let isAdmin = false;

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  initDynamicLinks();
  startStatusPolling();
  
  // Attach Tab handlers
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.getAttribute("data-tab")));
  });

  // Fetch initial data
  fetchModels();
  fetchGallery();
  fetchClasses();
});

// Dynamic Links
function initDynamicLinks() {
  const host = window.location.hostname || "localhost";
  const jupyterBtn = document.getElementById("btn-jupyter-link");
  if (jupyterBtn) jupyterBtn.href = `http://${host}:8888`;

  // Set direct stream URLs
  const streamUrl = `http://${host}:8000/api/stream`;
  const inferUrl = `http://${host}:8000/api/infer-stream`;
  
  const imgMain = document.getElementById("cam-stream-main");
  const imgCapture = document.getElementById("cam-stream-capture");
  const imgInfer = document.getElementById("cam-stream-infer");
  
  if (imgMain) imgMain.src = streamUrl;
  if (imgCapture) imgCapture.src = streamUrl;
  if (imgInfer) imgInfer.src = inferUrl;
}

// Theme
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

// Language
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
    if (dict[key]) el.textContent = dict[key];
  });
}

// Tab Switching
function switchTab(target) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
  
  const btn = document.querySelector(`.tab-btn[data-tab="${target}"]`);
  if(btn) btn.classList.add("active");
  const tab = document.getElementById(`tab-${target}`);
  if(tab) tab.classList.add("active");

  // Handle specific tab polling
  if (target === "kiosk") startFocusPolling();
  else stopFocusPolling();

  if (target === "coco") startInferPolling();
  else stopInferPolling();

  if (target === "capture") fetchGallery();
  if (target === "labeling") { fetchGalleryForLabeling(); fetchClasses(); }
  
  if (target === "training") startTrainPolling();
  else stopTrainPolling();
}

// System Status Polling
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

// Focus Score Polling
async function fetchFocusScore() {
  try {
    const host = window.location.hostname || "localhost";
    const res  = await fetch(`http://${host}:8000/api/focus-score`);
    if (!res.ok) return;
    const d = await res.json();

    const scoreEl = document.getElementById("focus-score-num");
    const gaugeEl = document.getElementById("focus-gauge-fill");
    const badgeEl = document.getElementById("focus-label-badge");
    const rawEl   = document.getElementById("focus-raw-var");
    const hintEl  = document.getElementById("focus-hint");

    if (scoreEl) { scoreEl.textContent = d.score; scoreEl.style.color = d.color; }
    if (gaugeEl) gaugeEl.style.width = d.score + "%";
    if (badgeEl) {
      badgeEl.textContent = d.label_de;
      badgeEl.style.background = d.color + "22";
      badgeEl.style.color      = d.color;
    }
    if (rawEl) rawEl.textContent = d.raw_variance.toFixed(1);
    if (hintEl) {
      const t = i18n[currentLang];
      if (d.label === "sharp") { hintEl.textContent = t.focusHintSharp; hintEl.style.color = "#16a34a"; }
      else if (d.label === "good") { hintEl.textContent = t.focusHintGood; hintEl.style.color = "#65a30d"; }
      else if (d.label === "ok") { hintEl.textContent = t.focusHintOk; hintEl.style.color = "#d97706"; }
      else if (d.label === "blurry") { hintEl.textContent = t.focusHintBlurry; hintEl.style.color = "#dc2626"; }
      else { hintEl.textContent = t.focusHintDefault; hintEl.style.color = ""; }
    }
  } catch (e) {}
}

function startFocusPolling() { if (!focusInterval) focusInterval = setInterval(fetchFocusScore, 500); }
function stopFocusPolling() { if (focusInterval) { clearInterval(focusInterval); focusInterval = null; } }

// ------------------------------------------------------------------
// Tab 3: COCO Live Inference
let inferInterval = null;
async function fetchModels() {
  const res = await fetch("/api/models");
  const data = await res.json();
  const sel = document.getElementById("coco-model-select");
  if(sel) {
    sel.innerHTML = "";
    data.builtin.forEach(m => sel.add(new Option(m, m)));
    data.custom.forEach(m => sel.add(new Option("Custom: " + m, m)));
    sel.value = data.current;
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
    const list = document.getElementById("infer-dets");
    list.innerHTML = d.detections.map(det => `
      <div class="det-item">
        <span class="det-cls">${det.class}</span>
        <span class="det-conf">${det.confidence}</span>
      </div>`).join("");
  }, 1000);
}
function stopInferPolling() { if(inferInterval) { clearInterval(inferInterval); inferInterval=null; } }

// ------------------------------------------------------------------
// Tab 4: Capture (Galerie)
let currentLightboxId = null;
async function captureImage() {
  const res = await fetch("/api/capture", {method:"POST"});
  if (res.ok) fetchGallery();
}

async function fetchGallery() {
  const res = await fetch("/api/images");
  const data = await res.json();
  document.getElementById("gallery-count").textContent = data.total;
  const grid = document.getElementById("gallery-grid");
  if(!grid) return;
  grid.innerHTML = data.images.map(img => `
    <div class="gallery-item" onclick="openLightbox('${img.id}')">
      <img src="/api/images/${img.id}" loading="lazy">
      ${img.annotated ? '<span class="badge-success">Labeled</span>' : ''}
    </div>
  `).join("");
}

function openLightbox(id) {
  currentLightboxId = id;
  const modal = document.getElementById("lightbox-modal");
  document.getElementById("lightbox-img").src = `/api/images/${id}`;
  modal.style.display = "block";
}
async function deleteCurrentImage() {
  if(!currentLightboxId) return;
  if(confirm("Bild wirklich löschen?")) {
    await fetch(`/api/images/${currentLightboxId}`, {method:"DELETE"});
    document.getElementById("lightbox-modal").style.display = "none";
    fetchGallery();
    fetchGalleryForLabeling();
  }
}

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
  await fetch("/api/labels", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({classes})});
  document.getElementById("new-class-name").value = "";
  renderClassList();
}
function renderClassList() {
  const cl = document.getElementById("class-list");
  if(!cl) return;
  cl.innerHTML = classes.map((c, i) => `
    <div class="class-item ${i===selectedClassIdx?'active':''}" onclick="selectedClassIdx=${i}; renderClassList();" style="border-left:4px solid ${getColor(i)}">
      ${i}: ${c}
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
  fetchGalleryForLabeling(); // update active state
  
  // load annotations
  const res = await fetch(`/api/annotations/${id}`);
  const data = await res.json();
  annotations = data.annotations;

  // load image to canvas
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
      <button onclick="deleteBox(${i})">🗑️</button>
    </div>
  `).join("");
}

function deleteBox(idx) {
  annotations.splice(idx, 1);
  drawCanvas();
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
    }
    drawCanvas();
  });
}

function getColor(idx) {
  const colors = ["#22c55e", "#f97316", "#3b82f6", "#ec4899", "#84cc16", "#14b8a6", "#eab308"];
  return colors[idx % colors.length];
}

async function saveAnnotations() {
  if(!activeImageId) return;
  await fetch(`/api/annotations/${activeImageId}`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({annotations})
  });
  alert("Gespeichert!");
  fetchGalleryForLabeling();
}

async function runAssistedLabeling() {
  if(!activeImageId) return;
  const res = await fetch(`/api/assisted-label/${activeImageId}`, {method:"POST"});
  if(res.ok) {
    const data = await res.json();
    annotations = data.annotations.map(a => ({
      class_id: Math.min(a.class_id, classes.length-1),
      cx: a.cx, cy: a.cy, w: a.w, h: a.h
    }));
    drawCanvas();
  } else {
    alert("Fehler bei Assisted Labeling");
  }
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

async function runEvaluation() {
  const res = await fetch("/api/evaluation/run", {method:"POST"});
  const d = await res.json();
  const out = document.getElementById("eval-results");
  if(d.error) {
    out.innerHTML = `<p style="color:red;">${d.error}</p>`;
  } else {
    out.innerHTML = `
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
// Tab 7: Admin
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
  alert("Update wird ausgeführt...");
  const res = await fetch("/api/admin/update", {method:"POST"});
  const d = await res.json();
  alert(d.output || d.error);
}
async function resetWorkspace() {
  if(confirm("Alle Praktikumsdaten wirklich löschen?")) {
    await fetch("/api/reset", {method:"POST"});
    alert("Workspace zurückgesetzt!");
    location.reload();
  }
}
