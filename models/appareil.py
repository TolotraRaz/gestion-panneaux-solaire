"""
Modèle Appareil : représente un appareil électrique avec ses heures d'utilisation.
"""


class Appareil:
    """
    Représente un appareil avec sa consommation énergétique.
    
    Attributs:
        id: Identifiant en base de données
        nom: Nom de l'appareil
        puissance_w: Puissance en watts (W)
        heure_debut: Heure de début d'utilisation (0-23)
        heure_fin: Heure de fin d'utilisation (0-23)
        tranche: Tranche horaire principale (déduite automatiquement)
    """

    TRANCHES_VALIDES = ("matin", "soir", "nuit")

    def __init__(self, nom, puissance_w, heure_debut, heure_fin, id=None):
        self.id = id
        self.nom = nom
        self.puissance_w = float(puissance_w)
        self.heure_debut = int(heure_debut)
        self.heure_fin = int(heure_fin)

        # Valider les heures (0-23)
        if not (0 <= self.heure_debut <= 23):
            raise ValueError(f"Heure de début invalide: {self.heure_debut} (0-23 attendu)")
        if not (0 <= self.heure_fin <= 23):
            raise ValueError(f"Heure de fin invalide: {self.heure_fin} (0-23 attendu)")

        # Déduire la tranche horaire principale (basée sur heure_debut)
        self.tranche = self._deduire_tranche()

    def _deduire_tranche(self):
        """Déduit la tranche horaire principale depuis heure_debut."""
        if 6 <= self.heure_debut < 17:
            return "matin"
        elif 17 <= self.heure_debut < 19:
            return "soir"
        else:
            return "nuit"

    def duree_h(self):
        """Calcule la durée d'utilisation en heures."""
        if self.heure_fin > self.heure_debut:
            return self.heure_fin - self.heure_debut
        elif self.heure_fin < self.heure_debut:
            # Passage par minuit (ex: 20h -> 5h = 9h)
            return (24 - self.heure_debut) + self.heure_fin
        else:
            # Si début == fin, c'est 24h
            return 24

    def energie_wh(self):
        """Calcule l'énergie consommée en Wh."""
        return self.puissance_w * self.duree_h()

    def est_actif_a(self, heure):
        """Vérifie si l'appareil est actif à une heure donnée (0-23)."""
        if self.heure_fin > self.heure_debut:
            return self.heure_debut <= heure < self.heure_fin
        elif self.heure_fin < self.heure_debut:
            # Passage par minuit
            return heure >= self.heure_debut or heure < self.heure_fin
        else:
            # 24h
            return True

    def heures_actives(self):
        """Retourne la liste des heures où l'appareil est actif."""
        return [h for h in range(24) if self.est_actif_a(h)]

    def __repr__(self):
        return (
            f"Appareil(id={self.id}, nom='{self.nom}', "
            f"puissance={self.puissance_w}W, {self.heure_debut}h-{self.heure_fin}h, "
            f"tranche='{self.tranche}', energie={self.energie_wh()}Wh)"
        )

    def __str__(self):
        return (
            f"{self.nom} -- {self.puissance_w}W x "
            f"{self.heure_debut}h->{self.heure_fin}h "
            f"({self.duree_h()}h) = {self.energie_wh()}Wh [{self.tranche}]"
        )
