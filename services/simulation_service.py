"""
Service de simulation d'une journée complète.
Supporte Alea 1 (double rendement), Alea 2 (pic de consommation heure par heure),
et Alea 3 (sélection optimale de panneaux solaires).
"""
from services.consommation_service import (
    calculer_energie_par_tranche,
    calculer_total_jour,
    calculer_total_nuit,
    calculer_total,
    separer_par_tranche
)
from services.batterie_service import (
    calculer_capacite_batterie,
    temps_charge,
    verifier_autonomie_nuit
)
from services.panneau_service import (
    calculer_puissance_panneau,
    production_reelle,
    production_journaliere,
    puissance_disponible_recharge
)
from services.alea3_service import calculer_options_panneaux
from config import HEURES_SOLEIL, RENDEMENT_PANNEAU, MARGE_BATTERIE


def _simuler_avec_rendement(appareils, rendement, energie_jour, energie_nuit,
                             energie_totale, energies_tranche, capacite_batterie):
    """
    Effectue le calcul panneau + recharge pour un rendement donné.
    """
    puissance_panneau = calculer_puissance_panneau(
        energie_jour, energie_nuit, rendement=rendement
    )
    prod_reel = production_reelle(puissance_panneau, rendement=rendement)
    prod_jour = production_journaliere(puissance_panneau, rendement=rendement)

    conso_moyenne_jour_w = energie_jour / HEURES_SOLEIL if HEURES_SOLEIL > 0 else 0
    puissance_recharge = puissance_disponible_recharge(
        puissance_panneau, conso_moyenne_jour_w, rendement=rendement
    )
    temps_rech = temps_charge(capacite_batterie, puissance_recharge) if puissance_recharge > 0 else float('inf')
    recharge_ok = temps_rech <= HEURES_SOLEIL

    return {
        "rendement": rendement,
        "rendement_pct": int(rendement * 100),
        "panneau_puissance_w": round(puissance_panneau, 2),
        "panneau_production_reelle_w": round(prod_reel, 2),
        "panneau_production_journaliere_wh": round(prod_jour, 2),
        "puissance_recharge_w": round(puissance_recharge, 2) if puissance_recharge != float('inf') else 0,
        "temps_recharge_h": round(temps_rech, 2) if temps_rech != float('inf') else None,
        "recharge_ok": recharge_ok,
    }


def calculer_pic_consommation(appareils):
    """
    Alea 2 : Calcule le pic de consommation heure par heure.
    
    Pour chaque heure (0-23), on additionne la puissance de tous les appareils
    actifs à cette heure. Le pic = l'heure avec la somme la plus élevée.
    Le convertisseur doit être dimensionné à pic × 2.
    
    Returns:
        dict avec pic, convertisseur, heure du pic, détail heure par heure,
              et liste des appareils actifs au moment du pic
    """
    # Calcul heure par heure
    detail_par_heure = {}
    appareils_par_heure = {}

    for h in range(24):
        actifs = [a for a in appareils if a.est_actif_a(h)]
        puissance_totale = sum(a.puissance_w for a in actifs)
        detail_par_heure[h] = round(puissance_totale, 2)
        appareils_par_heure[h] = actifs

    if not detail_par_heure:
        return {
            "pic_w": 0,
            "heure_pic": 0,
            "convertisseur_w": 0,
            "detail_par_heure": {},
            "appareils_pic": []
        }

    # Trouver le pic
    heure_pic = max(detail_par_heure, key=lambda h: detail_par_heure[h])
    pic = detail_par_heure[heure_pic]

    # Appareils actifs au moment du pic
    appareils_pic = [
        {"nom": a.nom, "puissance_w": a.puissance_w, "horaire": f"{a.heure_debut}h->{a.heure_fin}h"}
        for a in appareils_par_heure[heure_pic]
    ]

    return {
        "pic_w": round(pic, 2),
        "heure_pic": heure_pic,
        "convertisseur_w": round(pic * 2, 2),
        "detail_par_heure": detail_par_heure,
        "appareils_pic": appareils_pic
    }


def simuler_journee(appareils, panneaux=None, prix_energie=None):
    """
    Simule une journée complète avec Alea 1, Alea 2 et Alea 3.
    
    Args:
        appareils: Liste des appareils
        panneaux: Liste de PanneauSolaire (optionnel, pour Alea 3)
        prix_energie: dict des prix d'achat énergie (optionnel)
    """
    if not appareils:
        return {
            "erreur": "Aucun appareil à simuler.",
            "statut": "ERREUR"
        }

    # --- 1. Calcul des consommations ---
    energies_tranche = calculer_energie_par_tranche(appareils)
    energie_jour = calculer_total_jour(appareils)
    energie_nuit = calculer_total_nuit(appareils)
    energie_totale = calculer_total(appareils)

    # --- 2. Dimensionnement batterie ---
    capacite_batterie = calculer_capacite_batterie(energie_nuit)
    autonomie_ok, marge_pct = verifier_autonomie_nuit(capacite_batterie, energie_nuit)

    # --- 3. Alea 1 : Double rendement (40% et 30%) ---
    rendements = [0.4, 0.3]
    alea1_resultats = []
    for rend in rendements:
        res = _simuler_avec_rendement(
            appareils, rend, energie_jour, energie_nuit,
            energie_totale, energies_tranche, capacite_batterie
        )
        alea1_resultats.append(res)

    ref = alea1_resultats[0]  # Référence = 40%

    # --- 4. Alea 2 : Pic de consommation heure par heure ---
    alea2 = calculer_pic_consommation(appareils)

    # --- 5. Alea 3 : Sélection de panneaux solaires ---
    alea3 = []
    if panneaux:
        puissance_requise = ref["panneau_puissance_w"]
        alea3 = calculer_options_panneaux(puissance_requise, panneaux, energies_tranche)

        # Calculer les revenus de vente si les prix sont disponibles
        if prix_energie:
            for opt in alea3:
                e_jour = opt["energie_vendable_jour_wh"]
                e_soir = opt["energie_vendable_soir_wh"]
                opt["revenu_jour_ouvrable"] = round(e_jour * prix_energie["prix_jour_ouvrable"], 2)
                opt["revenu_soir_ouvrable"] = round(e_soir * prix_energie["prix_soir_ouvrable"], 2)
                opt["revenu_total_ouvrable"] = round(opt["revenu_jour_ouvrable"] + opt["revenu_soir_ouvrable"], 2)
                opt["revenu_jour_weekend"] = round(e_jour * prix_energie["prix_jour_weekend"], 2)
                opt["revenu_soir_weekend"] = round(e_soir * prix_energie["prix_soir_weekend"], 2)
                opt["revenu_total_weekend"] = round(opt["revenu_jour_weekend"] + opt["revenu_soir_weekend"], 2)

    # --- 6. Statut global ---
    if autonomie_ok and ref["recharge_ok"]:
        statut = "OK"
        message = "Le système est correctement dimensionné."
    elif not autonomie_ok:
        statut = "INSUFFISANT"
        message = "La batterie est insuffisante pour la nuit."
    else:
        temps_rech = ref["temps_recharge_h"]
        statut = "ATTENTION"
        if temps_rech is not None:
            message = f"La recharge prend {temps_rech:.1f}h, dépasse les {HEURES_SOLEIL}h disponibles."
        else:
            message = "Impossible de recharger la batterie (puissance insuffisante)."

    par_tranche = separer_par_tranche(appareils)

    return {
        "statut": statut,
        "message": message,

        # Consommation
        "energie_jour_wh": round(energie_jour, 2),
        "energie_nuit_wh": round(energie_nuit, 2),
        "energie_totale_wh": round(energie_totale, 2),
        "detail_tranches": {k: round(v, 2) for k, v in energies_tranche.items()},

        # Batterie
        "batterie_capacite_wh": round(capacite_batterie, 2),
        "batterie_autonomie_ok": autonomie_ok,
        "batterie_marge_pct": marge_pct,

        # Panneau (référence 40%)
        "panneau_puissance_w": ref["panneau_puissance_w"],
        "panneau_production_reelle_w": ref["panneau_production_reelle_w"],
        "panneau_production_journaliere_wh": ref["panneau_production_journaliere_wh"],

        # Recharge (référence 40%)
        "puissance_recharge_w": ref["puissance_recharge_w"],
        "temps_recharge_h": ref["temps_recharge_h"],
        "recharge_ok": ref["recharge_ok"],

        # Appareils
        "appareils_matin": len(par_tranche.get("matin", [])),
        "appareils_soir": len(par_tranche.get("soir", [])),
        "appareils_nuit": len(par_tranche.get("nuit", [])),
        "nb_appareils_total": len(appareils),

        # ALEA 1
        "alea1": alea1_resultats,

        # ALEA 2
        "alea2": alea2,

        # ALEA 3
        "alea3": alea3,

        # Prix énergie
        "prix_energie": prix_energie or {},
    }
