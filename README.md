# Système de Gestion d'Énergie Solaire

## Description

Ce projet est une application Python permettant de **simuler et dimensionner un système d'énergie solaire** à partir de la consommation électrique d'un ensemble d'appareils.

L'application permet notamment de :

* gérer les appareils électriques ;
* calculer leur consommation énergétique ;
* répartir la consommation selon différentes tranches horaires ;
* dimensionner la capacité nécessaire de la batterie ;
* calculer la puissance nécessaire des panneaux solaires ;
* vérifier l'autonomie de la batterie pendant la nuit ;
* calculer le temps nécessaire pour recharger la batterie ;
* déterminer le pic de consommation ;
* comparer différents rendements de panneaux ;
* comparer plusieurs modèles de panneaux solaires ;
* calculer le nombre de panneaux nécessaires ;
* estimer le coût d'installation ;
* calculer l'énergie éventuellement disponible à la vente ;
* sauvegarder les résultats des simulations dans une base de données SQL Server.

L'application possède une **interface graphique développée avec Tkinter** et utilise **SQL Server** pour stocker les données.

---

## Objectifs du projet

L'objectif principal est de fournir un outil permettant d'estimer les besoins d'une installation photovoltaïque à partir des habitudes de consommation électrique.

Le fonctionnement général est :

```text
Appareils électriques
        ↓
Calcul de la consommation
        ↓
Répartition par tranche horaire
        ↓
Calcul de l'énergie nécessaire
        ↓
Dimensionnement de la batterie
        ↓
Dimensionnement des panneaux
        ↓
Calcul du pic de consommation
        ↓
Comparaison des solutions
        ↓
Simulation finale
        ↓
Sauvegarde des résultats
```

---

## Technologies utilisées

### Langage

* **Python 3**

### Interface graphique

* **Tkinter**
* **ttk**

### Base de données

* **Microsoft SQL Server**
* **SQL Server Express**
* **pyodbc**

### Tests

* Tests Python avec les scripts intégrés au projet.

---

## Structure du projet

```text
codes/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── connection.py
│   ├── crud.py
│   ├── init_db.sql
│   └── __init__.py
│
├── models/
│   ├── appareil.py
│   ├── panneau_solaire.py
│   └── __init__.py
│
├── services/
│   ├── consommation_service.py
│   ├── batterie_service.py
│   ├── panneau_service.py
│   ├── simulation_service.py
│   ├── alea3_service.py
│   └── __init__.py
│
├── utils/
│   ├── conversions.py
│   └── __init__.py
│
├── test_logic.py
├── test_alea.py
└── drop_old_table.py
```

---

## Description des dossiers

### `models/`

Contient les classes représentant les objets principaux de l'application.

#### `appareil.py`

Représente un appareil électrique.

Un appareil possède notamment :

* son nom ;
* sa puissance en watts ;
* son heure de début d'utilisation ;
* son heure de fin ;
* sa tranche horaire.

Il permet également de calculer la durée d'utilisation et l'énergie consommée.

#### `panneau_solaire.py`

Représente un panneau solaire et permet notamment de déterminer sa puissance réelle selon son rendement.

---

### `services/`

Contient la logique métier de l'application.

#### `consommation_service.py`

Responsable du calcul de la consommation électrique :

* consommation du matin ;
* consommation du soir ;
* consommation de nuit ;
* consommation totale.

#### `batterie_service.py`

Permet de :

* calculer la capacité nécessaire de la batterie ;
* vérifier l'autonomie pendant la nuit ;
* calculer le temps de recharge ;
* vérifier si la batterie peut être correctement rechargée.

#### `panneau_service.py`

Permet de :

* calculer la puissance solaire nécessaire ;
* calculer la production réelle ;
* déterminer le nombre de panneaux nécessaires ;
* comparer différentes configurations.

#### `simulation_service.py`

Contient la logique de simulation générale.

Il permet notamment de calculer :

* le besoin énergétique ;
* le dimensionnement de la batterie ;
* le dimensionnement solaire ;
* le pic de consommation ;
* le convertisseur nécessaire ;
* le statut final de la simulation.

#### `alea3_service.py`

Permet de comparer différents modèles de panneaux solaires en fonction de :

* leur puissance ;
* leur rendement ;
* leur prix ;
* leur production ;
* leur nombre nécessaire.

---

### `database/`

Contient tout ce qui concerne la base de données.

#### `connection.py`

Gère la connexion à SQL Server et l'initialisation de la base.

#### `crud.py`

Contient les opérations CRUD :

```text
Create  → Ajouter
Read    → Lire
Update  → Modifier
Delete  → Supprimer
```

#### `init_db.sql`

Contient les commandes SQL nécessaires à la création des tables.

---

### `utils/`

Contient des fonctions utilitaires, notamment pour les conversions et le formatage des données.

---

## Base de données

Le projet utilise une base de données SQL Server appelée :

```text
SolaireDB
```

La connexion est configurée pour utiliser :

```text
localhost\SQLEXPRESS
```

### Tables principales

#### `appareils`

Stocke les appareils électriques.

```text
id
nom
puissance_w
heure_debut
heure_fin
tranche
```

#### `panneaux_solaires`

Stocke les différents modèles de panneaux.

```text
id
nom
energie_unitaire_w
pourcentage
prix_unitaire
```

#### `resultats`

Stocke les résultats des simulations.

```text
id
energie_jour
energie_nuit
batterie_wh
panneau_w
date_calcul
```

#### `prix_energie`

Stocke les différents prix de l'énergie.

```text
prix_jour_ouvrable
prix_soir_ouvrable
prix_jour_weekend
prix_soir_weekend
```

---

# Fonctionnement

## 1. Ajout des appareils

L'utilisateur peut enregistrer les appareils électriques utilisés dans le logement.

Par exemple :

```text
Télévision
Puissance : 80 W
Début : 19h
Fin : 22h
```

Le système détermine automatiquement la tranche horaire correspondante.

---

## 2. Calcul de la consommation

La consommation est calculée à partir de la formule :

```text
Énergie (Wh) = Puissance (W) × Durée (h)
```

### Exemple

Pour un appareil de 100 W utilisé pendant 5 heures :

```text
100 × 5 = 500 Wh
```

La consommation est donc de :

```text
500 Wh
```

---

## 3. Répartition des consommations

Le projet utilise trois tranches horaires :

| Tranche | Horaire   |
| ------- | --------- |
| Matin   | 06h → 17h |
| Soir    | 17h → 19h |
| Nuit    | 19h → 06h |

La consommation du soir est répartie entre la production solaire et la batterie.

---

## 4. Dimensionnement de la batterie

La batterie doit principalement couvrir les besoins énergétiques nocturnes.

Une marge de sécurité est appliquée :

```text
Capacité batterie = Consommation nuit × 1,5
```

### Exemple

Si la consommation nocturne est de :

```text
1 000 Wh
```

la capacité calculée est :

```text
1 000 × 1,5 = 1 500 Wh
```

La batterie nécessaire est donc de :

```text
1,5 kWh
```

---

## 5. Dimensionnement des panneaux

Le système utilise notamment :

```text
Heures de soleil = 11 h
Rendement = 40 %
```

La puissance solaire nécessaire est calculée à partir du besoin énergétique total.

Formule :

```text
Puissance panneaux =
Énergie nécessaire / (Heures de soleil × Rendement)
```

Le résultat permet de déterminer la puissance solaire théorique nécessaire.

---

## 6. Puissance réelle d'un panneau

La puissance réelle dépend du rendement.

Formule :

```text
Puissance réelle =
Puissance nominale × Rendement
```

### Exemple

Pour un panneau de :

```text
500 W
```

avec un rendement de :

```text
40 %
```

on obtient :

```text
500 × 0,40 = 200 W
```

---

## 7. Nombre de panneaux nécessaires

Une fois la puissance réelle d'un panneau connue, le programme détermine le nombre de panneaux nécessaires.

Le nombre est arrondi à l'entier supérieur.

Exemple :

```text
Besoin : 700 W
Production réelle d'un panneau : 80 W
```

Calcul :

```text
700 / 80 = 8,75
```

Le programme retient donc :

```text
9 panneaux
```

---

# Vérification de la batterie

Le programme vérifie si la batterie possède suffisamment d'énergie pour couvrir les besoins nocturnes.

Il calcule également le temps nécessaire pour recharger la batterie.

Formule :

```text
Temps de recharge =
Capacité batterie / Puissance disponible
```

Le résultat est ensuite comparé au nombre d'heures de soleil disponibles.

Le système peut ainsi déterminer différents statuts :

```text
OK
INSUFFISANT
ATTENTION
```

---

# Calcul du pic de consommation

Le système analyse la consommation heure par heure.

```text
00h
01h
02h
...
23h
```

Pour chaque heure, il additionne la puissance des appareils actifs.

La valeur maximale obtenue correspond au :

```text
PIC DE CONSOMMATION
```

Ce pic est notamment utilisé pour déterminer la puissance nécessaire du convertisseur.

La règle utilisée dans le projet est :

```text
Puissance convertisseur = Pic de consommation × 2
```

---

# ALEA 1 — Rendement des panneaux

Cette partie permet de comparer différents rendements.

Le projet teste notamment :

```text
40 %
30 %
```

Le même besoin énergétique est calculé avec les deux rendements.

Cela permet d'observer l'influence du rendement sur la puissance de panneaux nécessaire.

---

# ALEA 2 — Pic de consommation

Cette partie permet de simuler la consommation des appareils sur les 24 heures de la journée.

Elle prend en compte les horaires de fonctionnement des appareils afin de trouver l'heure à laquelle la consommation est maximale.

Le résultat permet ensuite de dimensionner le convertisseur.

---

# ALEA 3 — Comparaison des panneaux

Cette partie compare plusieurs modèles de panneaux solaires.

Les critères pris en compte sont notamment :

* puissance nominale ;
* rendement ;
* puissance réelle ;
* nombre de panneaux nécessaires ;
* prix unitaire ;
* coût total ;
* énergie produite ;
* énergie disponible à la vente.

Cela permet de comparer différentes configurations d'installation.

---

# Interface utilisateur

L'application possède une interface graphique développée avec **Tkinter**.

Le fichier principal est :

```text
main.py
```

L'interface permet d'accéder aux fonctionnalités de gestion et de simulation.

Les données peuvent notamment être affichées sous forme de tableaux grâce aux composants `ttk`.

---

# Installation

## Prérequis

Avant de lancer le projet, installer :

* Python 3 ;
* Microsoft SQL Server ou SQL Server Express ;
* ODBC Driver pour SQL Server ;
* `pip`.

Vérifier l'installation de Python :

```bash
python --version
```

Vérifier `pip` :

```bash
pip --version
```

---

## Installation des dépendances

Depuis le dossier du projet :

```bash
pip install -r requirements.txt
```

La bibliothèque principale utilisée pour la connexion à SQL Server est :

```text
pyodbc
```

---

# Configuration de SQL Server

Vérifier que SQL Server Express est installé et démarré.

Le projet utilise par défaut l'instance :

```text
localhost\SQLEXPRESS
```

La configuration de connexion se trouve dans :

```text
database/connection.py
```

Si l'instance SQL Server est différente sur votre ordinateur, modifier la configuration correspondante.

---

# Lancement du projet

Depuis la racine du projet :

```bash
python main.py
```

L'interface graphique devrait alors s'ouvrir.

---

# Exécution des tests

Pour tester la logique principale :

```bash
python test_logic.py
```

Pour tester les fonctionnalités ALEA :

```bash
python test_alea.py
```

---

# Exemple de scénario

Un scénario typique est le suivant :

```text
1. Ajouter les appareils électriques
             ↓
2. Définir leur puissance
             ↓
3. Définir leurs horaires d'utilisation
             ↓
4. Calculer leur consommation
             ↓
5. Répartir la consommation
   matin / soir / nuit
             ↓
6. Calculer la batterie
             ↓
7. Calculer la puissance solaire
             ↓
8. Calculer le pic de consommation
             ↓
9. Dimensionner le convertisseur
             ↓
10. Comparer les panneaux
             ↓
11. Afficher les résultats
             ↓
12. Enregistrer la simulation
```

---

# Principales formules

### Consommation

```text
E = P × t
```

où :

* `E` = énergie en Wh ;
* `P` = puissance en W ;
* `t` = durée en heures.

### Batterie

```text
Batterie = Consommation nuit × 1,5
```

### Puissance solaire

```text
Panneaux =
Énergie nécessaire / (Heures soleil × Rendement)
```

### Puissance réelle d'un panneau

```text
Puissance réelle =
Puissance nominale × Rendement
```

### Temps de recharge

```text
Temps recharge =
Capacité batterie / Puissance disponible
```

### Convertisseur

```text
Convertisseur =
Pic de consommation × 2
```

---

# Organisation du code

Le projet suit une séparation entre :

```text
Interface
   ↓
Services
   ↓
Models
   ↓
Database
```

Cette organisation permet de séparer :

* l'affichage ;
* les calculs ;
* les modèles de données ;
* l'accès à la base de données.

Ainsi, les calculs peuvent être testés indépendamment de l'interface graphique.

---

# Tests

Les fichiers :

```text
test_logic.py
test_alea.py
```

permettent de vérifier le comportement de différentes parties du programme.

Les tests permettent notamment de vérifier :

* le calcul de la durée ;
* le calcul de l'énergie ;
* la répartition par tranche ;
* le dimensionnement de la batterie ;
* le dimensionnement solaire ;
* le calcul du pic ;
* les comparaisons de rendement ;
* la comparaison des panneaux.

---

# Auteur

Projet réalisé dans le cadre d'un projet académique.

---

# Licence

Projet académique destiné à l'apprentissage et à la démonstration du dimensionnement d'un système d'énergie solaire.
