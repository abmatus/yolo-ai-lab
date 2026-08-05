# Dokument C: UI/UX & Messe-Modus Logik

**Globales Header-Menü:**
- **Sprach-Toggle:** DE | EN
- **Theme-Toggle:** ☀️ Light | 🌙 Dark
- **Status-Indikatoren (Grün/Rot):** Kamera, Docker, Hotspot.

**Messe-Modus (Demo):**
- **Ziel:** "Hook" für Vorbeigehende.
- **Visuals:** Großer Live-Kamera-Stream im Zentrum.
- **Gamification:** Aufforderung auf dem Bildschirm: *"Lege ein Objekt auf die Fläche. Kann die KI es erkennen?"*
- **Metriken:** Echtzeit-Anzeige der Inferenzgeschwindigkeit (FPS) und Confidence. Zeigt eindrucksvoll die Rechenleistung des Jetson Orin Nano.
- **Timeout-Logik:** Wenn 5 Minuten keine Bewegung im Bild ist, springt das System in einen "Attract Mode" (Slideshow der Praktikumsmöglichkeiten).