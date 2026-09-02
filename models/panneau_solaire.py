"""
Modèle PanneauSolaire : représente un type de panneau solaire disponible à l'achat.
"""


class PanneauSolaire:
    """
    Représente un type de panneau solaire avec ses caractéristiques.

    Attributs:
        id: Identifiant en base de données
        nom: Nom du panneau (ex: "P1", "SunMax 400")
        energie_unitaire_w: Puissance nominale d'un panneau (W)
        pourcentage: Rendement réel en % (ex: 40 signifie 40%)
        prix_unitaire: Prix d'un panneau (Ar)
    """

    def __init__(self, nom, energie_unitaire_w, pourcentage, prix_unitaire, id=None):
        self.id = id
        self.nom = nom
        self.energie_unitaire_w = float(energie_unitaire_w)
        self.pourcentage = float(pourcentage)
        self.prix_unitaire = float(prix_unitaire)

        if self.pourcentage <= 0 or self.pourcentage > 100:
            raise ValueError(f"Pourcentage invalide: {self.pourcentage} (1-100 attendu)")
        if self.energie_unitaire_w <= 0:
            raise ValueError(f"Énergie unitaire invalide: {self.energie_unitaire_w}")
        if self.prix_unitaire <= 0:
            raise ValueError(f"Prix unitaire invalide: {self.prix_unitaire}")

    @property
    def puissance_reelle_w(self):
        """Puissance réelle d'un panneau = énergie unitaire × pourcentage / 100."""
        return self.energie_unitaire_w * self.pourcentage / 100

    def __repr__(self):
        return (
            f"PanneauSolaire(id={self.id}, nom='{self.nom}', "
            f"energie={self.energie_unitaire_w}W, rendement={self.pourcentage}%, "
            f"réel={self.puissance_reelle_w}W, prix={self.prix_unitaire} Ar)"
        )

    def __str__(self):
        return (
            f"{self.nom} — {self.energie_unitaire_w}W nominal, "
            f"{self.pourcentage}% rendement → {self.puissance_reelle_w}W réel, "
            f"{self.prix_unitaire} Ar/unité"
        )
