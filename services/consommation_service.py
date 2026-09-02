"""
Service de calcul de consommation énergétique.
"""
from config import TRANCHE_MATIN, TRANCHE_SOIR, TRANCHE_NUIT, PRODUCTION_SOIR


def calculer_energie(appareil):
    """
    Calcule l'énergie consommée par un appareil.
    
    Returns:
        float: Énergie en Wh
    """
    return appareil.energie_wh()


def separer_par_tranche(appareils):
    """
    Sépare les appareils par tranche horaire.
    
    Returns:
        dict: {'matin': [...], 'soir': [...], 'nuit': [...]}
    """
    result = {
        TRANCHE_MATIN: [],
        TRANCHE_SOIR: [],
        TRANCHE_NUIT: []
    }
    for appareil in appareils:
        result[appareil.tranche].append(appareil)
    return result


def calculer_energie_par_tranche(appareils):
    """
    Calcule l'énergie totale par tranche horaire.
    
    Returns:
        dict: {'matin': float, 'soir': float, 'nuit': float} en Wh
    """
    par_tranche = separer_par_tranche(appareils)
    return {
        TRANCHE_MATIN: sum(a.energie_wh() for a in par_tranche[TRANCHE_MATIN]),
        TRANCHE_SOIR: sum(a.energie_wh() for a in par_tranche[TRANCHE_SOIR]),
        TRANCHE_NUIT: sum(a.energie_wh() for a in par_tranche[TRANCHE_NUIT])
    }


def calculer_total_jour(appareils):
    """
    Calcule la consommation totale de jour (matin + 50% soir).
    Les appareils du soir sont alimentés à 50% par le panneau solaire.
    
    Returns:
        float: Énergie jour en Wh
    """
    energies = calculer_energie_par_tranche(appareils)
    return energies[TRANCHE_MATIN] + (energies[TRANCHE_SOIR] * PRODUCTION_SOIR)


def calculer_total_nuit(appareils):
    """
    Calcule la consommation totale de nuit (nuit + 50% soir).
    Les appareils du soir sont alimentés à 50% par la batterie.
    
    Returns:
        float: Énergie nuit en Wh
    """
    energies = calculer_energie_par_tranche(appareils)
    return energies[TRANCHE_NUIT] + (energies[TRANCHE_SOIR] * (1 - PRODUCTION_SOIR))


def calculer_total(appareils):
    """
    Calcule la consommation totale (toutes tranches confondues).
    
    Returns:
        float: Énergie totale en Wh
    """
    return sum(a.energie_wh() for a in appareils)
