# Berechnung der Finger-Winkel und der daraus resultierenden PWM-Signale.

import config


def abstand(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def daumen_cmc_winkel_berechnen(hand_landmark_liste):

    daumenspitze = hand_landmark_liste[4]
    kleinfinger_grund = hand_landmark_liste[17]
    zeigefinger_grund = hand_landmark_liste[5]

    handbreite = abstand(zeigefinger_grund, kleinfinger_grund)
    if handbreite == 0:
        return 0

    verhaeltnis = abstand(daumenspitze, kleinfinger_grund) / handbreite

    normiert = (config.CMC_MAX_VERHAELTNIS - verhaeltnis) / (config.CMC_MAX_VERHAELTNIS - config.CMC_MIN_VERHAELTNIS)
    normiert = max(0.0, min(1.0, normiert))

    return int(normiert * config.MAX_WINKEL)


def finger_winkel_berechnen(hand_landmark_liste):
    """Gibt 6 Winkel zurück: Daumen, Zeige, Mittel, Ring, Klein, Daumen-CMC."""
    handgelenk = hand_landmark_liste[0]
    winkel_liste = []

    for finger_nr in range(1, 6):
        indexe = config.FINGER_INDEXE[finger_nr]
        grund = hand_landmark_liste[indexe["grundgelenk"]]
        spitze = hand_landmark_liste[indexe["spitze"]]

        # Beim Daumen als Bezugspunkt das CMC-Gelenk (Landmark 1) statt dem
        # Handgelenk (0) verwenden -- das Handgelenk ist beim Daumen kein
        # zuverlässiger Bezug, da schon eine leichte Drehung/Kippen der Hand
        # den Abstand Handgelenk->Daumenspitze verfälscht.
        bezugspunkt = hand_landmark_liste[1] if finger_nr == 1 else handgelenk

        abstand_grund = abstand(bezugspunkt, grund)
        abstand_spitze = abstand(bezugspunkt, spitze)

        if abstand_grund == 0:
            verhaeltnis = 1.0
        else:
            verhaeltnis = abstand_spitze / abstand_grund

        if finger_nr == 1:
            min_verhaeltnis, max_verhaeltnis = config.DAUMEN_MIN_VERHAELTNIS, config.DAUMEN_MAX_VERHAELTNIS
        else:
            min_verhaeltnis, max_verhaeltnis = config.MIN_VERHAELTNIS, config.MAX_VERHAELTNIS

        normiert = (verhaeltnis - min_verhaeltnis) / (max_verhaeltnis - min_verhaeltnis)
        normiert = max(0.0, min(1.0, normiert))

        winkel_liste.append(int(normiert * config.MAX_WINKEL))

    winkel_liste.append(daumen_cmc_winkel_berechnen(hand_landmark_liste))

    return winkel_liste


def glaetten(alte_winkel, neue_winkel):
    """
    Glättet jeden Finger individuell basierend auf seiner Bewegungsgeschwindigkeit.
    Schnelle Bewegung -> kaum Verzögerung
    Langsame Bewegung -> stark glätten um Zittern zu unterdrücken

    Daumen-Beugung (Index 0) und Daumen-CMC (Index 5) nutzen eigene, stärkere
    Glättungswerte, da MediaPipe deren Landmarks unzuverlässiger erkennt.
    """
    ergebnis = []
    for i, (alt, neu) in enumerate(zip(alte_winkel, neue_winkel)):
        differenz = abs(neu - alt)

        if i in (0, 5):
            stufen = config.DAUMEN_GLAETTUNGS_STUFEN
            standard_faktor = config.DAUMEN_GLAETTUNGS_FAKTOR_STANDARD
        else:
            stufen = config.GLAETTUNGS_STUFEN
            standard_faktor = config.GLAETTUNGS_FAKTOR_STANDARD

        faktor = standard_faktor
        for schwelle, stufen_faktor in stufen:
            if differenz > schwelle:
                faktor = stufen_faktor
                break

        # Bewusst als Kommazahl weiterführen: mit int()/round() pro Frame
        # bleibt der Wert bei kleinen Differenzen hängen (z.B. Daumen f=0.92:
        # 0.08 * 6° < 0.5° -> kein Schritt mehr), der geglättete Winkel
        # erreicht den echten dann nie. Gerundet wird erst in winkel_zu_duty().
        ergebnis.append(faktor * alt + (1 - faktor) * neu)
    return ergebnis


def winkel_zu_duty(winkel):
    """Rechnet einen Servo-Winkel (0-180) in einen PWM-Duty-Wert um."""
    winkel = max(0, min(180, winkel))
    spanne = config.DUTY_MAX - config.DUTY_MIN
    # round statt int: der geglättete Winkel nähert sich z.B. 120° nur an
    # (119.9999...), int() würde dann dauerhaft einen Duty-Schritt zu tief liegen.
    return round((winkel / 180) * spanne + config.DUTY_MIN)


def winkel_liste_zu_duty_liste(winkel_liste):
    return [winkel_zu_duty(w) for w in winkel_liste]
