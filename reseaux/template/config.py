"""Lecture de la configuration : variables d'environnement, ou fichier .env en local."""
import os
from pathlib import Path

RACINE = Path(__file__).parent


def _charger_env():
    fichier = RACINE / ".env"
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        os.environ.setdefault(cle.strip(), valeur.strip().strip('"').strip("'"))


_charger_env()


def env(cle, defaut=None, requis=False):
    valeur = os.environ.get(cle, "").strip() or defaut
    if requis and not valeur:
        raise RuntimeError(f"Variable manquante : {cle} (voir la commande /reseaux:start)")
    return valeur
