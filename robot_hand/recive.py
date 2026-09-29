# Läuft auf dem ESP32 (MicroPython).
# Empfängt fertige PWM-Duty-Werte über die serielle Verbindung (bereits von
# calculate.py berechnet) und stellt die Servos entsprechend.
#
# Hochladen zusammen mit config.py auf den ESP32 (z.B. per mpremote/ampy),
# z.B. als main.py oder über boot.py gestartet.

import machine
import sys
import select

import config

_pwm_cache = {}


def servo_stellen(duty, pin):
    if not (config.DUTY_MIN <= duty <= config.DUTY_MAX):
        return
    if pin not in _pwm_cache:
        _pwm_cache[pin] = machine.PWM(machine.Pin(pin), freq=config.SERVO_FREQ)
    _pwm_cache[pin].duty(duty)


def verarbeite_nachricht(zeile):
    try:
        duty_liste = [int(w.strip()) for w in zeile.split(",")]
        if len(duty_liste) == len(config.SERVO_PINS):
            for i, pin in enumerate(config.SERVO_PINS):
                servo_stellen(duty_liste[i], pin)
            print("Servos gestellt:", duty_liste)
    except ValueError:
        print("Fehler bei:", zeile)


def main():
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    print("Bereit - warte auf Daten...")

    puffer = ""
    while True:
        ereignisse = poller.poll(10)
        if ereignisse:
            zeichen = sys.stdin.read(1)
            if zeichen == "\n":
                verarbeite_nachricht(puffer)
                puffer = ""
            else:
                puffer += zeichen


main()
