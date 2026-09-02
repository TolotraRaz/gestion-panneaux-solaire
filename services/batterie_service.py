"""
Service de calcul de la batterie.
"""
from config import MARGE_BATTERIE


def calculer_capacite_batterie(energie_nuit_wh):
    """
    Calcule la capacité nécessaire de la batterie avec marge de sécurité (+50%).
    
    Args:
        energie_nuit_wh: Énergie nécessaire la nuit en Wh
    
    Returns:
        float: Capacité batterie en Wh (avec marge)
    """
    return energie_nuit_wh * MARGE_BATTERIE


def temps_charge(capacite_wh, puissance_disponible_w):
    """
    Calcule le temps nécessaire pour charger la batterie.
    
    Formule: Temps (h) = Capacité (Wh) / Puissance disponible (W)
    
    Args:
        capacite_wh: Capacité de la batterie en Wh
        puissance_disponible_w: Puissance disponible pour la recharge en W
    
    Returns:
        float: Temps de charge en heures
    """
    if puissance_disponible_w <= 0:
        return float('inf')
    return capacite_wh / puissance_disponible_w


def verifier_autonomie_nuit(capacite_wh, energie_nuit_wh):
    """
    Vérifie si la batterie a assez de capacité pour la nuit.
    
    Returns:
        tuple: (bool suffisant, float marge en %)
    """
    if energie_nuit_wh <= 0:
        return True, 100.0
    
    marge = ((capacite_wh - energie_nuit_wh) / energie_nuit_wh) * 100
    return capacite_wh >= energie_nuit_wh, round(marge, 1)
