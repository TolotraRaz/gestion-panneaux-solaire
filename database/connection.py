"""
Module de connexion à SQL Server.
"""
import pyodbc
import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def get_connection(database=None):
    """
    Établit et retourne une connexion à SQL Server.
    
    Args:
        database: Nom de la base de données. Si None, utilise config.DB_NAME.
                  Passer "" pour se connecter sans spécifier de base (utile pour CREATE DATABASE).
    
    Returns:
        pyodbc.Connection: Connexion à SQL Server.
    """
    db_name = config.DB_NAME if database is None else database

    conn_str = (
        f"DRIVER={config.DB_DRIVER};"
        f"SERVER={config.DB_SERVER};"
        f"Trusted_Connection={config.DB_TRUSTED_CONNECTION};"
    )

    if db_name:
        conn_str += f"DATABASE={db_name};"

    return pyodbc.connect(conn_str)


def init_database():
    """
    Initialise la base de données et les tables.
    Crée la base SolaireDB si elle n'existe pas, puis crée les tables.
    """
    # Étape 1 : Créer la base de données si nécessaire
    conn = get_connection(database="")
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{config.DB_NAME}')
        BEGIN
            CREATE DATABASE {config.DB_NAME};
        END
    """)
    cursor.close()
    conn.close()

    # Étape 2 : Créer les tables
    conn = get_connection()
    cursor = conn.cursor()

    # Table appareils
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'appareils')
        BEGIN
            CREATE TABLE appareils (
                id INT PRIMARY KEY IDENTITY(1,1),
                nom VARCHAR(100) NOT NULL,
                puissance_w FLOAT NOT NULL,
                heure_debut INT NOT NULL CHECK (heure_debut >= 0 AND heure_debut <= 23),
                heure_fin INT NOT NULL CHECK (heure_fin >= 0 AND heure_fin <= 23),
                tranche VARCHAR(20) NOT NULL CHECK (tranche IN ('matin', 'soir', 'nuit'))
            );
        END
    """)

    # Table resultats
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'resultats')
        BEGIN
            CREATE TABLE resultats (
                id INT PRIMARY KEY IDENTITY(1,1),
                energie_jour FLOAT NOT NULL,
                energie_nuit FLOAT NOT NULL,
                batterie_wh FLOAT NOT NULL,
                panneau_w FLOAT NOT NULL,
                date_calcul DATETIME DEFAULT GETDATE()
            );
        END
    """)

    # Table panneaux_solaires (Alea 3)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'panneaux_solaires')
        BEGIN
            CREATE TABLE panneaux_solaires (
                id INT PRIMARY KEY IDENTITY(1,1),
                nom VARCHAR(100) NOT NULL,
                energie_unitaire_w FLOAT NOT NULL,
                pourcentage FLOAT NOT NULL,
                prix_unitaire FLOAT NOT NULL
            );
        END
    """)

    # Table prix_energie (prix d'achat énergie par tranche/jour)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prix_energie')
        BEGIN
            CREATE TABLE prix_energie (
                id INT PRIMARY KEY IDENTITY(1,1),
                prix_jour_ouvrable FLOAT NOT NULL DEFAULT 50,
                prix_soir_ouvrable FLOAT NOT NULL DEFAULT 80,
                prix_jour_weekend FLOAT NOT NULL DEFAULT 70,
                prix_soir_weekend FLOAT NOT NULL DEFAULT 100
            );
        END
    """)

    # Insérer les prix par défaut si la table est vide
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM prix_energie)
        BEGIN
            INSERT INTO prix_energie (prix_jour_ouvrable, prix_soir_ouvrable, prix_jour_weekend, prix_soir_weekend)
            VALUES (50, 80, 70, 100);
        END
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Base de données et tables initialisées avec succès.")


if __name__ == "__main__":
    init_database()
