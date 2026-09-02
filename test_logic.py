"""Script de test rapide de la logique métier (sans base de données)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.appareil import Appareil
from services.consommation_service import (
    calculer_energie, separer_par_tranche,
    calculer_total_jour, calculer_total_nuit
)
from services.batterie_service import calculer_capacite_batterie, temps_charge
from services.panneau_service import calculer_puissance_panneau, production_reelle
from services.simulation_service import simuler_journee
from utils.conversions import formater_energie, formater_puissance

# Appareils de test
appareils = [
    Appareil("Lampe salon", 15, 5, "nuit"),
    Appareil("Lampe chambre", 10, 4, "nuit"),
    Appareil("Ventilateur", 50, 8, "matin"),
    Appareil("Refrigerateur", 100, 11, "matin"),
    Appareil("Television", 80, 3, "nuit"),
    Appareil("Chargeur telephone", 10, 2, "matin"),
    Appareil("Radio", 15, 6, "matin"),
    Appareil("Lampe exterieure", 20, 2, "soir"),
]

print("=== TEST MODELE ===")
for a in appareils:
    print(f"  {a}")

print("\n=== TEST CONSOMMATION ===")
e_jour = calculer_total_jour(appareils)
e_nuit = calculer_total_nuit(appareils)
print(f"  Energie jour: {formater_energie(e_jour)}")
print(f"  Energie nuit: {formater_energie(e_nuit)}")

print("\n=== TEST BATTERIE ===")
cap = calculer_capacite_batterie(e_nuit)
print(f"  Capacite batterie: {formater_energie(cap)}")
t = temps_charge(cap, 200)
print(f"  Temps de charge a 200W: {t:.1f}h")

print("\n=== TEST PANNEAU ===")
p = calculer_puissance_panneau(e_jour, e_nuit)
print(f"  Puissance panneau necessaire: {formater_puissance(p)}")
print(f"  Production reelle: {formater_puissance(production_reelle(p))}")

print("\n=== TEST SIMULATION COMPLETE ===")
result = simuler_journee(appareils)
for k, v in result.items():
    print(f"  {k}: {v}")

print("\n=== TOUS LES TESTS OK ===")
