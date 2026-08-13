/* ==============================================================================
   HFU AI-LAB: Frontend Application JavaScript
   Bilingual i18n, Theme Manager, System Monitor, Kiosk & Demo Mode Logic
   ============================================================================== */

const i18n = {
  de: {
    stationTitle: "HFU KI-Praktikumsstation",
    subtitle: "Autarke Objekterkennung mit YOLOv11 & NVIDIA Jetson Orin Nano",
    tabDashboard: "Dashboard & BYOD",
    tabKiosk: "Hardware- & Fokus-Test",
    tabDemo: "Messe- / Demo-Modus",
    tabSystem: "System & USB Export",
    camStatus: "Kamera",
    wlanStatus: "WLAN AP",
    dockerStatus: "Docker Containers",
    openJupyter: "🚀 JupyterLab Starten",
    resetWorkspace: "🗑️ Praktikum Zurücksetzen",
    exportUSB: "💾 Daten auf USB-Stick exportieren",
    demoCallout: "Lege ein Objekt auf die Prüffläche. Kann die KI es erkennen?",
    attractTitle: "Willkommen am HFU KI-Praktikumsstand!",
    attractText: "Erleben Sie Echtzeit-Objekterkennung auf dem NVIDIA Jetson Orin Nano. Berühren Sie den Bildschirm, um zu starten.",
    welcomeTitle: "Willkommen zum Objekterkennungs-Praktikum",
    welcomeText: "Diese autarke KI-Workstation ermöglicht das vollständige Training und die Evaluierung eines modernen YOLOv11 Neuronalen Netzes direkt auf der NVIDIA Jetson Orin Nano GPU.",
    stepsTitle: "Praktikumsablauf (6 Schritte)",
    hardwareTitle: "Hardware Setup",
    focusTitle: "Live-Kamerabild & Fokus-Messung (Siemensstern)",
    focusDesc: "Stellen Sie den manuellen Fokusring der C-Mount Linse ein, bis die Linien des Siemenssterns im Zentrum scharf abgegrenzt sind.",
    exportTitle: "Daten-Export auf USB-Stick",
    exportDesc: "Kopiert alle erfassten Bilder, Annotations, trainierte YOLOv11 PyTorch & TensorRT Gewichte sowie den automatisch generierten PDF-Praktikumsbericht auf den angeschlossenen USB-Speicher.",
    resetTitle: "Station Zurücksetzen (System Reset)",
    resetDesc: "Setzt den Arbeitsbereich für das nächste Studierenden-Team zurück (Löscht Datensätze, Gewichte und Auswertungsberichte).",
    step1: "1. Hardware & Fokus",
    step1Desc: "Siemensstern Schärfeeinstellung der Industriekamera.",
    step2: "2. COCO Exploration",
    step2Desc: "Vertrautheits-Test mit vortrainierten YOLOv11-Klassen.",
    step3: "3. Bilderfassung",
    step3Desc: "30+ Aufnahmen von OP-Besteck oder IXO-Bauteilen.",
    step4: "4. Assisted Labeling",
    step4Desc: "KI-unterstützte Annotation & Korrektur.",
    step5: "5. YOLOv11 Training",
    step5Desc: "Transfer Learning direkt auf der Jetson GPU.",
    step6: "6. Real-World Evaluation",
    step6Desc: "TensorRT Beschleunigung, mAP & PDF-Protokoll.",
    systemResetSuccess: "Praktikumsdaten wurden erfolgreich zurückgesetzt!",
    usbExportSuccess: "Daten wurden erfolgreich auf den angeschlossenen USB-Stick exportiert!"
  },
  en: {
    stationTitle: "HFU AI Lab Workstation",
    subtitle: "Autonomous Object Detection with YOLOv11 & NVIDIA Jetson Orin Nano",
    tabDashboard: "Dashboard & BYOD",
    tabKiosk: "Hardware & Focus Test",
    tabDemo: "Exhibition / Demo Mode",
    tabSystem: "System & USB Export",
    camStatus: "Camera",
    wlanStatus: "WLAN AP",
    dockerStatus: "Docker Containers",
    openJupyter: "🚀 Launch JupyterLab",
    resetWorkspace: "🗑️ Reset Lab Workspace",
    exportUSB: "💾 Export Data to USB Drive",
    demoCallout: "Place an object on the inspection area. Can AI detect it?",
    attractTitle: "Welcome to the HFU AI Workstation!",
    attractText: "Experience real-time object detection powered by NVIDIA Jetson Orin Nano. Touch screen to start.",
    welcomeTitle: "Welcome to the Object Detection Lab",
    welcomeText: "This autonomous AI workstation enables end-to-end training and evaluation of a modern YOLOv11 Neural Network directly on the NVIDIA Jetson Orin Nano GPU.",
    stepsTitle: "Lab Workflow (6 Steps)",
    hardwareTitle: "Hardware Setup",
    focusTitle: "Live Camera View & Focus Measurement (Siemens Star)",
    focusDesc: "Adjust the manual focus ring on the C-mount lens until the Siemens star lines in the center are crisp and clear.",
    exportTitle: "Data Export to USB Drive",
    exportDesc: "Copies all captured images, annotations, trained YOLOv11 PyTorch & TensorRT weights, and the automatically generated PDF lab report to the connected USB drive.",
    resetTitle: "Reset Station (System Reset)",
    resetDesc: "Resets the workspace for the next student team (Clears datasets, trained weights, and evaluation reports).",
    step1: "1. Hardware & Focus",
    step1Desc: "Siemens star sharpness alignment of industrial camera.",
    step2: "2. COCO Exploration",
    step2Desc: "Familiarization test with pre-trained YOLOv11 classes.",
    step3: "3. Image Acquisition",
    step3Desc: "30+ captures of medical surgical tools or IXO components.",
    step4: "4. Assisted Labeling",
    step4Desc: "AI-assisted annotation & manual adjustment.",
    step5: "5. YOLOv11 Training",
    step5Desc: "Transfer learning directly on the Jetson GPU.",
    step6: "6. Real-World Evaluation",
    step6Desc: "TensorRT acceleration, mAP & PDF report export.",
    systemResetSuccess: "Workspace successfully reset for next student team!",
    usbExportSuccess: "Data successfully exported to connected USB drive!"
  }
};

let currentLang = "de";
let inactivityTimer = null;
const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  initTabs();
  initDynamicLinks();
  startStatusPolling();
  initAttractMode();
});

// Dynamic Links setup (JupyterLab port 8888 according to host IP/hostname)
function initDynamicLinks() {
  const host = window.location.hostname || "localhost";

  // JupyterLab direct link
  const jupyterBtn = document.getElementById("btn-jupyter-link");
  if (jupyterBtn) {
    jupyterBtn.href = `http://${host}:8888`;
  }

  // MJPEG stream: bypass Nginx and connect directly to backend on port 8000.
  // Nginx proxy_buffering causes the stream to freeze even with proxy_buffering off
  // on some Nginx versions. Direct connection is always reliable.
  const streamUrl = `http://${host}:8000/api/stream`;
  const streamMain = document.getElementById("cam-stream-main");
  const streamDemo = document.getElementById("cam-stream-demo");
  if (streamMain) streamMain.src = streamUrl;
  if (streamDemo) streamDemo.src = streamUrl;
}

// Theme Management
function initTheme() {
  const themeBtn = document.getElementById("theme-toggle");
  const savedTheme = localStorage.getItem("hfu_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  themeBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("hfu_theme", next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  document.getElementById("theme-toggle").textContent = theme === "dark" ? "☀️ Light" : "🌙 Dark";
}

// Language i18n Management
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
      el.textContent = dict[key];
    }
  });
}

// Navigation Tabs
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${target}`).classList.add("active");
      resetInactivityTimer();
    });
  });
}

// System Status Polling (Using relative endpoint /api/status via Nginx)
function startStatusPolling() {
  fetchStatus();
  setInterval(fetchStatus, 3000);
}

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    if (res.ok) {
      const data = await res.json();
      updateDot("dot-cam", data.camera.online);
      updateDot("dot-wlan", data.wlan.active);
      updateDot("dot-docker", data.status === "online");

      const ssidLabel = document.getElementById("ssid-display");
      if (ssidLabel) ssidLabel.textContent = data.wlan.ssid;
      
      const statsDisplay = document.getElementById("demo-stats");
      if (statsDisplay && data.system) {
        statsDisplay.textContent = `GPU/CPU: ${data.system.cpu_percent}% | RAM: ${data.system.ram_used_gb}/${data.system.ram_total_gb} GB`;
      }
    }
  } catch (e) {
    updateDot("dot-cam", false);
    updateDot("dot-wlan", false);
    updateDot("dot-docker", false);
  }
}

function updateDot(id, isOnline) {
  const dot = document.getElementById(id);
  if (dot) {
    if (isOnline) {
      dot.classList.add("online");
    } else {
      dot.classList.remove("online");
    }
  }
}

// Attract Mode Logic (Messe / Demo Timeout)
function initAttractMode() {
  ["mousemove", "keydown", "touchstart", "click"].forEach(evt => {
    window.addEventListener(evt, resetInactivityTimer);
  });
  resetInactivityTimer();
}

function resetInactivityTimer() {
  const attractScreen = document.getElementById("attract-screen");
  if (attractScreen) attractScreen.style.display = "none";
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(showAttractMode, INACTIVITY_TIMEOUT_MS);
}

function showAttractMode() {
  const demoTab = document.getElementById("tab-demo");
  if (demoTab && demoTab.classList.contains("active")) {
    const attractScreen = document.getElementById("attract-screen");
    if (attractScreen) attractScreen.style.display = "flex";
  }
}

// USB Export Handler (Using relative /api/export-usb)
async function triggerUSBExport() {
  const btn = document.getElementById("btn-usb-export");
  btn.disabled = true;
  btn.textContent = "⏳ Exporting...";
  try {
    const res = await fetch("/api/export-usb", { method: "POST" });
    const data = await res.json();
    alert(data.success ? i18n[currentLang].usbExportSuccess : `Export Result: ${data.output || data.error}`);
  } catch (e) {
    alert(`Export Error: ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = i18n[currentLang].exportUSB;
  }
}

// Reset Workspace Handler (Using relative /api/reset)
async function triggerResetWorkspace() {
  if (confirm(currentLang === "de" ? "Praktikumsdaten wirklich zurücksetzen?" : "Reset all student images, annotations and models?")) {
    try {
      const res = await fetch("/api/reset", { method: "POST" });
      const data = await res.json();
      alert(data.success ? i18n[currentLang].systemResetSuccess : `Reset Error: ${data.error}`);
    } catch (e) {
      alert(`Reset Error: ${e.message}`);
    }
  }
}
