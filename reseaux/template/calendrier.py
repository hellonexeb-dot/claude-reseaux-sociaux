"""Rythme de publication (créneaux automatiques) et contexte du calendrier éditorial."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import notion
import schema as s
import themes
from config import env

PARIS = ZoneInfo("Europe/Paris")
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def rythme():
    """Jours de publication (0 = lundi) et heure, ou None si le rythme automatique est coupé.

    Réglages dans .env : RYTHME_JOURS=mardi,jeudi (ou « aucun ») et RYTHME_HEURE=12:15.
    """
    texte = env("RYTHME_JOURS", "mardi,jeudi").lower()
    if texte in ("aucun", "non", "off"):
        return None
    abreges = {j[:3]: i for i, j in enumerate(JOURS)}
    jours = sorted({abreges[m.strip()[:3]] for m in texte.replace(";", ",").split(",")
                    if m.strip()[:3] in abreges})
    if not jours:
        raise RuntimeError(f"RYTHME_JOURS illisible : {texte} (ex. mardi,jeudi)")
    morceaux = env("RYTHME_HEURE", "12:15").lower().replace("h", ":").split(":")
    heure = time(int(morceaux[0]), int(morceaux[1]) if len(morceaux) > 1 and morceaux[1] else 0)
    return jours, heure


def creneaux(debut, fin):
    """Les créneaux du rythme compris entre deux instants."""
    r = rythme()
    if r is None:
        return []
    jours, heure = r
    resultat = []
    jour = debut.astimezone(PARIS).date()
    while jour <= fin.astimezone(PARIS).date():
        if jour.weekday() in jours:
            moment = datetime.combine(jour, heure, PARIS)
            if debut <= moment < fin:
                resultat.append(moment)
        jour += timedelta(days=1)
    return resultat


def date_de_publication(valeur):
    if not valeur:
        return None
    if "T" not in valeur:  # date sans heure : 9h, heure de Paris
        return datetime.combine(date.fromisoformat(valeur), time(9, 0), PARIS)
    moment = datetime.fromisoformat(valeur.replace("Z", "+00:00"))
    return moment if moment.tzinfo else moment.replace(tzinfo=PARIS)


def jours_occupes(pages):
    """{jour: titre} des publications déjà datées : un seul post par jour."""
    occupes = {}
    for page in pages:
        moment = date_de_publication(notion.lire(page, s.DATE))
        if moment:
            occupes[moment.astimezone(PARIS).date()] = notion.lire(page, s.TITRE)
    return occupes


def prochain_creneau(occupes):
    """Premier créneau libre, en laissant le temps de relire (24 h par défaut)."""
    debut = datetime.now(PARIS) + timedelta(hours=int(env("RYTHME_DELAI_HEURES", "24")))
    for moment in creneaux(debut, debut + timedelta(days=180)):
        if moment.date() not in occupes:
            return moment
    return None


def contexte_mois(mois):
    """Tout ce qu'il faut pour préparer le calendrier d'un mois (format AAAA-MM)."""
    annee, numero = (int(x) for x in mois.split("-"))
    debut = datetime(annee, numero, 1, tzinfo=PARIS)
    fin = datetime(annee + numero // 12, numero % 12 + 1, 1, tzinfo=PARIS)
    pages = notion.chercher()
    occupes = jours_occupes(pages)

    r = rythme()
    libres = [c.isoformat() for c in creneaux(max(debut, datetime.now(PARIS)), fin)
              if c.date() not in occupes]
    recents = sorted(pages, key=lambda p: p["created_time"], reverse=True)[:40]
    return {
        "mois": mois,
        "rythme": ({"jours": [JOURS[j] for j in r[0]], "heure": r[1].strftime("%H:%M")}
                   if r else None),
        "creneaux_libres": libres,
        "deja_prevus": [{"jour": j.isoformat(), "titre": t} for j, t in sorted(occupes.items())
                        if debut.date() <= j < fin.date()],
        "titres_recents": [notion.lire(p, s.TITRE) for p in recents],
        "themes": themes.themes_actifs(),
    }
