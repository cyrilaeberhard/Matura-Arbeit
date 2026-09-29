<div align="center">

# Kamerabasierte Steuerung einer anthropomorphen Roboterhand

**Maturaarbeit 2026 · Cyril Aeberhard**

Eine 3D-gedruckte Roboterhand, die menschliche Fingerbewegungen in Echtzeit nachbildet –
gesteuert allein über eine Laptopkamera, ohne Handschuh und ohne Sensoren am Körper.

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Landmarker-0097A7?logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5-5C3EE8?logo=opencv&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-MicroPython-E7352C?logo=espressif&logoColor=white)
![3D-Druck](https://img.shields.io/badge/3D--Druck-PLA%20%7C%20ABS%2B-555555)

</div>

---

## Voraussetzungen

- Laptop mit Python 3 und Kamera
- ESP32 mit MicroPython
- Roboterhand mit 6 Servos (MG90S)

## 3D-Druck

Die Teile der Hand liegen als 3MF-Dateien im Ordner [`3d/`](3d):

| Datei | Teil |
|---|---|
| `finger.3mf` | Finger mit Fingergliedern |
| `handgeruest.3mf` | Handgerüst |
| `servo-aufsatz.3mf` | Aufsatz für die Servos |
| `kabelhalter.3mf` | Kabelhalter |
| `verbindungsstuecke_14-10-6mm.3mf` | Verbindungsstücke in 14, 10 und 6 mm Länge, mit denen die Finger zusammengesetzt werden |

Gedruckt aus ABS+ (Prototypen aus PLA).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> MediaPipe ist auf Version 1.0.0 festgelegt, weil 1.0.1 unter macOS beim Start abstürzt.

## ESP32 einrichten

`recive.py` wird auf dem ESP32 als `main.py` gespeichert und startet so nach dem Einschalten
automatisch:

```bash
mpremote cp robot_hand/config.py :config.py
mpremote cp robot_hand/recive.py :main.py
```

## Einstellungen

In [`robot_hand/config.py`](robot_hand/config.py) an den eigenen Computer anpassen:

| Einstellung | Bedeutung |
|---|---|
| `MODELL_PFAD` | Pfad zu `hand_landmarker.task` |
| `SERIAL_PORT` | USB-Anschluss des ESP32, z. B. `/dev/cu.usbserial-…` |
| `KAMERA_INDEX` | Nummer der Kamera (meist `0` oder `1`) |

## Starten

```bash
python3 robot_hand/main.py
```

Beenden mit `q`.
