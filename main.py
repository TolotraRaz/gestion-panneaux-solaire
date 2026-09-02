"""
Interface graphique (Tkinter) pour le système de gestion d'énergie solaire.
Fenêtrage complet avec navigation par onglets, formulaires, tableaux et résultats visuels.
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_database
from database.crud import (
    insert_appareil,
    get_all_appareils,
    get_appareil_by_id,
    delete_appareil,
    save_resultat,
    get_all_resultats,
    insert_panneau,
    get_all_panneaux,
    delete_panneau,
    get_prix_energie,
    update_prix_energie
)
from services.simulation_service import simuler_journee
from utils.conversions import formater_energie, formater_puissance


# ==========================================
# Palette de couleurs
# ==========================================
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_sidebar": "#16213e",
    "bg_card": "#0f3460",
    "bg_input": "#1a1a3e",
    "accent": "#e94560",
    "accent_hover": "#ff6b81",
    "solar_yellow": "#f5a623",
    "solar_orange": "#f39c12",
    "battery_green": "#27ae60",
    "battery_blue": "#2980b9",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0c0",
    "text_muted": "#6c6c8a",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "border": "#2a2a4a",
}


# ==========================================
# Application principale
# ==========================================
class SolaireApp(tk.Tk):
    """Fenêtre principale de l'application Solaire."""

    def __init__(self):
        super().__init__()

        self.title("☀️ Système de Gestion d'Énergie Solaire")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg_dark"])

        # Binding global (pour cleanup)
        self._global_bindings = []

        # Polices
        self.font_title = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_heading = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_subheading = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_body = tkfont.Font(family="Segoe UI", size=10)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_menu = tkfont.Font(family="Segoe UI", size=11)
        self.font_big_value = tkfont.Font(family="Segoe UI", size=22, weight="bold")

        # Style ttk
        self._setup_styles()

        # Initialiser la DB
        self._init_db()

        # Layout principal
        self._build_sidebar()
        self._build_main_area()

        # Afficher la page d'accueil
        self.show_page("accueil")

    def _setup_styles(self):
        """Configure les styles ttk pour les Treeview et scrollbars."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Dark.Treeview",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["text_primary"],
                        fieldbackground=COLORS["bg_dark"],
                        borderwidth=0,
                        rowheight=30,
                        font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading",
                        background=COLORS["bg_card"],
                        foreground=COLORS["solar_yellow"],
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("Dark.Treeview",
                  background=[("selected", COLORS["bg_card"])],
                  foreground=[("selected", COLORS["solar_yellow"])])

        style.configure("Dark.Vertical.TScrollbar",
                        background=COLORS["bg_sidebar"],
                        troughcolor=COLORS["bg_dark"],
                        borderwidth=0,
                        arrowsize=0)

    def _init_db(self):
        """Initialise la base de données au démarrage."""
        try:
            init_database()
        except Exception as e:
            messagebox.showerror(
                "Erreur de connexion",
                f"Impossible de se connecter à SQL Server :\n{e}\n\n"
                f"Vérifiez que SQL Server est démarré."
            )

    # ------------------------------------------
    # Sidebar
    # ------------------------------------------
    def _build_sidebar(self):
        """Construit la barre latérale de navigation."""
        self.sidebar = tk.Frame(self, bg=COLORS["bg_sidebar"], width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Titre application
        title_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        title_frame.pack(fill=tk.X, pady=(20, 30), padx=15)

        tk.Label(title_frame, text="☀️", font=("Segoe UI", 28),
                 bg=COLORS["bg_sidebar"], fg=COLORS["solar_yellow"]).pack()
        tk.Label(title_frame, text="SOLAIRE", font=self.font_title,
                 bg=COLORS["bg_sidebar"], fg=COLORS["text_primary"]).pack()
        tk.Label(title_frame, text="Gestion d'Énergie", font=self.font_small,
                 bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"]).pack()

        # Séparateur
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=20, pady=5)

        # Boutons du menu
        self.menu_buttons = {}
        menu_items = [
            ("accueil", "🏠  Accueil"),
            ("ajouter", "➕  Ajouter Appareil"),
            ("liste", "📋  Liste Appareils"),
            ("panneaux", "🔆  Panneaux"),
            ("parametres", "⚙️  Paramètres"),
            ("simulation", "🚀  Simulation"),
            ("historique", "📜  Historique"),
        ]

        for page_name, label in menu_items:
            btn = tk.Label(
                self.sidebar, text=label, font=self.font_menu,
                bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"],
                anchor="w", padx=20, pady=10, cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_card"], fg=COLORS["text_primary"]))
            btn.bind("<Leave>", lambda e, b=btn, p=page_name: self._menu_leave(b, p))
            btn.bind("<Button-1>", lambda e, p=page_name: self.show_page(p))
            self.menu_buttons[page_name] = btn

    def _menu_leave(self, btn, page_name):
        """Gère le survol de sortie du menu."""
        if getattr(self, '_current_page', None) == page_name:
            btn.config(bg=COLORS["bg_card"], fg=COLORS["solar_yellow"])
        else:
            btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"])

    # ------------------------------------------
    # Zone principale
    # ------------------------------------------
    def _build_main_area(self):
        """Construit la zone de contenu principal."""
        self.main_area = tk.Frame(self, bg=COLORS["bg_dark"])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.pages = {}

    def show_page(self, page_name):
        """Affiche une page dans la zone principale."""
        # Mettre à jour le style du menu
        self._current_page = page_name
        for name, btn in self.menu_buttons.items():
            if name == page_name:
                btn.config(bg=COLORS["bg_card"], fg=COLORS["solar_yellow"])
            else:
                btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"])

        # Nettoyer les bindings globaux
        for seq, func_id in self._global_bindings:
            self.unbind_all(seq)
        self._global_bindings = []

        # Effacer le contenu actuel
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Construire la page
        builders = {
            "accueil": self._page_accueil,
            "ajouter": self._page_ajouter,
            "liste": self._page_liste,
            "panneaux": self._page_panneaux,
            "parametres": self._page_parametres,
            "simulation": self._page_simulation,
            "historique": self._page_historique,
        }
        builder = builders.get(page_name)
        if builder:
            builder()

    # ------------------------------------------
    # Helpers UI
    # ------------------------------------------
    def _make_header(self, parent, title, subtitle=""):
        """Crée un en-tête de page."""
        header = tk.Frame(parent, bg=COLORS["bg_dark"])
        header.pack(fill=tk.X, padx=30, pady=(25, 15))
        tk.Label(header, text=title, font=self.font_title,
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, font=self.font_body,
                     bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=30, pady=(0, 15))
        return header

    def _make_card(self, parent, **pack_kwargs):
        """Crée un cadre style carte."""
        card = tk.Frame(parent, bg=COLORS["bg_card"],
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(padx=30, pady=8, fill=tk.X, **pack_kwargs)
        return card

    def _make_button(self, parent, text, command, color=None, width=20):
        """Crée un bouton stylisé."""
        bg = color or COLORS["accent"]
        btn = tk.Label(
            parent, text=text, font=self.font_btn,
            bg=bg, fg=COLORS["text_primary"],
            padx=20, pady=8, cursor="hand2", width=width,
            anchor="center"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent_hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def _make_entry(self, parent, label_text, row):
        """Crée un champ de saisie avec label."""
        tk.Label(parent, text=label_text, font=self.font_body,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=row, column=0, sticky="w", padx=15, pady=8)

        entry = tk.Entry(parent, font=self.font_body,
                         bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS["border"],
                         highlightcolor=COLORS["solar_yellow"])
        entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=8, ipady=4)
        return entry

    def _make_stat_card(self, parent, icon, label, value, color):
        """Crée une carte statistique compacte."""
        card = tk.Frame(parent, bg=COLORS["bg_card"],
                        highlightbackground=color, highlightthickness=2)

        tk.Label(card, text=icon, font=("Segoe UI", 24),
                 bg=COLORS["bg_card"], fg=color).pack(pady=(12, 2))
        tk.Label(card, text=value, font=self.font_big_value,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()
        tk.Label(card, text=label, font=self.font_small,
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(pady=(0, 12))
        return card

    # ------------------------------------------
    # PAGE: Accueil
    # ------------------------------------------
    def _page_accueil(self):
        """Page d'accueil avec résumé du système."""
        self._make_header(self.main_area, "Tableau de bord", "Vue d'ensemble de votre installation solaire")

        # Charger les données
        try:
            appareils = get_all_appareils()
        except Exception:
            appareils = []

        nb_total = len(appareils)
        nb_matin = sum(1 for a in appareils if a.tranche == "matin")
        nb_soir = sum(1 for a in appareils if a.tranche == "soir")
        nb_nuit = sum(1 for a in appareils if a.tranche == "nuit")
        conso_totale = sum(a.energie_wh() for a in appareils)

        # Cartes statistiques
        stats_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        stats_frame.pack(fill=tk.X, padx=30, pady=10)
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        cards_data = [
            ("⚡", "Appareils", str(nb_total), COLORS["solar_yellow"]),
            ("☀️", "Jour (Matin)", str(nb_matin), COLORS["solar_orange"]),
            ("🌙", "Nuit", str(nb_nuit), COLORS["battery_blue"]),
            ("🔋", "Conso. Totale", formater_energie(conso_totale), COLORS["battery_green"]),
        ]

        for i, (icon, label, value, color) in enumerate(cards_data):
            card = self._make_stat_card(stats_frame, icon, label, value, color)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

        # Info appareils soir
        if nb_soir > 0:
            info_card = self._make_card(self.main_area)
            tk.Label(info_card, text=f"🌆  {nb_soir} appareil(s) en tranche soir (17h-19h) — alimentés à 50% solaire / 50% batterie",
                     font=self.font_body, bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack(padx=15, pady=10)

        # Actions rapides
        actions_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        actions_frame.pack(fill=tk.X, padx=30, pady=20)

        tk.Label(actions_frame, text="Actions rapides", font=self.font_heading,
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))

        btns_frame = tk.Frame(actions_frame, bg=COLORS["bg_dark"])
        btns_frame.pack(fill=tk.X)

        self._make_button(btns_frame, "➕  Ajouter un appareil",
                          lambda: self.show_page("ajouter"),
                          color=COLORS["battery_green"], width=25).pack(side=tk.LEFT, padx=(0, 10))
        self._make_button(btns_frame, "🚀  Lancer la simulation",
                          lambda: self.show_page("simulation"),
                          color=COLORS["accent"], width=25).pack(side=tk.LEFT, padx=(0, 10))
        self._make_button(btns_frame, "📜  Voir l'historique",
                          lambda: self.show_page("historique"),
                          color=COLORS["battery_blue"], width=25).pack(side=tk.LEFT)

    # ------------------------------------------
    # PAGE: Ajouter un appareil
    # ------------------------------------------
    def _page_ajouter(self):
        """Formulaire d'ajout d'appareil."""
        self._make_header(self.main_area, "Ajouter un appareil", "Enregistrer un nouvel appareil électrique")

        card = self._make_card(self.main_area)
        card.columnconfigure(1, weight=1)

        # Champs
        self._entry_nom = self._make_entry(card, "Nom de l'appareil :", 0)
        self._entry_puissance = self._make_entry(card, "Puissance (W) :", 1)

        # Heure début (Spinbox 0-23)
        tk.Label(card, text="Heure de début (0-23) :", font=self.font_body,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=2, column=0, sticky="w", padx=15, pady=8)

        self._spin_debut = tk.Spinbox(card, from_=0, to=23, width=5,
                                       font=self.font_body,
                                       bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                                       insertbackground=COLORS["text_primary"],
                                       relief="flat", highlightthickness=1,
                                       highlightbackground=COLORS["border"],
                                       highlightcolor=COLORS["solar_yellow"])
        self._spin_debut.grid(row=2, column=1, sticky="w", padx=(5, 15), pady=8, ipady=4)

        # Heure fin (Spinbox 0-23)
        tk.Label(card, text="Heure de fin (0-23) :", font=self.font_body,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=3, column=0, sticky="w", padx=15, pady=8)

        self._spin_fin = tk.Spinbox(card, from_=0, to=23, width=5,
                                     font=self.font_body,
                                     bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                                     insertbackground=COLORS["text_primary"],
                                     relief="flat", highlightthickness=1,
                                     highlightbackground=COLORS["border"],
                                     highlightcolor=COLORS["solar_yellow"])
        self._spin_fin.grid(row=3, column=1, sticky="w", padx=(5, 15), pady=8, ipady=4)

        # Info tranche (auto-déduite)
        info_frame = tk.Frame(card, bg=COLORS["bg_card"])
        info_frame.grid(row=4, column=0, columnspan=2, padx=15, pady=5)
        tk.Label(info_frame, text="ℹ️  La tranche horaire est déduite automatiquement : "
                 "Matin (6h-17h) | Soir (17h-19h) | Nuit (19h-6h)",
                 font=self.font_small, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], wraplength=500).pack()

        # Bouton ajouter
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)

        self._make_button(btn_frame, "✅  Ajouter l'appareil",
                          self._action_ajouter,
                          color=COLORS["battery_green"], width=30).pack()

        # Zone de message
        self._label_message = tk.Label(self.main_area, text="", font=self.font_body,
                                       bg=COLORS["bg_dark"], fg=COLORS["success"])
        self._label_message.pack(pady=5)

    def _action_ajouter(self):
        """Action du bouton Ajouter."""
        nom = self._entry_nom.get().strip()
        puissance_str = self._entry_puissance.get().strip()
        debut_str = self._spin_debut.get().strip()
        fin_str = self._spin_fin.get().strip()

        if not nom:
            messagebox.showwarning("Champ manquant", "Le nom de l'appareil est requis.")
            return

        try:
            puissance = float(puissance_str)
        except ValueError:
            messagebox.showwarning("Valeur invalide", "La puissance doit être un nombre.")
            return

        if puissance <= 0:
            messagebox.showwarning("Valeur invalide", "La puissance doit être positive.")
            return

        try:
            heure_debut = int(debut_str)
            heure_fin = int(fin_str)
        except ValueError:
            messagebox.showwarning("Valeur invalide", "Les heures doivent être des entiers (0-23).")
            return

        if not (0 <= heure_debut <= 23) or not (0 <= heure_fin <= 23):
            messagebox.showwarning("Valeur invalide", "Les heures doivent être entre 0 et 23.")
            return

        try:
            insert_appareil(nom, puissance, heure_debut, heure_fin)
            from models.appareil import Appareil
            a = Appareil(nom, puissance, heure_debut, heure_fin)
            self._label_message.config(
                text=f"✅ '{nom}' ajouté — {puissance}W, {heure_debut}h→{heure_fin}h "
                     f"({a.duree_h()}h) = {a.energie_wh()} Wh [{a.tranche}]",
                fg=COLORS["success"])
            # Vider les champs
            self._entry_nom.delete(0, tk.END)
            self._entry_puissance.delete(0, tk.END)
            self._spin_debut.delete(0, tk.END)
            self._spin_debut.insert(0, "0")
            self._spin_fin.delete(0, tk.END)
            self._spin_fin.insert(0, "0")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter l'appareil :\n{e}")

    # ------------------------------------------
    # PAGE: Liste des appareils
    # ------------------------------------------
    def _page_liste(self):
        """Tableau des appareils avec suppression."""
        self._make_header(self.main_area, "Liste des appareils", "Tous les appareils enregistrés")

        # Treeview
        tree_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))

        columns = ("id", "nom", "puissance", "horaire", "duree", "energie", "tranche")
        self._tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                  style="Dark.Treeview", selectmode="browse")

        headers = {
            "id": ("ID", 50),
            "nom": ("Nom", 180),
            "puissance": ("Puissance (W)", 110),
            "horaire": ("Horaire", 100),
            "duree": ("Durée (h)", 80),
            "energie": ("Énergie (Wh)", 110),
            "tranche": ("Tranche", 80),
        }
        for col, (text, width) in headers.items():
            self._tree.heading(col, text=text)
            self._tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview,
                                  style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Boutons
        btn_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        self._make_button(btn_frame, "🗑️  Supprimer sélection",
                          self._action_supprimer,
                          color=COLORS["danger"], width=25).pack(side=tk.LEFT, padx=(0, 10))
        self._make_button(btn_frame, "🔄  Rafraîchir",
                          lambda: self.show_page("liste"),
                          color=COLORS["battery_blue"], width=15).pack(side=tk.LEFT)

        # Charger les données
        self._charger_appareils()

    def _charger_appareils(self):
        """Charge les appareils dans le Treeview."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        try:
            appareils = get_all_appareils()
            for a in appareils:
                self._tree.insert("", tk.END, values=(
                    a.id, a.nom, f"{a.puissance_w:.1f}",
                    f"{a.heure_debut}h→{a.heure_fin}h",
                    f"{a.duree_h()}", f"{a.energie_wh():.1f}", a.tranche
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les appareils :\n{e}")

    def _action_supprimer(self):
        """Supprime l'appareil sélectionné."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Veuillez sélectionner un appareil à supprimer.")
            return

        item = self._tree.item(selected[0])
        appareil_id = item["values"][0]
        nom = item["values"][1]

        if messagebox.askyesno("Confirmation", f"Supprimer l'appareil '{nom}' (ID {appareil_id}) ?"):
            try:
                delete_appareil(appareil_id)
                self._charger_appareils()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer :\n{e}")

    # ------------------------------------------
    # PAGE: Panneaux Solaires (Alea 3)
    # ------------------------------------------
    def _page_panneaux(self):
        """Page de gestion des types de panneaux solaires."""
        self._make_header(self.main_area, "Panneaux Solaires",
                          "Définir les types de panneaux disponibles à l'achat")

        # --- Formulaire d'ajout ---
        card = self._make_card(self.main_area)
        card.columnconfigure(1, weight=1)

        tk.Label(card, text="➕  Ajouter un panneau", font=self.font_subheading,
                 bg=COLORS["bg_card"], fg=COLORS["solar_yellow"]).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self._pn_nom = self._make_entry(card, "Nom du panneau :", 1)
        self._pn_energie = self._make_entry(card, "Énergie unitaire (W) :", 2)
        self._pn_pourcentage = self._make_entry(card, "Pourcentage rendement (%) :", 3)
        self._pn_prix = self._make_entry(card, "Prix unitaire (Ar) :", 4)

        # Info
        info_frame = tk.Frame(card, bg=COLORS["bg_card"])
        info_frame.grid(row=5, column=0, columnspan=2, padx=15, pady=5)
        tk.Label(info_frame,
                 text="ℹ️  Puissance réelle = Énergie unitaire × Pourcentage / 100",
                 font=self.font_small, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack()

        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        self._make_button(btn_frame, "✅  Ajouter le panneau",
                          self._action_ajouter_panneau,
                          color=COLORS["battery_green"], width=30).pack()

        self._pn_message = tk.Label(self.main_area, text="", font=self.font_body,
                                    bg=COLORS["bg_dark"], fg=COLORS["success"])
        self._pn_message.pack(pady=5)

        # --- Tableau des panneaux ---
        tree_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))

        columns = ("id", "nom", "energie", "pourcentage", "reel", "prix")
        self._pn_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      style="Dark.Treeview", selectmode="browse")

        headers = {
            "id": ("ID", 50),
            "nom": ("Nom", 150),
            "energie": ("Énergie (W)", 110),
            "pourcentage": ("Rendement (%)", 110),
            "reel": ("Réel (W)", 100),
            "prix": ("Prix (Ar)", 120),
        }
        for col, (text, width) in headers.items():
            self._pn_tree.heading(col, text=text)
            self._pn_tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._pn_tree.yview,
                                  style="Dark.Vertical.TScrollbar")
        self._pn_tree.configure(yscrollcommand=scrollbar.set)
        self._pn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Boutons
        btn_frame2 = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        btn_frame2.pack(fill=tk.X, padx=30, pady=(0, 20))
        self._make_button(btn_frame2, "🗑️  Supprimer sélection",
                          self._action_supprimer_panneau,
                          color=COLORS["danger"], width=25).pack(side=tk.LEFT, padx=(0, 10))
        self._make_button(btn_frame2, "🔄  Rafraîchir",
                          lambda: self.show_page("panneaux"),
                          color=COLORS["battery_blue"], width=15).pack(side=tk.LEFT)

        self._charger_panneaux()

    def _charger_panneaux(self):
        """Charge les panneaux dans le Treeview."""
        for item in self._pn_tree.get_children():
            self._pn_tree.delete(item)
        try:
            panneaux = get_all_panneaux()
            for p in panneaux:
                self._pn_tree.insert("", tk.END, values=(
                    p.id, p.nom, f"{p.energie_unitaire_w:.1f}",
                    f"{p.pourcentage:.1f}", f"{p.puissance_reelle_w:.1f}",
                    f"{p.prix_unitaire:.0f}"
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les panneaux :\n{e}")

    def _action_ajouter_panneau(self):
        """Ajoute un panneau."""
        nom = self._pn_nom.get().strip()
        if not nom:
            messagebox.showwarning("Champ manquant", "Le nom du panneau est requis.")
            return
        try:
            energie = float(self._pn_energie.get().strip())
            pourcentage = float(self._pn_pourcentage.get().strip())
            prix = float(self._pn_prix.get().strip())
        except ValueError:
            messagebox.showwarning("Valeur invalide",
                                   "Énergie, pourcentage et prix doivent être des nombres.")
            return

        try:
            insert_panneau(nom, energie, pourcentage, prix)
            reel = energie * pourcentage / 100
            self._pn_message.config(
                text=f"✅ '{nom}' ajouté — {energie}W × {pourcentage}% = {reel:.1f}W réel, {prix:.0f} Ar",
                fg=COLORS["success"])
            self._pn_nom.delete(0, tk.END)
            self._pn_energie.delete(0, tk.END)
            self._pn_pourcentage.delete(0, tk.END)
            self._pn_prix.delete(0, tk.END)
            self._charger_panneaux()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter le panneau :\n{e}")

    def _action_supprimer_panneau(self):
        """Supprime le panneau sélectionné."""
        selected = self._pn_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Veuillez sélectionner un panneau à supprimer.")
            return
        item = self._pn_tree.item(selected[0])
        panneau_id = item["values"][0]
        nom = item["values"][1]
        if messagebox.askyesno("Confirmation", f"Supprimer le panneau '{nom}' (ID {panneau_id}) ?"):
            try:
                delete_panneau(panneau_id)
                self._charger_panneaux()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer :\n{e}")

    # ------------------------------------------
    # PAGE: Paramètres (Prix énergie)
    # ------------------------------------------
    def _page_parametres(self):
        """Page de paramétrage des prix d'achat de l'énergie."""
        self._make_header(self.main_area, "Paramètres",
                          "Configurer les prix d'achat de l'énergie (Ar/Wh)")

        # Charger les prix actuels
        try:
            prix = get_prix_energie()
        except Exception:
            prix = {
                "prix_jour_ouvrable": 50,
                "prix_soir_ouvrable": 80,
                "prix_jour_weekend": 70,
                "prix_soir_weekend": 100,
            }

        # --- Carte Jours Ouvrables ---
        card_ouv = self._make_card(self.main_area)
        card_ouv.columnconfigure(1, weight=1)

        tk.Label(card_ouv, text="📅  Jours Ouvrables (Lundi → Vendredi)",
                 font=self.font_subheading,
                 bg=COLORS["bg_card"], fg=COLORS["solar_yellow"]).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self._prix_jour_ouv = self._make_entry(card_ouv, "Prix jour (Ar/Wh) :", 1)
        self._prix_jour_ouv.insert(0, str(prix["prix_jour_ouvrable"]))

        self._prix_soir_ouv = self._make_entry(card_ouv, "Prix soir (Ar/Wh) :", 2)
        self._prix_soir_ouv.insert(0, str(prix["prix_soir_ouvrable"]))

        tk.Frame(card_ouv, bg=COLORS["bg_card"], height=8).grid(
            row=3, column=0, columnspan=2)

        # --- Carte Weekend ---
        card_wkd = self._make_card(self.main_area)
        card_wkd.columnconfigure(1, weight=1)

        tk.Label(card_wkd, text="🏖️  Weekend (Samedi → Dimanche)",
                 font=self.font_subheading,
                 bg=COLORS["bg_card"], fg=COLORS["solar_yellow"]).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self._prix_jour_wkd = self._make_entry(card_wkd, "Prix jour (Ar/Wh) :", 1)
        self._prix_jour_wkd.insert(0, str(prix["prix_jour_weekend"]))

        self._prix_soir_wkd = self._make_entry(card_wkd, "Prix soir (Ar/Wh) :", 2)
        self._prix_soir_wkd.insert(0, str(prix["prix_soir_weekend"]))

        tk.Frame(card_wkd, bg=COLORS["bg_card"], height=8).grid(
            row=3, column=0, columnspan=2)

        # Bouton enregistrer
        btn_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=30, pady=10)

        self._make_button(btn_frame, "💾  Enregistrer les prix",
                          self._action_enregistrer_prix,
                          color=COLORS["battery_green"], width=30).pack(anchor="w")

        # Message de feedback
        self._prix_message = tk.Label(self.main_area, text="", font=self.font_body,
                                       bg=COLORS["bg_dark"], fg=COLORS["success"])
        self._prix_message.pack(pady=5)

        # Info
        info_card = self._make_card(self.main_area)
        tk.Label(info_card,
                 text="ℹ️  Ces prix sont utilisés dans la simulation (ALEA 3) pour calculer\n"
                      "les revenus de vente de l'énergie excédentaire produite par les panneaux.\n"
                      "Jour = 6h→17h | Soir = 17h→19h | La nuit, les panneaux ne produisent pas.",
                 font=self.font_small, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], justify="left").pack(padx=15, pady=10)

    def _action_enregistrer_prix(self):
        """Enregistre les prix d'achat dans la base de données."""
        try:
            pjo = float(self._prix_jour_ouv.get().strip())
            pso = float(self._prix_soir_ouv.get().strip())
            pjw = float(self._prix_jour_wkd.get().strip())
            psw = float(self._prix_soir_wkd.get().strip())
        except ValueError:
            messagebox.showwarning("Valeur invalide",
                                   "Tous les prix doivent être des nombres.")
            return

        if any(v < 0 for v in [pjo, pso, pjw, psw]):
            messagebox.showwarning("Valeur invalide",
                                   "Les prix ne peuvent pas être négatifs.")
            return

        try:
            update_prix_energie(pjo, pso, pjw, psw)
            self._prix_message.config(
                text=f"✅ Prix enregistrés — Ouvrable: {pjo}/{pso} Ar/Wh | "
                     f"Weekend: {pjw}/{psw} Ar/Wh",
                fg=COLORS["success"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer :\\n{e}")

    # ------------------------------------------
    # PAGE: Simulation
    # ------------------------------------------
    def _page_simulation(self):
        """Page de simulation avec résultats visuels."""
        self._make_header(self.main_area, "Simulation", "Simuler une journée complète et dimensionner le système")

        # Scrollable frame
        canvas = tk.Canvas(self.main_area, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_area, orient=tk.VERTICAL, command=canvas.yview,
                                  style="Dark.Vertical.TScrollbar")
        self._sim_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        self._sim_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._sim_frame, anchor="nw", tags="frame")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Responsive width
        def on_canvas_configure(event):
            canvas.itemconfig("frame", width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mousewheel scroll
        def on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        self._global_bindings.append(("<MouseWheel>", None))

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bouton lancer simulation
        btn_frame = tk.Frame(self._sim_frame, bg=COLORS["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=30, pady=10)

        self._make_button(btn_frame, "🚀  Lancer la simulation",
                          self._action_simuler,
                          color=COLORS["accent"], width=30).pack(anchor="w")

        # Zone résultats (sera remplie après simulation)
        self._result_container = tk.Frame(self._sim_frame, bg=COLORS["bg_dark"])
        self._result_container.pack(fill=tk.BOTH, expand=True)

    def _action_simuler(self):
        """Lance la simulation et affiche les résultats."""
        # Vider les résultats précédents
        for widget in self._result_container.winfo_children():
            widget.destroy()

        try:
            appareils = get_all_appareils()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les appareils :\n{e}")
            return

        if not appareils:
            messagebox.showinfo("Information", "Aucun appareil enregistré.\nAjoutez des appareils d'abord.")
            return

        # Charger les panneaux pour Alea 3
        try:
            panneaux = get_all_panneaux()
        except Exception:
            panneaux = []

        # Charger les prix d'achat énergie
        try:
            prix_energie = get_prix_energie()
        except Exception:
            prix_energie = None

        resultat = simuler_journee(appareils, panneaux=panneaux, prix_energie=prix_energie)

        if resultat.get("erreur"):
            messagebox.showerror("Erreur", resultat["erreur"])
            return

        container = self._result_container

        # --- Statut global ---
        statut = resultat["statut"]
        statut_info = {
            "OK": ("✅ Système correctement dimensionné", COLORS["success"]),
            "INSUFFISANT": ("❌ Batterie insuffisante pour la nuit", COLORS["danger"]),
            "ATTENTION": ("⚠️ " + resultat["message"], COLORS["warning"]),
        }
        msg, color = statut_info.get(statut, ("❓ Inconnu", COLORS["text_muted"]))

        status_card = tk.Frame(container, bg=color, highlightbackground=color, highlightthickness=2)
        status_card.pack(fill=tk.X, padx=30, pady=(10, 5))
        tk.Label(status_card, text=msg, font=self.font_heading,
                 bg=color, fg="white").pack(padx=15, pady=10)

        # --- Cartes métriques principales ---
        metrics_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        metrics_frame.pack(fill=tk.X, padx=30, pady=10)
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1)

        metrics = [
            ("☀️", "Panneau requis", formater_puissance(resultat["panneau_puissance_w"]), COLORS["solar_yellow"]),
            ("🔋", "Batterie requise", formater_energie(resultat["batterie_capacite_wh"]), COLORS["battery_green"]),
            ("📊", "Conso. Jour", formater_energie(resultat["energie_jour_wh"]), COLORS["solar_orange"]),
            ("🌙", "Conso. Nuit", formater_energie(resultat["energie_nuit_wh"]), COLORS["battery_blue"]),
        ]

        for i, (icon, label, value, c) in enumerate(metrics):
            card = self._make_stat_card(metrics_frame, icon, label, value, c)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

        # --- Détail sections ---
        sections = [
            ("📊  Consommation Énergétique", [
                ("Énergie jour (matin + 50% soir)", formater_energie(resultat["energie_jour_wh"])),
                ("Énergie nuit (nuit + 50% soir)", formater_energie(resultat["energie_nuit_wh"])),
                ("Énergie totale", formater_energie(resultat["energie_totale_wh"])),
            ]),
            ("🕒  Détail par Tranche", [
                (f"{t.capitalize()}", formater_energie(v))
                for t, v in resultat["detail_tranches"].items()
            ]),
            ("🔋  Batterie", [
                ("Capacité nécessaire (avec marge +50%)", formater_energie(resultat["batterie_capacite_wh"])),
                ("Autonomie nuit", "✅ OK" if resultat["batterie_autonomie_ok"] else "❌ Insuffisante"),
                ("Marge de sécurité", f"{resultat['batterie_marge_pct']}%"),
            ]),
            ("🔄  Recharge Batterie", [
                ("Puissance disponible recharge", formater_puissance(resultat["puissance_recharge_w"])),
                ("Temps de recharge estimé", f"{resultat['temps_recharge_h']:.1f} h" if resultat["temps_recharge_h"] else "∞ (impossible)"),
                ("Batterie chargée avant 17h", "✅ OUI" if resultat["recharge_ok"] else "❌ NON"),
            ]),
        ]

        for title, rows in sections:
            card = tk.Frame(container, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(fill=tk.X, padx=30, pady=5)

            tk.Label(card, text=title, font=self.font_subheading,
                     bg=COLORS["bg_card"], fg=COLORS["solar_yellow"],
                     anchor="w").pack(fill=tk.X, padx=15, pady=(10, 5))

            for label, value in rows:
                row_frame = tk.Frame(card, bg=COLORS["bg_card"])
                row_frame.pack(fill=tk.X, padx=15, pady=2)
                tk.Label(row_frame, text=label, font=self.font_body,
                         bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                         anchor="w").pack(side=tk.LEFT)
                tk.Label(row_frame, text=value, font=self.font_body,
                         bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                         anchor="e").pack(side=tk.RIGHT)

            # petit padding en bas
            tk.Frame(card, bg=COLORS["bg_card"], height=8).pack()

        # ==========================================================
        # ALEA 1 : Comparaison rendement 40% vs 30%
        # ==========================================================
        alea1 = resultat.get("alea1", [])
        if alea1:
            # Titre section
            tk.Frame(container, bg=COLORS["accent"], height=3).pack(fill=tk.X, padx=30, pady=(20, 0))
            alea1_header = tk.Frame(container, bg=COLORS["bg_dark"])
            alea1_header.pack(fill=tk.X, padx=30, pady=(5, 10))
            tk.Label(alea1_header, text="🎲  ALEA 1 — Comparaison Rendement Panneau",
                     font=self.font_heading, bg=COLORS["bg_dark"],
                     fg=COLORS["accent"]).pack(anchor="w")
            tk.Label(alea1_header, text="Simulation avec deux rendements différents côte à côte",
                     font=self.font_small, bg=COLORS["bg_dark"],
                     fg=COLORS["text_muted"]).pack(anchor="w")

            # Cartes côte à côte
            compare_frame = tk.Frame(container, bg=COLORS["bg_dark"])
            compare_frame.pack(fill=tk.X, padx=30, pady=5)
            compare_frame.columnconfigure((0, 1), weight=1)

            colors_alea = [COLORS["solar_yellow"], COLORS["solar_orange"]]

            for i, res in enumerate(alea1):
                rend_pct = res["rendement_pct"]
                border_color = colors_alea[i]

                card = tk.Frame(compare_frame, bg=COLORS["bg_card"],
                                highlightbackground=border_color, highlightthickness=2)
                card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

                # En-tête de la carte
                header_bg = border_color
                header_frame = tk.Frame(card, bg=header_bg)
                header_frame.pack(fill=tk.X)
                tk.Label(header_frame, text=f"☀️  Rendement {rend_pct}%",
                         font=self.font_subheading, bg=header_bg,
                         fg="white").pack(padx=15, pady=8)

                # Données
                rows_alea = [
                    ("Puissance panneau", formater_puissance(res["panneau_puissance_w"])),
                    ("Production réelle", formater_puissance(res["panneau_production_reelle_w"])),
                    ("Production journalière", formater_energie(res["panneau_production_journaliere_wh"])),
                    ("Puissance recharge", formater_puissance(res["puissance_recharge_w"])),
                    ("Temps de recharge",
                     f"{res['temps_recharge_h']:.1f} h" if res["temps_recharge_h"] else "∞"),
                    ("Recharge avant 17h",
                     "✅ OUI" if res["recharge_ok"] else "❌ NON"),
                ]

                for label, value in rows_alea:
                    row_frame = tk.Frame(card, bg=COLORS["bg_card"])
                    row_frame.pack(fill=tk.X, padx=15, pady=3)
                    tk.Label(row_frame, text=label, font=self.font_body,
                             bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                             anchor="w").pack(side=tk.LEFT)
                    tk.Label(row_frame, text=value, font=self.font_body,
                             bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                             anchor="e").pack(side=tk.RIGHT)

                tk.Frame(card, bg=COLORS["bg_card"], height=10).pack()

        # ==========================================================
        # ALEA 2 : Pic de consommation / Convertisseur
        # ==========================================================
        alea2 = resultat.get("alea2", {})
        if alea2 and alea2.get("pic_w", 0) > 0:
            # Titre section
            tk.Frame(container, bg=COLORS["battery_blue"], height=3).pack(fill=tk.X, padx=30, pady=(20, 0))
            alea2_header = tk.Frame(container, bg=COLORS["bg_dark"])
            alea2_header.pack(fill=tk.X, padx=30, pady=(5, 10))
            tk.Label(alea2_header, text="🎲  ALEA 2 — Pic de Consommation & Convertisseur",
                     font=self.font_heading, bg=COLORS["bg_dark"],
                     fg=COLORS["battery_blue"]).pack(anchor="w")
            tk.Label(alea2_header,
                     text="Pic = puissance max simultanée (heure par heure) | Convertisseur = Pic × 2",
                     font=self.font_small, bg=COLORS["bg_dark"],
                     fg=COLORS["text_muted"]).pack(anchor="w")

            # Cartes principales Alea 2
            alea2_metrics = tk.Frame(container, bg=COLORS["bg_dark"])
            alea2_metrics.pack(fill=tk.X, padx=30, pady=5)
            alea2_metrics.columnconfigure((0, 1, 2), weight=1)

            pic_card = self._make_stat_card(
                alea2_metrics, "⚡", "Pic de consommation",
                formater_puissance(alea2["pic_w"]),
                COLORS["danger"]
            )
            pic_card.grid(row=0, column=0, padx=8, pady=5, sticky="nsew")

            conv_card = self._make_stat_card(
                alea2_metrics, "🔌", "Convertisseur (Pic × 2)",
                formater_puissance(alea2["convertisseur_w"]),
                COLORS["accent"]
            )
            conv_card.grid(row=0, column=1, padx=8, pady=5, sticky="nsew")

            heure_pic = alea2["heure_pic"]
            heure_card = self._make_stat_card(
                alea2_metrics, "🕒", "Heure du pic",
                f"{heure_pic}h",
                COLORS["solar_orange"]
            )
            heure_card.grid(row=0, column=2, padx=8, pady=5, sticky="nsew")

            # Appareils actifs au moment du pic
            if alea2.get("appareils_pic"):
                pic_detail_card = tk.Frame(container, bg=COLORS["bg_card"],
                                           highlightbackground=COLORS["danger"],
                                           highlightthickness=1)
                pic_detail_card.pack(fill=tk.X, padx=30, pady=5)

                tk.Label(pic_detail_card,
                         text=f"⚡  Appareils actifs à {heure_pic}h (chevauchement)",
                         font=self.font_subheading, bg=COLORS["bg_card"],
                         fg=COLORS["danger"]).pack(fill=tk.X, padx=15, pady=(10, 5))

                for ap in alea2["appareils_pic"]:
                    row_frame = tk.Frame(pic_detail_card, bg=COLORS["bg_card"])
                    row_frame.pack(fill=tk.X, padx=15, pady=2)
                    tk.Label(row_frame, text=f"  {ap['nom']}  ({ap['horaire']})",
                             font=self.font_body, bg=COLORS["bg_card"],
                             fg=COLORS["text_secondary"], anchor="w").pack(side=tk.LEFT)
                    tk.Label(row_frame, text=formater_puissance(ap["puissance_w"]),
                             font=self.font_body, bg=COLORS["bg_card"],
                             fg=COLORS["text_primary"], anchor="e").pack(side=tk.RIGHT)

                tk.Frame(pic_detail_card, bg=COLORS["bg_card"], height=10).pack()

            # Graphe heure par heure (texte)
            hourly_card = tk.Frame(container, bg=COLORS["bg_card"],
                                   highlightbackground=COLORS["battery_blue"],
                                   highlightthickness=1)
            hourly_card.pack(fill=tk.X, padx=30, pady=5)

            tk.Label(hourly_card, text="📊  Puissance totale heure par heure",
                     font=self.font_subheading, bg=COLORS["bg_card"],
                     fg=COLORS["battery_blue"]).pack(fill=tk.X, padx=15, pady=(10, 5))

            detail_heure = alea2.get("detail_par_heure", {})
            max_p = max(detail_heure.values()) if detail_heure else 1
            bar_max_width = 30  # chars

            for h in range(24):
                p = detail_heure.get(h, 0)
                if p == 0:
                    continue

                row_frame = tk.Frame(hourly_card, bg=COLORS["bg_card"])
                row_frame.pack(fill=tk.X, padx=15, pady=1)

                is_pic = (h == heure_pic)
                fg = COLORS["danger"] if is_pic else COLORS["text_secondary"]
                bar_len = int((p / max_p) * bar_max_width) if max_p > 0 else 0
                bar = "█" * bar_len
                marker = " ◀ PIC" if is_pic else ""

                tk.Label(row_frame, text=f"{h:2d}h", font=("Consolas", 9),
                         bg=COLORS["bg_card"], fg=fg, width=4,
                         anchor="e").pack(side=tk.LEFT)
                tk.Label(row_frame, text=f" {bar}", font=("Consolas", 9),
                         bg=COLORS["bg_card"], fg=COLORS["solar_yellow"] if not is_pic else COLORS["danger"],
                         anchor="w").pack(side=tk.LEFT)
                tk.Label(row_frame, text=f" {formater_puissance(p)}{marker}",
                         font=("Consolas", 9), bg=COLORS["bg_card"],
                         fg=fg, anchor="w").pack(side=tk.LEFT)

            tk.Frame(hourly_card, bg=COLORS["bg_card"], height=10).pack()

        # ==========================================================
        # ALEA 3 : Sélection de panneaux solaires
        # ==========================================================
        alea3 = resultat.get("alea3", [])
        if alea3:
            # Titre section
            tk.Frame(container, bg=COLORS["battery_green"], height=3).pack(fill=tk.X, padx=30, pady=(20, 0))
            alea3_header = tk.Frame(container, bg=COLORS["bg_dark"])
            alea3_header.pack(fill=tk.X, padx=30, pady=(5, 10))
            tk.Label(alea3_header, text="🎲  ALEA 3 — Sélection de Panneaux Solaires",
                     font=self.font_heading, bg=COLORS["bg_dark"],
                     fg=COLORS["battery_green"]).pack(anchor="w")

            puissance_req = resultat["panneau_puissance_w"]
            tk.Label(alea3_header,
                     text=f"Puissance théorique requise : {formater_puissance(puissance_req)} — "
                          f"Prix total pour chaque type de panneau",
                     font=self.font_small, bg=COLORS["bg_dark"],
                     fg=COLORS["text_muted"]).pack(anchor="w")

            # Tableau comparatif
            table_card = tk.Frame(container, bg=COLORS["bg_card"],
                                  highlightbackground=COLORS["battery_green"],
                                  highlightthickness=1)
            table_card.pack(fill=tk.X, padx=30, pady=5)

            # En-têtes
            header_frame = tk.Frame(table_card, bg=COLORS["bg_card"])
            header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
            header_cols = ["Rang", "Nom", "Unitaire (W)", "Rendement", "Réel (W)",
                           "Nb panneaux", "Prix unit.", "Prix TOTAL",
                           "Vend. Jour", "Vend. Soir"]
            for j, h_text in enumerate(header_cols):
                w = 10 if j >= 8 else 12
                tk.Label(header_frame, text=h_text, font=self.font_small,
                         bg=COLORS["bg_card"], fg=COLORS["solar_yellow"],
                         width=w, anchor="center").pack(side=tk.LEFT, padx=2)

            tk.Frame(table_card, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=15)

            # Lignes (triées par prix total croissant)
            for idx, opt in enumerate(alea3):
                is_best = (idx == 0)
                row_bg = COLORS["bg_card"]
                row_frame = tk.Frame(table_card, bg=row_bg)
                row_frame.pack(fill=tk.X, padx=15, pady=2)

                rang_text = f"🏆 {idx + 1}" if is_best else f"   {idx + 1}"
                fg_color = COLORS["success"] if is_best else COLORS["text_secondary"]
                prix_fg = COLORS["success"] if is_best else COLORS["text_primary"]

                values = [
                    rang_text,
                    opt["nom"],
                    f"{opt['energie_unitaire_w']:.0f} W",
                    f"{opt['pourcentage']:.0f}%",
                    f"{opt['puissance_reelle_w']:.1f} W",
                    f"{opt['nb_panneaux']}",
                    f"{opt['prix_unitaire']:.0f} Ar",
                    f"{opt['prix_total']:.0f} Ar",
                    formater_energie(opt.get('energie_vendable_jour_wh', 0)),
                    formater_energie(opt.get('energie_vendable_soir_wh', 0)),
                ]

                for j, val in enumerate(values):
                    fg = prix_fg if j == 7 else fg_color
                    w = 10 if j >= 8 else 12
                    tk.Label(row_frame, text=val, font=self.font_body,
                             bg=row_bg, fg=fg, width=w,
                             anchor="center").pack(side=tk.LEFT, padx=2)

            # Meilleur choix en évidence
            best = alea3[0]
            best_card = tk.Frame(container, bg=COLORS["bg_card"],
                                 highlightbackground=COLORS["success"],
                                 highlightthickness=2)
            best_card.pack(fill=tk.X, padx=30, pady=(10, 5))

            tk.Label(best_card,
                     text=f"🏆  Meilleur choix : {best['nom']} — "
                          f"{best['nb_panneaux']} panneau(x) × {best['prix_unitaire']:.0f} Ar = "
                          f"{best['prix_total']:.0f} Ar",
                     font=self.font_subheading, bg=COLORS["bg_card"],
                     fg=COLORS["success"]).pack(padx=15, pady=10)

            tk.Label(best_card,
                     text=f"Puissance totale fournie : {best['puissance_totale_w']:.1f} W "
                          f"(besoin : {puissance_req:.1f} W)",
                     font=self.font_body, bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack(padx=15, pady=(0, 10))

            tk.Frame(table_card, bg=COLORS["bg_card"], height=10).pack()

            # ==========================================================
            # Revenus de vente d'énergie excédentaire
            # ==========================================================
            prix_e = resultat.get("prix_energie", {})
            if prix_e and alea3[0].get("revenu_total_ouvrable") is not None:
                tk.Frame(container, bg=COLORS["solar_orange"], height=3).pack(
                    fill=tk.X, padx=30, pady=(20, 0))
                rev_header = tk.Frame(container, bg=COLORS["bg_dark"])
                rev_header.pack(fill=tk.X, padx=30, pady=(5, 10))
                tk.Label(rev_header,
                         text="💰  Revenus de Vente — Énergie Excédentaire",
                         font=self.font_heading, bg=COLORS["bg_dark"],
                         fg=COLORS["solar_orange"]).pack(anchor="w")
                tk.Label(rev_header,
                         text=f"Prix (Ar/Wh) — Ouvrable: Jour={prix_e['prix_jour_ouvrable']} | "
                              f"Soir={prix_e['prix_soir_ouvrable']}  •  "
                              f"Weekend: Jour={prix_e['prix_jour_weekend']} | "
                              f"Soir={prix_e['prix_soir_weekend']}",
                         font=self.font_small, bg=COLORS["bg_dark"],
                         fg=COLORS["text_muted"]).pack(anchor="w")

                for opt in alea3:
                    rev_card = tk.Frame(container, bg=COLORS["bg_card"],
                                        highlightbackground=COLORS["solar_orange"],
                                        highlightthickness=1)
                    rev_card.pack(fill=tk.X, padx=30, pady=4)

                    tk.Label(rev_card,
                             text=f"🔆  {opt['nom']} — {opt['nb_panneaux']} panneau(x)",
                             font=self.font_subheading, bg=COLORS["bg_card"],
                             fg=COLORS["solar_yellow"]).pack(
                        fill=tk.X, padx=15, pady=(10, 5))

                    # Sous-header
                    sh_frame = tk.Frame(rev_card, bg=COLORS["bg_card"])
                    sh_frame.pack(fill=tk.X, padx=15, pady=2)
                    sh_labels = ["", "Vendable Jour", "Prix Jour",
                                 "Vendable Soir", "Prix Soir", "TOTAL"]
                    for sl in sh_labels:
                        tk.Label(sh_frame, text=sl, font=self.font_small,
                                 bg=COLORS["bg_card"], fg=COLORS["solar_yellow"],
                                 width=14, anchor="center").pack(side=tk.LEFT, padx=1)

                    tk.Frame(rev_card, bg=COLORS["border"], height=1).pack(
                        fill=tk.X, padx=15)

                    # Ligne Jour Ouvrable
                    ouv_frame = tk.Frame(rev_card, bg=COLORS["bg_card"])
                    ouv_frame.pack(fill=tk.X, padx=15, pady=2)
                    ouv_vals = [
                        "📅 Ouvrable",
                        formater_energie(opt.get('energie_vendable_jour_wh', 0)),
                        f"{opt.get('revenu_jour_ouvrable', 0):.0f} Ar",
                        formater_energie(opt.get('energie_vendable_soir_wh', 0)),
                        f"{opt.get('revenu_soir_ouvrable', 0):.0f} Ar",
                        f"{opt.get('revenu_total_ouvrable', 0):.0f} Ar",
                    ]
                    for vi, v in enumerate(ouv_vals):
                        fg = COLORS["success"] if vi == 5 else COLORS["text_primary"]
                        tk.Label(ouv_frame, text=v, font=self.font_body,
                                 bg=COLORS["bg_card"], fg=fg,
                                 width=14, anchor="center").pack(side=tk.LEFT, padx=1)

                    # Ligne Weekend
                    wkd_frame = tk.Frame(rev_card, bg=COLORS["bg_card"])
                    wkd_frame.pack(fill=tk.X, padx=15, pady=2)
                    wkd_vals = [
                        "🏖️ Weekend",
                        formater_energie(opt.get('energie_vendable_jour_wh', 0)),
                        f"{opt.get('revenu_jour_weekend', 0):.0f} Ar",
                        formater_energie(opt.get('energie_vendable_soir_wh', 0)),
                        f"{opt.get('revenu_soir_weekend', 0):.0f} Ar",
                        f"{opt.get('revenu_total_weekend', 0):.0f} Ar",
                    ]
                    for vi, v in enumerate(wkd_vals):
                        fg = COLORS["success"] if vi == 5 else COLORS["text_primary"]
                        tk.Label(wkd_frame, text=v, font=self.font_body,
                                 bg=COLORS["bg_card"], fg=fg,
                                 width=14, anchor="center").pack(side=tk.LEFT, padx=1)

                    tk.Frame(rev_card, bg=COLORS["bg_card"], height=8).pack()

        elif not resultat.get("alea3"):
            # Aucun panneau défini
            tk.Frame(container, bg=COLORS["battery_green"], height=3).pack(fill=tk.X, padx=30, pady=(20, 0))
            no_pn_card = tk.Frame(container, bg=COLORS["bg_card"],
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1)
            no_pn_card.pack(fill=tk.X, padx=30, pady=5)
            tk.Label(no_pn_card,
                     text="🔆  ALEA 3 — Aucun panneau défini. "
                          "Ajoutez des panneaux dans la page 'Panneaux' pour voir la comparaison.",
                     font=self.font_body, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(padx=15, pady=10)

        # --- Sauvegarder ---
        try:
            save_resultat(
                resultat["energie_jour_wh"],
                resultat["energie_nuit_wh"],
                resultat["batterie_capacite_wh"],
                resultat["panneau_puissance_w"]
            )
            save_label = tk.Label(container, text="💾  Résultat sauvegardé dans l'historique",
                                  font=self.font_small, bg=COLORS["bg_dark"],
                                  fg=COLORS["success"])
            save_label.pack(pady=10)
        except Exception:
            pass

    # ------------------------------------------
    # PAGE: Historique
    # ------------------------------------------
    def _page_historique(self):
        """Tableau de l'historique des simulations."""
        self._make_header(self.main_area, "Historique", "Résultats des simulations précédentes")

        tree_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        columns = ("id", "e_jour", "e_nuit", "batterie", "panneau", "date")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            style="Dark.Treeview", selectmode="browse")

        headers = {
            "id": ("ID", 50),
            "e_jour": ("Énergie Jour (Wh)", 140),
            "e_nuit": ("Énergie Nuit (Wh)", 140),
            "batterie": ("Batterie (Wh)", 130),
            "panneau": ("Panneau (W)", 120),
            "date": ("Date", 160),
        }
        for col, (text, width) in headers.items():
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview,
                                  style="Dark.Vertical.TScrollbar")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Charger données
        try:
            resultats = get_all_resultats()
            for r in resultats:
                date_str = r[5].strftime("%d/%m/%Y %H:%M") if r[5] else "N/A"
                tree.insert("", tk.END, values=(
                    r[0], f"{r[1]:.1f}", f"{r[2]:.1f}",
                    f"{r[3]:.1f}", f"{r[4]:.1f}", date_str
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'historique :\n{e}")

        # Bouton rafraîchir
        btn_frame = tk.Frame(self.main_area, bg=COLORS["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 15))
        self._make_button(btn_frame, "🔄  Rafraîchir",
                          lambda: self.show_page("historique"),
                          color=COLORS["battery_blue"], width=15).pack(anchor="w")


# ==========================================
# Point d'entrée
# ==========================================
if __name__ == "__main__":
    app = SolaireApp()
    app.mainloop()
