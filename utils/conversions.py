"""
Utilitaires de conversion d'unités et de gestion du temps.
"""


# ==========================================
# Conversions de puissance
# ==========================================

def w_to_kw(watts):
    """Convertit des watts en kilowatts."""
    return watts / 1000


def kw_to_w(kilowatts):
    """Convertit des kilowatts en watts."""
    return kilowatts * 1000


# ==========================================
# Conversions d'énergie
# ==========================================

def wh_to_kwh(wh):
    """Convertit des watt-heures en kilowatt-heures."""
    return wh / 1000


def kwh_to_wh(kwh):
    """Convertit des kilowatt-heures en watt-heures."""
    return kwh * 1000


# ==========================================
# Formatage
# ==========================================

def formater_energie(wh):
    """
    Formate une valeur d'énergie de manière lisible.
    Affiche en Wh si < 1000, sinon en kWh.
    """
    if wh >= 1000:
        return f"{wh_to_kwh(wh):.2f} kWh"
    return f"{wh:.2f} Wh"


def formater_puissance(w):
    """
    Formate une valeur de puissance de manière lisible.
    Affiche en W si < 1000, sinon en kW.
    """
    if w >= 1000:
        return f"{w_to_kw(w):.2f} kW"
    return f"{w:.2f} W"


# ==========================================
# Gestion du temps / tranches horaires
# ==========================================

def heure_vers_tranche(heure):
    """
    Détermine la tranche horaire à partir d'une heure (0-23).
    
    Returns:
        str: 'matin', 'soir' ou 'nuit'
    """
    if 6 <= heure < 17:
        return "matin"
    elif 17 <= heure < 19:
        return "soir"
    else:
        return "nuit"


def duree_tranche(tranche):
    """
    Retourne la durée d'une tranche horaire en heures.
    
    Returns:
        int: Nombre d'heures de la tranche
    """
    durees = {
        "matin": 11,   # 06h → 17h
        "soir": 2,     # 17h → 19h
        "nuit": 11     # 19h → 06h
    }
    return durees.get(tranche, 0)
