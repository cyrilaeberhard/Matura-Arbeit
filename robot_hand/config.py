# Zentrale Einstellungen für die Handerkennung -> Servo-Steuerung.
# Diese Datei wird sowohl von den Host-Skripten (main.py, hand_tracking.py, ...)
# als auch vom ESP32 (recive.py, per mpremote/ampy hochgeladen) eingelesen.

# --- Kamera / MediaPipe ---
KAMERA_INDEX = 1
MODELL_PFAD = "/Users/cyrilaeberhard/local python/python/Maturaarbeit/hand_landmarker.task"
ANZAHL_HAENDE = 1

# --- Serielle Verbindung (Host <-> ESP32) ---
SERIAL_PORT = "/dev/cu.wchusbserial110"
BAUDRATE = 115200
SERIAL_TIMEOUT = 1

# --- Servo-Pins am ESP32 ---
# Reihenfolge: Daumen, Zeige, Mittel, Ring, Klein, Daumen-CMC (Abspreizung)
# TODO: Pin für den 6. Servo (Daumen-CMC) an die tatsächliche Verkabelung anpassen.
SERVO_PINS = [13, 12, 14, 27, 26, 25]
SERVO_FREQ = 50

# --- PWM-Duty-Grenzwerte (10-bit, passend zu machine.PWM(...).duty()) ---
# Harte Grenzen: recive.py verwirft alles ausserhalb (Schutz der Mechanik),
# servo_slider.py nutzt sie als Reglerbereich. 26-128 = ca. 0,5-2,5 ms.
DUTY_MIN = 26
DUTY_MAX = 128
# Pro Servo (Reihenfolge wie SERVO_PINS): Duty bei 0° und bei MAX_WINKEL.
# Werden mit servo_slider.py per Knopf gesetzt, das Programm schreibt diese
# beiden Zeilen neu.
DUTY_MIN_FINGER = [52, 42, 40, 40, 41, 46]
DUTY_MAX_FINGER = [114, 114, 114, 114, 113, 114]

# --- Finger-Landmark-Indexe im MediaPipe-Handmodell ---
FINGER_INDEXE = {
    1: {"grundgelenk": 2, "spitze": 4},    # Daumen
    2: {"grundgelenk": 5, "spitze": 8},    # Zeigefinger
    3: {"grundgelenk": 9, "spitze": 12},   # Mittelfinger
    4: {"grundgelenk": 13, "spitze": 16},  # Ringfinger
    5: {"grundgelenk": 17, "spitze": 20},  # Kleiner Finger
}
FINGER_NAMEN = ["Daumen", "Zeige", "Mittel", "Ring", "Klein", "Daumen CMC"]

# --- Kalibrierung Winkelberechnung (Zeige/Mittel/Ring/Klein, Bezug Handgelenk) ---
MIN_VERHAELTNIS = 0.7
MAX_VERHAELTNIS = 1.8
MAX_WINKEL = 120  # maximaler Servo-Winkel bei ganz ausgestrecktem Finger

# --- Kalibrierung Daumen-Beugung (Bezug: CMC-Gelenk (1) statt Handgelenk) ---
# Verhältnis dist(Spitze 4, CMC 1) / dist(Grundgelenk 2, CMC 1). Da CMC viel
# näher an den Daumengelenken liegt als das Handgelenk, ist dieser Wertebereich
# deutlich anders als MIN_VERHAELTNIS/MAX_VERHAELTNIS oben.
# Aus aufgenommenen Rohwerten bestimmt, danach von Auge verbessert.
DAUMEN_MIN_VERHAELTNIS = 1.8
DAUMEN_MAX_VERHAELTNIS = 2.4

# --- Kalibrierung Daumen-CMC-Gelenk (Einklappen über die Handfläche) ---
# Verhältnis (Daumenspitze<->Kleinfinger-Grundgelenk) / Handbreite.
# CMC_MIN_VERHAELTNIS: Daumen voll über die Handfläche eingeklappt.
# CMC_MAX_VERHAELTNIS: Daumen in normaler Ruheposition/gestreckt.
# Aus aufgenommenen Rohwerten bestimmt, danach von Auge verbessert.
CMC_MIN_VERHAELTNIS = 0.3
CMC_MAX_VERHAELTNIS = 1.3

# --- Glättung der Winkel zwischen zwei Frames ---
# (differenz_schwelle, faktor) -- je grösser die Bewegung, desto kleiner der
# Glättungsfaktor (schnelle Bewegung soll kaum verzögert werden)
GLAETTUNGS_STUFEN = [
    (30, 0.1),   # schnelle Bewegung
    (15, 0.3),   # mittlere Bewegung
    (5, 0.6),    # langsame Bewegung
]
GLAETTUNGS_FAKTOR_STANDARD = 0.85  # kaum Bewegung -> Zittern unterdrücken

# --- Separate Glättung für Daumen-Beugung (Index 0) und Daumen-CMC (Index 5) ---
# MediaPipe erkennt die Daumen-Landmarks deutlich unzuverlässiger als die
# übrigen Finger. Das dadurch entstehende Rauschen wird von der normalen
# Schwellenlogik oben sonst als "schnelle Bewegung" fehlinterpretiert und kaum
# geglättet -> ständiges Zittern. Deshalb hier höhere Schwellen und generell
# stärkere Faktoren: Nur wirklich grosse Sprünge gelten als echte Bewegung.
DAUMEN_GLAETTUNGS_STUFEN = [
    (30, 0.1),   # nur sehr grosse Sprünge -> etwas reaktionsschneller
    (25, 0.6),   # mittlerer Sprung -> könnte echte Bewegung sein
    (10, 0.8),   # kleiner Sprung -> vermutlich Erkennungsrauschen
]
DAUMEN_GLAETTUNGS_FAKTOR_STANDARD = 0.92  # kaum Sprung -> fast sicher Rauschen, stark glätten


START_WINKEL = [60, 60, 60, 60, 60, 60]
