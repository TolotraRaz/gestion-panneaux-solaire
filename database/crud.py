"""
Module CRUD pour les appareils et résultats.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.connection import get_connection
from models.appareil import Appareil


# ==========================================
# CRUD Appareils
# ==========================================

def insert_appareil(nom, puissance_w, heure_debut, heure_fin):
    """Insère un nouvel appareil dans la base de données."""
    # Créer l'appareil pour valider et déduire la tranche
    appareil = Appareil(nom, puissance_w, heure_debut, heure_fin)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appareils (nom, puissance_w, heure_debut, heure_fin, tranche) VALUES (?, ?, ?, ?, ?)",
        (nom, puissance_w, appareil.heure_debut, appareil.heure_fin, appareil.tranche)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_appareils():
    """Récupère tous les appareils de la base de données."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, puissance_w, heure_debut, heure_fin FROM appareils")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    appareils = []
    for row in rows:
        appareils.append(Appareil(
            id=row[0],
            nom=row[1],
            puissance_w=row[2],
            heure_debut=row[3],
            heure_fin=row[4]
        ))
    return appareils


def get_appareil_by_id(appareil_id):
    """Récupère un appareil par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nom, puissance_w, heure_debut, heure_fin FROM appareils WHERE id = ?",
        (appareil_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return Appareil(
            id=row[0],
            nom=row[1],
            puissance_w=row[2],
            heure_debut=row[3],
            heure_fin=row[4]
        )
    return None


def update_appareil(appareil_id, nom=None, puissance_w=None, heure_debut=None, heure_fin=None):
    """Met à jour un appareil existant."""
    appareil = get_appareil_by_id(appareil_id)
    if not appareil:
        return False

    nom = nom or appareil.nom
    puissance_w = puissance_w or appareil.puissance_w
    heure_debut = heure_debut if heure_debut is not None else appareil.heure_debut
    heure_fin = heure_fin if heure_fin is not None else appareil.heure_fin

    # Recréer pour re-déduire la tranche
    updated = Appareil(nom, puissance_w, heure_debut, heure_fin)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appareils SET nom=?, puissance_w=?, heure_debut=?, heure_fin=?, tranche=? WHERE id=?",
        (nom, puissance_w, updated.heure_debut, updated.heure_fin, updated.tranche, appareil_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True


def delete_appareil(appareil_id):
    """Supprime un appareil par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appareils WHERE id = ?", (appareil_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


# ==========================================
# CRUD Résultats
# ==========================================

def save_resultat(energie_jour, energie_nuit, batterie_wh, panneau_w):
    """Sauvegarde un résultat de simulation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resultats (energie_jour, energie_nuit, batterie_wh, panneau_w) VALUES (?, ?, ?, ?)",
        (energie_jour, energie_nuit, batterie_wh, panneau_w)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_resultats():
    """Récupère tous les résultats de simulation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, energie_jour, energie_nuit, batterie_wh, panneau_w, date_calcul FROM resultats ORDER BY date_calcul DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ==========================================
# CRUD Panneaux Solaires (Alea 3)
# ==========================================

def insert_panneau(nom, energie_unitaire_w, pourcentage, prix_unitaire):
    """Insère un nouveau type de panneau solaire."""
    from models.panneau_solaire import PanneauSolaire
    # Valider via le modèle
    PanneauSolaire(nom, energie_unitaire_w, pourcentage, prix_unitaire)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO panneaux_solaires (nom, energie_unitaire_w, pourcentage, prix_unitaire) VALUES (?, ?, ?, ?)",
        (nom, float(energie_unitaire_w), float(pourcentage), float(prix_unitaire))
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_panneaux():
    """Récupère tous les panneaux solaires."""
    from models.panneau_solaire import PanneauSolaire
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, energie_unitaire_w, pourcentage, prix_unitaire FROM panneaux_solaires")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    panneaux = []
    for row in rows:
        panneaux.append(PanneauSolaire(
            id=row[0],
            nom=row[1],
            energie_unitaire_w=row[2],
            pourcentage=row[3],
            prix_unitaire=row[4]
        ))
    return panneaux


def delete_panneau(panneau_id):
    """Supprime un panneau par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM panneaux_solaires WHERE id = ?", (panneau_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


# ==========================================
# CRUD Prix Énergie
# ==========================================

def get_prix_energie():
    """Récupère les prix d'achat de l'énergie (ligne unique)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prix_jour_ouvrable, prix_soir_ouvrable, prix_jour_weekend, prix_soir_weekend "
        "FROM prix_energie"
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return {
            "prix_jour_ouvrable": row[0],
            "prix_soir_ouvrable": row[1],
            "prix_jour_weekend": row[2],
            "prix_soir_weekend": row[3],
        }
    # Si aucune ligne, insérer les défauts et retourner
    defaults = {
        "prix_jour_ouvrable": 50,
        "prix_soir_ouvrable": 80,
        "prix_jour_weekend": 70,
        "prix_soir_weekend": 100,
    }
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prix_energie (prix_jour_ouvrable, prix_soir_ouvrable, prix_jour_weekend, prix_soir_weekend) "
        "VALUES (?, ?, ?, ?)",
        (defaults["prix_jour_ouvrable"], defaults["prix_soir_ouvrable"],
         defaults["prix_jour_weekend"], defaults["prix_soir_weekend"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return defaults


def update_prix_energie(prix_jour_ouvrable, prix_soir_ouvrable, prix_jour_weekend, prix_soir_weekend):
    """Met à jour les prix d'achat de l'énergie."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE prix_energie SET "
        "prix_jour_ouvrable=?, prix_soir_ouvrable=?, prix_jour_weekend=?, prix_soir_weekend=?",
        (float(prix_jour_ouvrable), float(prix_soir_ouvrable),
         float(prix_jour_weekend), float(prix_soir_weekend))
    )
    conn.commit()
    cursor.close()
    conn.close()
