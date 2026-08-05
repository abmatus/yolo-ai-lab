# Dokument B: Didaktischer Leitfaden & Anwendungsszenarien

Da die Zielgruppe aus Maschinenbau, Medizintechnik und Wirtschaftsingenieurwesen besteht, müssen die Beispiele domänenspezifisch sein.

**Szenarien:**
1. **Szenario 1 (Medizintechnik):** Automatische Zählung und Überprüfung von OP-Besteck (Skalpell, Klemme, Pinzette) zur Qualitätssicherung nach der Sterilisation.
2. **Szenario 2 (Maschinenbau/Wirtschaftsing.):** Montageüberprüfung eines IXO-Akkuschraubers (Gehäuseschale, Motor, Akku, Handbuch). Sind alle Teile in der Box vorhanden?

**Die 6 Schritte des Praktikums:**
1. **Setup:** Fokus der Industriekamera mit Siemensstern einstellen (Hardware-Understanding).
2. **Exploration:** Test von YOLOv11 COCO auf Alltagsgegenstände (Confidence vs. Realität).
3. **Data Collection:** Aufnahme von mind. 30 Bildern der Szenario-Objekte unter dem Bosch-Lichtbalken.
4. **Annotation:** Assisted Labeling via vortrainierter Netzwerke und manueller Korrektur.
5. **Training:** YOLOv11 Transfer-Learning direkt auf der Orin Nano GPU.
6. **Evaluation:** Test des eigenen Modells. Bewertung von mAP, Precision und Recall im Kontext industrieller Fehlerquoten.