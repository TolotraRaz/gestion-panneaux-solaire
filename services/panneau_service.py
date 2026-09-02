"""
Service de calcul des panneaux solaires.
Supporte un rendement paramétrable pour les simulations Alea.
"""
from config import RENDEMENT_PANNEAU, HEURES_SOLEIL


def calculer_puissance_panneau(energie_jour_wh, energie_nuit_wh, heures_soleil=None, rendement=None):
    """
    Calcule la puissance nécessaire des panneaux solaires.
    
    Le panneau doit couvrir :
      - La consommation de jour
      - La recharge de la batterie (énergie de nuit)
    
    Formule: Puissance = (Énergie jour + Énergie nuit) / (heures soleil × rendement)
    
    Args:
        energie_jour_wh: Énergie consommée le jour en Wh
        energie_nuit_wh: Énergie consommée la nuit en Wh
        heures_soleil: Heures d'ensoleillement (défaut: config.HEURES_SOLEIL)
        rendement: Rendement du panneau (défaut: config.RENDEMENT_PANNEAU)
    
    Returns:
        float: Puissance panneau nécessaire en W
    """
    if heures_soleil is None:
        heures_soleil = HEURES_SOLEIL
    if rendement is None:
        rendement = RENDEMENT_PANNEAU

    besoin_total = energie_jour_wh + energie_nuit_wh
    return besoin_total / (heures_soleil * rendement)


def production_reelle(puissance_panneau_w, rendement=None):
    """
    Calcule la production réelle d'un panneau.
    
    Returns:
        float: Puissance réelle en W
    """
    if rendement is None:
        rendement = RENDEMENT_PANNEAU
    return puissance_panneau_w * rendement


def production_journaliere(puissance_panneau_w, heures_soleil=None, rendement=None):
    """
    Calcule la production journalière totale d'un panneau.
    
    Returns:
        float: Énergie produite en Wh
    """
    if heures_soleil is None:
        heures_soleil = HEURES_SOLEIL

    return production_reelle(puissance_panneau_w, rendement) * heures_soleil


def puissance_disponible_recharge(puissance_panneau_w, consommation_w, rendement=None):
    """
    Calcule la puissance disponible pour recharger la batterie.
    
    Returns:
        float: Puissance excédentaire en W (peut être négative si insuffisant)
    """
    return production_reelle(puissance_panneau_w, rendement) - consommation_w
