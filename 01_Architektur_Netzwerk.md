# Dokument A: Architektur & Netzwerk-Spezifikation

**Zielumgebung:** NVIDIA Jetson Orin Nano (Jetson Linux, L4T).

**Netzwerk:** 
- Der Jetson muss als Access Point agieren (SSID: `AI-LAB-ORIN`). 
- Eine lokale DNS-Auflösung (z.B. `ai-lab.local`) soll auf das Kiosk-Dashboard und JupyterLab verweisen.
- Es müssen mehrere dieser Stände parallel betrieben werden können.

**Containerisierung:** 
Alles muss in Docker-Containern laufen, um einen "System-Reset" durch Studierende zu ermöglichen (Löschen aller generierten Bilder/Modelle nach dem Praktikum). 
Benötigte Services:
- `frontend`: Web-Dashboard (Port 80)
- `backend`: API für Hardware-Status, Kamera-Stream-Verteilung und Reset-Logik.
- `jupyter`: JupyterLab Umgebung mit Ultralytics YOLOv11, PyTorch, OpenCV.

**Kamera-Handling:** 
Die USB-Kamera wird als `/dev/video0` in die Container gemountet.