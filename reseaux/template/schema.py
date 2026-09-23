"""Noms des colonnes et des statuts de la base Notion (partagés par tout l'agent)."""

# Statuts : le cycle de vie d'une publication
IDEE = "💡 Idée"
A_REDIGER = "✍️ À rédiger"
A_VALIDER = "👀 À valider"
VALIDE = "✅ Validé"
PUBLIE = "🚀 Publié"
ERREUR = "⚠️ Erreur"

STATUTS = [
    (IDEE, "gray"),
    (A_REDIGER, "blue"),
    (A_VALIDER, "yellow"),
    (VALIDE, "green"),
    (PUBLIE, "purple"),
    (ERREUR, "red"),
]

# Colonnes
TITRE = "Titre"
STATUT = "Statut"
MOTS_CLES = "Mots-clés"
PILIER = "Pilier"
ANGLE = "Angle"
RESEAUX = "Réseaux"
DATE = "Date de publication"
TEXTE_LINKEDIN = "Texte LinkedIn"
TEXTE_FACEBOOK = "Texte Facebook"
TEXTE_INSTAGRAM = "Texte Instagram"
PROMPT_IMAGE = "Prompt image"
IMAGE = "Image"
PUBLIE_SUR = "Publié sur"
LIENS = "Liens"
ERREUR_DETAIL = "Erreur"
ACTION = "Action"
CONSIGNES = "Consignes"

# Actions à la demande (colonne Action, ou bouton Notion qui la remplit)
REECRIRE = "🔄 Réécrire le texte"
NOUVELLE_IMAGE = "🎨 Nouvelle image"
TOUT_REFAIRE = "✨ Tout refaire"
ACTIONS = [(REECRIRE, "blue"), (NOUVELLE_IMAGE, "pink"), (TOUT_REFAIRE, "purple")]

# Base « Thèmes de contenu »
THEME_NOM = "Thème"
THEME_ACTIF = "Actif"
THEME_FREQUENCE = "Fréquence"
THEME_DESCRIPTION = "Description"
THEME_MOTS_CLES = "Mots-clés"
FREQUENCES = [("Souvent", "green"), ("Normal", "blue"), ("Rarement", "gray")]

LINKEDIN, FACEBOOK, INSTAGRAM = "LinkedIn", "Facebook", "Instagram"
TOUS_RESEAUX = [LINKEDIN, FACEBOOK, INSTAGRAM]
TEXTE_PAR_RESEAU = {
    LINKEDIN: TEXTE_LINKEDIN,
    FACEBOOK: TEXTE_FACEBOOK,
    INSTAGRAM: TEXTE_INSTAGRAM,
}

def _options(noms_couleurs):
    return {"options": [{"name": n, "color": c} for n, c in noms_couleurs]}


RESEAU_COULEURS = [(LINKEDIN, "blue"), (FACEBOOK, "default"), (INSTAGRAM, "pink")]

# Définition utilisée par `python agent.py installer` pour créer la base
PROPRIETES = {
    TITRE: {"title": {}},
    STATUT: {"select": _options(STATUTS)},
    DATE: {"date": {}},
    RESEAUX: {"multi_select": _options(RESEAU_COULEURS)},
    PILIER: {"select": {}},  # options créées au fil des idées, selon marque.md
    MOTS_CLES: {"multi_select": {}},
    ANGLE: {"rich_text": {}},
    IMAGE: {"files": {}},
    TEXTE_LINKEDIN: {"rich_text": {}},
    TEXTE_FACEBOOK: {"rich_text": {}},
    TEXTE_INSTAGRAM: {"rich_text": {}},
    PROMPT_IMAGE: {"rich_text": {}},
    PUBLIE_SUR: {"multi_select": _options(RESEAU_COULEURS)},
    LIENS: {"rich_text": {}},
    ERREUR_DETAIL: {"rich_text": {}},
    ACTION: {"select": _options(ACTIONS)},
    CONSIGNES: {"rich_text": {}},
}

PROPRIETES_THEMES = {
    THEME_NOM: {"title": {}},
    THEME_ACTIF: {"checkbox": {}},
    THEME_FREQUENCE: {"select": _options(FREQUENCES)},
    THEME_DESCRIPTION: {"rich_text": {}},
    THEME_MOTS_CLES: {"multi_select": {}},
}
