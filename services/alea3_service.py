"""
Service Alea 3 : Sélection de panneaux solaires optimaux.

Pour chaque type de panneau, calcule le nombre nécessaire pour atteindre
la puissance théorique requise, le prix total correspondant,
et la puissance vendable (excédentaire) le jour et le soir.
"""
import math
from config import HEURES_SOLEIL, PRODUCTION_SOIR


def calculer_options_panneaux(puissance_requise_w, panneaux, energies_tranche=None):
    """
    Pour chaque type de panneau, calcule combien il en faut, le coût total,
    et la puissance/énergie vendable par tranche.

    Args:
        puissance_requise_w: Puissance panneau requise (W) issue de la simulation
        panneaux: Liste de PanneauSolaire
        energies_tranche: dict {'matin': Wh, 'soir': Wh, 'nuit': Wh} (optionnel)

    Returns:
        list[dict]: Options triées par prix total croissant
    """
    if puissance_requise_w <= 0 or not panneaux:
        return []

    # Consommation en puissance (W) par tranche
    conso_jour_w = 0
    conso_soir_w = 0
    if energies_tranche:
        # Matin: énergie / heures soleil = puissance moyenne
        conso_jour_w = energies_tranche.get("matin", 0) / HEURES_SOLEIL if HEURES_SOLEIL > 0 else 0
        # Soir: énergie / 2h = puissance moyenne, mais seul PRODUCTION_SOIR est solaire
        duree_soir = 2  # 17h-19h
        conso_soir_w = energies_tranche.get("soir", 0) / duree_soir if duree_soir > 0 else 0

    options = []
    for p in panneaux:
        puissance_reelle = p.puissance_reelle_w
        if puissance_reelle <= 0:
            continue

        nb = math.ceil(puissance_requise_w / puissance_reelle)
        prix_total = nb * p.prix_unitaire
        puissance_totale = nb * puissance_reelle

        # Puissance vendable = production des panneaux - consommation
        # Jour : les panneaux produisent puissance_totale, on consomme conso_jour_w
        vendable_jour_w = max(0, puissance_totale - conso_jour_w)
        # Soir : les panneaux produisent à PRODUCTION_SOIR (50%), on consomme la part solaire du soir
        production_soir_w = puissance_totale * PRODUCTION_SOIR
        conso_soir_solaire_w = conso_soir_w * PRODUCTION_SOIR
        vendable_soir_w = max(0, production_soir_w - conso_soir_solaire_w)

        # Énergie vendable (Wh)
        duree_soir = 2
        energie_vendable_jour_wh = vendable_jour_w * HEURES_SOLEIL
        energie_vendable_soir_wh = vendable_soir_w * duree_soir

        options.append({
            "id": p.id,
            "nom": p.nom,
            "energie_unitaire_w": p.energie_unitaire_w,
            "pourcentage": p.pourcentage,
            "puissance_reelle_w": round(puissance_reelle, 2),
            "nb_panneaux": nb,
            "prix_unitaire": p.prix_unitaire,
            "prix_total": prix_total,
            "puissance_totale_w": round(puissance_totale, 2),
            # Vendable
            "vendable_jour_w": round(vendable_jour_w, 2),
            "vendable_soir_w": round(vendable_soir_w, 2),
            "energie_vendable_jour_wh": round(energie_vendable_jour_wh, 2),
            "energie_vendable_soir_wh": round(energie_vendable_soir_wh, 2),
        })

    # Trier par prix total croissant
    options.sort(key=lambda x: x["prix_total"])
    return options
