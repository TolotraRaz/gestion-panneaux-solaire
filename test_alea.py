"""Test complet du nouveau modèle heure_debut/heure_fin."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.appareil import Appareil
from services.simulation_service import simuler_journee

apps = [
    Appareil("Frigo", 800, 8, 11, id=1),         # matin, 3h
    Appareil("Ordi", 65, 10, 12, id=2),           # matin, 2h — chevauche frigo 10h-11h
    Appareil("TV", 65, 17, 18, id=3),             # soir, 1h
    Appareil("Lampe salon", 15, 19, 0, id=4),     # nuit, 5h
    Appareil("Ventilateur", 50, 8, 16, id=5),     # matin, 8h
]

print("=== TEST MODELE ===")
for a in apps:
    print(f"  {a}")
    print(f"    Actif a 10h: {a.est_actif_a(10)}, Actif a 20h: {a.est_actif_a(20)}")

print("\n=== TEST SIMULATION ===")
r = simuler_journee(apps)
print(f"  Statut: {r['statut']}")
print(f"  Energie jour: {r['energie_jour_wh']} Wh")
print(f"  Energie nuit: {r['energie_nuit_wh']} Wh")

print("\n=== ALEA 1 ===")
for a1 in r["alea1"]:
    print(f"  Rendement {a1['rendement_pct']}%: panneau={a1['panneau_puissance_w']}W")

print("\n=== ALEA 2 (heure par heure) ===")
a2 = r["alea2"]
print(f"  Pic: {a2['pic_w']}W a {a2['heure_pic']}h")
print(f"  Convertisseur: {a2['convertisseur_w']}W")
print(f"  Appareils au pic:")
for ap in a2["appareils_pic"]:
    print(f"    - {ap['nom']} ({ap['horaire']}) {ap['puissance_w']}W")
print(f"  Detail horaire:")
for h in range(24):
    p = a2["detail_par_heure"].get(h, 0)
    if p > 0:
        marker = " <-- PIC" if h == a2["heure_pic"] else ""
        print(f"    {h:2d}h: {p}W{marker}")

print("\n=== OK ===")
