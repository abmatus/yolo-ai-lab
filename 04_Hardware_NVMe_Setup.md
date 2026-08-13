# 🔧 NVIDIA Jetson Orin Nano Hardware & Boot-Setup

## 📋 Übersicht
Das System wurde von einer SD-Karten-Lösung auf eine performante **NVMe SSD** migriert, um die Ladezeiten der Docker-Container und des KI-Trainings zu minimieren.

## 💾 Migration & Boot-Konfiguration
1. **Image:** Jetson Linux (L4T R36.4.7)
2. **Flash-Vorgang:** Direktes Schreiben auf NVMe via *Balena Etcher*.
3. **Boot-Fix:** 
   - Anpassung der `extlinux.conf`.
   - Änderung des Root-Pfades von `root=/dev/mmcblk0p1` zu `root=/dev/nvme0n1p1`.
4. **Firmware:** QSPI-Update wurde über einen temporären SD-Karten-Boot durchgeführt.

---

## 🛠️ Performance & NVMe Vorteile
- **Schnellere Container-Initialisierung:** Docker Daemon und Container-Builds starten in Bruchteilen von Sekunden.
- **Hohe I/O-Leistung beim KI-Training:** Schnelles Laden und Speichern von Bild-Datensätzen und YOLOv11 TensorRT Engine-Dateien.
- **Langzeitstabilität:** Schutz vor SD-Karten-Verschleiß bei intensiven Schreiboperationen während der Praktikumsversuche.
