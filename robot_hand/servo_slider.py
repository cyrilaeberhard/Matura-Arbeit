# Stellt jeden Servo von Hand per Schieberegler (DUTY_MIN..DUTY_MAX), ohne Kamera.
# Zweck: herausfinden, welcher Kanal welchen Finger bewegt, und pro Finger
# die Endwerte einstellen: Regler auf die gewünschte Stellung, dann "Min"
# (= 0°, eingeklappt) bzw. "Max" (= MAX_WINKEL, gestreckt) drücken. Das
# schreibt DUTY_MIN_FINGER / DUTY_MAX_FINGER sofort in config.py.
#
# Auf dem ESP32 muss recive.py laufen, mit einer config.py, die schon die
# Grenzen 26-128 enthält.
# Zu grossen Teilen von Claude Code geschrieben.

import re
import tkinter as tk
from pathlib import Path

import serial

import config
import send

_CONFIG_PFAD = Path(config.__file__)


def config_liste_schreiben(name, werte):
    text = _CONFIG_PFAD.read_text()
    neu, anzahl = re.subn(rf"^{name} = .*$", f"{name} = {werte}", text, flags=re.M)
    if anzahl != 1:
        raise RuntimeError(f"{name} kommt in config.py nicht genau einmal vor ({anzahl}x)")
    _CONFIG_PFAD.write_text(neu)


def main():
    try:
        send.verbindung_oeffnen()
    except serial.SerialException as fehler:
        print("Serielle Verbindung fehlgeschlagen (", config.SERIAL_PORT, "):", fehler)
        return

    grenzen = {"DUTY_MIN_FINGER": list(config.DUTY_MIN_FINGER),
               "DUTY_MAX_FINGER": list(config.DUTY_MAX_FINGER)}

    fenster = tk.Tk()
    fenster.title("Servo-Slider")
    regler_werte = [tk.IntVar(value=(lo + hi) // 2) for lo, hi in zip(*grenzen.values())]
    grenz_texte = [tk.StringVar() for _ in config.SERVO_PINS]
    anzeige = tk.StringVar()

    def grenz_text_setzen(i):
        grenz_texte[i].set(f"Min {grenzen['DUTY_MIN_FINGER'][i]}  Max {grenzen['DUTY_MAX_FINGER'][i]}")

    def senden(_=None):
        duty_liste = [w.get() for w in regler_werte]
        send.duty_werte_senden(duty_liste)
        anzeige.set("Gesendet: " + ", ".join(str(d) for d in duty_liste))

    def grenze_setzen(name, i):
        neu = list(grenzen[name])
        neu[i] = regler_werte[i].get()
        config_liste_schreiben(name, neu)
        grenzen[name] = neu
        grenz_text_setzen(i)

    for i, (name, pin) in enumerate(zip(config.FINGER_NAMEN, config.SERVO_PINS)):
        tk.Label(fenster, text=f"Kanal {i}: {name} (GPIO {pin})").grid(row=i, column=0, sticky="w", padx=8)
        tk.Scale(
            fenster, from_=config.DUTY_MIN, to=config.DUTY_MAX, orient="horizontal",
            length=600, variable=regler_werte[i], command=senden,
        ).grid(row=i, column=1, padx=8)
        tk.Button(fenster, text="Min", command=lambda i=i: grenze_setzen("DUTY_MIN_FINGER", i)).grid(row=i, column=2)
        tk.Button(fenster, text="Max", command=lambda i=i: grenze_setzen("DUTY_MAX_FINGER", i)).grid(row=i, column=3)
        tk.Label(fenster, textvariable=grenz_texte[i], width=16).grid(row=i, column=4, padx=8)
        grenz_text_setzen(i)

    tk.Label(fenster, textvariable=anzeige, font=("Menlo", 14)).grid(
        row=len(config.SERVO_PINS), column=0, columnspan=5, pady=8)

    senden()
    try:
        fenster.mainloop()
    finally:
        send.schliessen()


if __name__ == "__main__":
    main()
