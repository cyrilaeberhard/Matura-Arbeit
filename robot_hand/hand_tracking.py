# Handerkennung mit MediaPipe.

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config

_basis_optionen = python.BaseOptions(model_asset_path=config.MODELL_PFAD)
_hand_optionen = vision.HandLandmarkerOptions(
    base_options=_basis_optionen,
    num_hands=config.ANZAHL_HAENDE,
    # IMAGE-Modus: jedes Bild wird unabhängig erkannt, ohne Tracking über
    # mehrere Frames (siehe Arbeit Kap. 2.6.4). Das Zittern fängt glaetten() ab.
    running_mode=vision.RunningMode.IMAGE,
)
hand_erkenner = vision.HandLandmarker.create_from_options(_hand_optionen)


def kamera_oeffnen():
    return cv2.VideoCapture(config.KAMERA_INDEX)


def hand_erkennen(kamerabild_bgr):
    """Nimmt ein BGR-Kamerabild entgegen und gibt (rgb_bild, erkennergebnis) zurück."""
    kamerabild_rgb = cv2.cvtColor(kamerabild_bgr, cv2.COLOR_BGR2RGB)
    mp_bild = mp.Image(image_format=mp.ImageFormat.SRGB, data=kamerabild_rgb)

    erkennergebnis = hand_erkenner.detect(mp_bild)
    return kamerabild_rgb, erkennergebnis


def zeichne_punkte_und_text(rgb_bild, ergebnis, winkel_liste):
    bild_mit_anzeige = rgb_bild.copy()
    if ergebnis is None or not ergebnis.hand_landmarks:
        return bild_mit_anzeige

    bild_hoehe, bild_breite, _ = bild_mit_anzeige.shape
    hand = ergebnis.hand_landmarks[0]

    for punkt in hand:
        x_pixel = int(punkt.x * bild_breite)
        y_pixel = int(punkt.y * bild_hoehe)
        cv2.circle(bild_mit_anzeige, (x_pixel, y_pixel), 3, (0, 255, 0), -1)

    for i, (name, winkel) in enumerate(zip(config.FINGER_NAMEN, winkel_liste)):
        cv2.putText(bild_mit_anzeige, f"{name}: {winkel:.0f}°",
                    (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return bild_mit_anzeige
