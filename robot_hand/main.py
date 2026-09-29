# Steuert den gesamten Ablauf: Hand erkennen -> Winkel/PWM berechnen -> senden.

import cv2

import config
import hand_tracking
import calculate
import send


def main(show_camera=True):
    kamera = hand_tracking.kamera_oeffnen()
    letzte_winkel = list(config.START_WINKEL)

    try:
        while True:
            erfolgreich, kamerabild_bgr = kamera.read()
            if not erfolgreich:
                break

            # Spiegeln VOR der Erkennung, damit Landmarks und Text zur
            # gespiegelten Selfie-Ansicht passen (sonst wird auch der Text
            # spiegelverkehrt dargestellt).
            kamerabild_bgr = cv2.flip(kamerabild_bgr, 1)

            kamerabild_rgb, erkennergebnis = hand_tracking.hand_erkennen(kamerabild_bgr)

            if erkennergebnis and erkennergebnis.hand_landmarks:
                hand = erkennergebnis.hand_landmarks[0]
                neue_winkel = calculate.finger_winkel_berechnen(hand)
                letzte_winkel = calculate.glaetten(letzte_winkel, neue_winkel)

            duty_liste = calculate.winkel_liste_zu_duty_liste(letzte_winkel)
            send.duty_werte_senden(duty_liste)

            if show_camera:
                bild_mit_fingern = hand_tracking.zeichne_punkte_und_text(
                    kamerabild_rgb, erkennergebnis, letzte_winkel
                )
                bild_mit_fingern_bgr = cv2.cvtColor(bild_mit_fingern, cv2.COLOR_RGB2BGR)
                cv2.imshow("Handerkennung", bild_mit_fingern_bgr)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        kamera.release()
        cv2.destroyAllWindows()
        send.schliessen()


if __name__ == "__main__":
    main(show_camera=True)
