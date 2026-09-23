"""Thèmes de contenu (piliers) : gérés dans la base Notion « Thèmes de contenu ».

L'utilisateur y ajoute, corrige, désactive ou supprime des thèmes et leurs mots-clés ;
l'agent les relit à chaque passage. Sans cette base, on se rabat sur marque.md.
"""
from functools import cache

import notion
import schema as s
from config import RACINE, env


def _texte_marque():
    fichier = RACINE / "marque.md"
    return fichier.read_text(encoding="utf-8") if fichier.exists() else ""


def _est_section_themes(titre):
    titre = titre.lower()
    return "pilier" in titre or "thème" in titre


def piliers_de_marque(texte=None):
    """Lit la liste « - Nom : description » de la section Piliers de marque.md."""
    themes, dans_section = [], False
    for ligne in (texte if texte is not None else _texte_marque()).splitlines():
        if ligne.startswith("## "):
            dans_section = _est_section_themes(ligne)
            continue
        if dans_section and ligne.strip().startswith("- "):
            nom, _, description = ligne.strip()[2:].partition(":")
            nom = nom.strip().strip("*").strip()
            if nom and not nom.startswith("["):
                themes.append({"nom": nom, "description": description.strip(),
                               "frequence": "Normal", "mots_cles": []})
    return themes


@cache
def themes_actifs():
    """Les thèmes cochés « Actif » dans Notion, ou ceux de marque.md à défaut."""
    base = env("NOTION_THEMES_ID")
    if not base:
        return piliers_de_marque()
    pages = notion.chercher({"property": s.THEME_ACTIF, "checkbox": {"equals": True}}, base)
    themes = []
    for page in pages:
        nom = (notion.lire(page, s.THEME_NOM) or "").strip()
        if nom:
            themes.append({
                "nom": nom,
                "description": (notion.lire(page, s.THEME_DESCRIPTION) or "").strip(),
                "frequence": notion.lire(page, s.THEME_FREQUENCE) or "Normal",
                "mots_cles": notion.lire(page, s.THEME_MOTS_CLES) or [],
            })
    return themes


def contexte_marque():
    """marque.md, dont la section des piliers est remplacée par les thèmes actifs de Notion."""
    texte = _texte_marque()
    if not env("NOTION_THEMES_ID"):
        return texte
    lignes, dans_section = [], False
    for ligne in texte.splitlines():
        if ligne.startswith("## "):
            dans_section = _est_section_themes(ligne)
        if not dans_section:
            lignes.append(ligne)

    bloc = ["## Thèmes de contenu (piliers)", ""]
    for t in themes_actifs():
        ligne = f"- {t['nom']} (fréquence : {t['frequence'].lower()})"
        if t["description"]:
            ligne += f" : {t['description']}"
        if t["mots_cles"]:
            ligne += f" | mots-clés à privilégier : {', '.join(t['mots_cles'])}"
        bloc.append(ligne)
    bloc += ["", "Fréquence « souvent » = à privilégier, « rarement » = occasionnel. "
                 "N'utilise que ces thèmes, avec leur nom exact."]
    return "\n".join(lignes).rstrip() + "\n\n" + "\n".join(bloc) + "\n"


def creer_base_themes(page_parent_id):
    """Crée la base « Thèmes de contenu » et y recopie les piliers de marque.md."""
    base = notion.creer_base(page_parent_id, "Thèmes de contenu", s.PROPRIETES_THEMES)
    base_id = base["id"].replace("-", "")
    themes = piliers_de_marque()
    for t in themes:
        notion.creer({
            s.THEME_NOM: notion.texte(t["nom"], titre=True),
            s.THEME_DESCRIPTION: notion.texte(t["description"]),
            s.THEME_FREQUENCE: notion.choix("Normal"),
            s.THEME_ACTIF: {"checkbox": True},
        }, base_id)
    return base_id, len(themes)
