"""Petit client pour l'API Notion (lecture / écriture de la base éditoriale)."""
import re

import requests

from config import env

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


def _appel(methode, chemin, **kwargs):
    entetes = {
        "Authorization": f"Bearer {env('NOTION_TOKEN', requis=True)}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }
    r = requests.request(methode, API + chemin, headers=entetes, timeout=30, **kwargs)
    if not r.ok:
        raise RuntimeError(f"Notion {r.status_code} : {r.text[:500]}")
    return r.json()


def _base_id():
    return env("NOTION_DATABASE_ID", requis=True)


def extraire_id(lien_ou_id):
    """Accepte un lien de page Notion ou un identifiant brut."""
    chemin = lien_ou_id.split("?")[0].lower()
    trouve = re.findall(r"(?<![0-9a-f])([0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12})(?![0-9a-f])",
                        chemin)
    if not trouve:
        raise RuntimeError(f"Identifiant Notion introuvable dans : {lien_ou_id}")
    return trouve[-1].replace("-", "")


def decrire_base(base_id=None):
    return _appel("GET", f"/databases/{base_id or _base_id()}")


def creer_base(page_parent_id, titre, proprietes):
    return _appel("POST", "/databases", json={
        "parent": {"type": "page_id", "page_id": page_parent_id},
        "title": [{"type": "text", "text": {"content": titre}}],
        "properties": proprietes,
    })


def mettre_a_jour_base(base_id, proprietes):
    """Ajoute les colonnes manquantes (les colonnes existantes ne sont pas modifiées)."""
    existantes = decrire_base(base_id)["properties"]
    nouvelles = {n: d for n, d in proprietes.items() if n not in existantes and "title" not in d}
    if nouvelles:
        _appel("PATCH", f"/databases/{base_id}", json={"properties": nouvelles})


def chercher(filtre=None, base_id=None):
    corps = {"page_size": 100}
    if filtre:
        corps["filter"] = filtre
    pages = []
    while True:
        rep = _appel("POST", f"/databases/{base_id or _base_id()}/query", json=corps)
        pages += rep["results"]
        if not rep.get("has_more"):
            return pages
        corps["start_cursor"] = rep["next_cursor"]


def par_statut(statut):
    return chercher({"property": "Statut", "select": {"equals": statut}})


def creer(proprietes, base_id=None):
    return _appel("POST", "/pages", json={
        "parent": {"database_id": base_id or _base_id()},
        "properties": proprietes,
    })


def modifier(page_id, proprietes):
    return _appel("PATCH", f"/pages/{page_id}", json={"properties": proprietes})


def ajouter_blocs(page_id, blocs):
    return _appel("PATCH", f"/blocks/{page_id}/children", json={"children": blocs})


# --- Lecture d'une propriété -------------------------------------------------

def lire(page, nom):
    prop = page["properties"].get(nom)
    if prop is None:
        return None
    t = prop["type"]
    if t in ("title", "rich_text"):
        return "".join(x["plain_text"] for x in prop[t])
    if t == "select":
        return prop["select"]["name"] if prop["select"] else None
    if t == "multi_select":
        return [o["name"] for o in prop["multi_select"]]
    if t == "date":
        return prop["date"]["start"] if prop["date"] else None
    if t == "files":
        return prop["files"]
    if t == "checkbox":
        return prop["checkbox"]
    return None


# --- Écriture d'une propriété ------------------------------------------------

def texte(contenu, titre=False):
    # Notion limite chaque bloc de texte à 2000 caractères
    morceaux = [contenu[i:i + 2000] for i in range(0, len(contenu), 2000)]
    return {"title" if titre else "rich_text": [
        {"type": "text", "text": {"content": m}} for m in morceaux
    ]}


def choix(nom):
    return {"select": {"name": nom} if nom else None}


def choix_multiples(noms):
    # Les virgules sont interdites dans les options Notion
    return {"multi_select": [{"name": n.replace(",", " ").strip()[:100]} for n in noms if n.strip()]}


def fichier_externe(url, nom="visuel.jpg"):
    return {"files": [{"name": nom, "type": "external", "external": {"url": url}}]}


def date_heure(moment):
    return {"date": {"start": moment.isoformat()}}
