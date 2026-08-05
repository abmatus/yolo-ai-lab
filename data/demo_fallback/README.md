# HFU AI-LAB Demo Fallback Data Directory

Ordnerstruktur für Offline-/Fallback-Beispielbilder der beiden Praktikumsszenarien:

## Szenario 1: Medizintechnik (OP-Besteck)
Legen Sie Beispielbilder von Skalpellen, Klemmen und Pinzetten in:
`data/demo_fallback/scenario_1_medical/images/`
`data/demo_fallback/scenario_1_medical/labels/`

## Szenario 2: Maschinenbau / WIng (Bosch IXO Akkuschrauber)
Legen Sie Beispielbilder der Bauteile (Gehäuse, Motor, Akku, Handbuch) in:
`data/demo_fallback/scenario_2_bosch/images/`
`data/demo_fallback/scenario_2_bosch/labels/`

---
Das System greift automatisch auf diesen Ordner zurück, wenn in Versuch 1 keine USB-Kamera erkannt wird oder der Demo-Modus ohne Live-Hardware betrieben wird.
