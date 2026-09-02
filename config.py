# Configuration du projet Solaire

# SQL Server
DB_SERVER = r"localhost\SQLEXPRESS"
DB_NAME = "SolaireDB"
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"
DB_TRUSTED_CONNECTION = "yes"

# Paramètres solaires
RENDEMENT_PANNEAU = 0.4          # 40% de rendement réel
PRODUCTION_SOIR = 0.5            # 50% de production entre 17h-19h
MARGE_BATTERIE = 1.5             # +50% marge de sécurité
HEURES_SOLEIL = 11               # 06h → 17h = 11 heures

# Tranches horaires
TRANCHE_MATIN = "matin"         # 06h → 17h
TRANCHE_SOIR = "soir"           # 17h → 19h
TRANCHE_NUIT = "nuit"           # 19h → 06h
