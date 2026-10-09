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
# Antwort "Servos gestellt" nur im Messmodus (latenz_seriell.py schaltet ihn mit "?"
# ein, mit "!" aus). Im Betrieb liest der Laptop nichts zurück, die 43 Byte pro
# Zeile kosteten den ESP32 nur Zeit.
_antworten = False


def servo_stellen(duty, pin):
    if not (config.DUTY_MIN <= duty <= config.DUTY_MAX):
        return
    if pin not in _pwm_cache:
        _pwm_cache[pin] = machine.PWM(machine.Pin(pin), freq=config.SERVO_FREQ)
    _pwm_cache[pin].duty(duty)


def verarbeite_nachricht(zeile):
    global _antworten
    if zeile in ("?", "!"):
        _antworten = zeile == "?"
        print("Messmodus", "an" if _antworten else "aus")
        return
    try:
        duty_liste = [int(w.strip()) for w in zeile.split(",")]
        if len(duty_liste) == len(config.SERVO_PINS):
            for i, pin in enumerate(config.SERVO_PINS):
                servo_stellen(duty_liste[i], pin)
            if _antworten:
                print("Servos gestellt:", duty_liste)
    except ValueError:
        print("Fehler bei:", zeile)


def main():
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    print("Bereit - warte auf Daten...")

    puffer = ""
    while True:
        poller.poll()  # schlafen, bis Daten kommen
        # Alles abholen, was schon angekommen ist, und nur die neueste vollständige
        # Zeile verwenden. Vorher wurde jede Zeile einzeln abgearbeitet: Sendet der
        # Laptop schneller, als der ESP32 verarbeitet, warteten alte Stellungen in
        # einer Schlange (im Video ~350 ms Verzögerung). Ältere Zeilen sind veraltet.
        neueste = None
        while poller.poll(0):
            zeichen = sys.stdin.read(1)
            if zeichen == "\n":
                if puffer in ("?", "!"):  # Schalter nie verwerfen
                    verarbeite_nachricht(puffer)
                else:
                    neueste = puffer
                puffer = ""
            else:
                puffer += zeichen
        if neueste is not None:
            verarbeite_nachricht(neueste)


main()
