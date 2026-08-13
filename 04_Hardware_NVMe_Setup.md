# 🔧 NVIDIA Jetson Orin Nano Super Hardware & Installation Guide (JetPack 7.2.1 / L4T r39.2.1)

> 🔗 **Offizielle Dokumentation:** Basierend auf dem [NVIDIA Jetson Orin Nano Developer Kit User Guide (Quick Start)](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html).

## 📋 Übersicht
Die HFU KI-Praktikumsstation nutzt **JetPack 7.2.1 (Jetson Linux r39.2.1)** auf einer performanten **NVMe SSD** (M.2 Key-M Slot), um die maximale KI-Rechenleistung des Jetson Orin Nano Super freizuschalten.

---

## ⚡ Wichtige Hardware- & Netzteil-Voraussetzungen
- **Spannungsversorgung:** 19V DC Netzteil (Anschließen am DC-Stecker, Power-LED nahe dem USB-C/DC Anschluss leuchtet auf).
- **Zielspeicher:** NVMe SSD (M.2 Key-M Slot) wird dringend für schnelle Docker-Container-Starts und TensorRT-Inferenz empfohlen.
- **Installationsmedium:** 16 GB+ USB 3.0 Stick mit der offiziellen Jetson ISO (`r39.2.1`).

---

## ⚠️ Die Firmware-Schranke ("Firmware Gate")
JetPack 7.2.1 erfordert mindestens die **UEFI/QSPI Firmware Version 36.x+**. Auf Geräten im alten Fabrikzustand (< 36.0) kann JetPack 7.2.1 nicht direkt installiert werden.

---

## 🛠️ Schritt-für-Schritt Installationsanleitung

### Schritt 1: UEFI/QSPI-Firmware prüfen
1. Schließe Monitor (DisplayPort/HDMI), Tastatur und 19V Netzteil an den Jetson an.
2. Drücke beim Einschalten mehrmals `Esc`, um ins **UEFI-Setup-Menü** zu gelangen.
3. Prüfe die angezeigte Firmware-Version oben auf dem Bildschirm:
   - **Version < 36.0 (Fabrikzustand):** Zuerst den *JetPack 6.x Update Path* durchlaufen, um die QSPI-Firmware auf Version 36.x zu aktualisieren.
   - **Version >= 36.x:** Bereit für Schritt 2!

### Schritt 2: USB-Installationsstick am PC erstellen
1. Benötigt einen **16 GB+ USB-Stick**.
2. Lade das **Jetson ISO (r39.2.1)** für JetPack 7.2.1 aus dem [NVIDIA Developer Center](https://developer.nvidia.com/embedded/downloads) herunter.
3. Schreibe das ISO mit **BalenaEtcher** auf den USB-Stick (*direkt flashen, nicht auf SD-Karte entpacken!*).

### Schritt 3: Jetson ISO booten & Firmware-Countdown
1. Stecke den USB-Stick und die **NVMe-SSD** (M.2 Slot) in den Jetson.
2. Starte das Gerät, gehe über `Esc` in den **Boot Manager** und wähle den USB-Stick als Boot-Laufwerk aus.
3. ⚠️ **Achtung (30-Sekunden Countdown!):** Beim ersten Start wird nach einem Firmware-Update gefragt. Bestätige **innerhalb von 30 Sekunden mit `Y`**. *Verpasst du dies, schlägt die spätere OS-Installation fehl!*

### Schritt 4: Betriebssystem auf NVMe-SSD installieren
1. Wähle im Installationsmenü die **NVMe-SSD** (`/dev/nvme0n1`) als Zielmedium aus.
2. Das System installiert Jetson Linux r39.2.1 auf die NVMe.
3. Richte nach dem automatischen Neustart Sprache (*Deutsch/Englisch*), Benutzername (`hfu`) und Passwort ein.

### Schritt 5: 'Super Performance' (MAXN SUPER) aktivieren
1. Melde dich im Ubuntu-Desktop an.
2. Klicke oben rechts im Panel auf das **Power Mode Applet** (oder nutze den Befehl `sudo nvpmodel -m 0`).
3. Stelle den Modus von `25W` auf **`MAXN SUPER`** um, um die maximale Taktung der Ampere GPU & Tensor Cores für YOLOv11 & TensorRT freizuschalten.

---

## 🔗 Weiterführende Links & NVIDIA Referenzen
- [NVIDIA Jetson Orin Nano Developer Kit User Guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html)
- [NVIDIA Jetson Embedded Download Center](https://developer.nvidia.com/embedded/downloads)
- [Jetson AI Lab & JetPack SDK Overview](https://www.jetson-ai-lab.com/)
