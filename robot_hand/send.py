# Senden der berechneten PWM-Signale an den ESP32 über die serielle Schnittstelle.

import serial

import config

_ser = None


def verbindung_oeffnen():
    global _ser
    if _ser is None:
        _ser = serial.Serial(config.SERIAL_PORT, baudrate=config.BAUDRATE, timeout=config.SERIAL_TIMEOUT)
    return _ser


def duty_werte_senden(duty_liste):
    ser = verbindung_oeffnen()
    nachricht = ",".join(str(d) for d in duty_liste) + "\n"
    ser.write(nachricht.encode())


def schliessen():
    global _ser
    if _ser is not None:
        _ser.close()
        _ser = None
