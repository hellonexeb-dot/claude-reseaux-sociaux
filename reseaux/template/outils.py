"""Outils d'installation : écrire dans .env, obtenir le jeton Meta permanent, envoyer les secrets sur GitHub.

Aucune clé n'est jamais affichée : elles passent du fichier .env aux services directement.
"""
import http.server
import os
import re
import secrets
import shutil
import subprocess
import urllib.parse
import webbrowser
from datetime import date, datetime, time, timedelta, timezone

import requests

import calendrier
import notion
from calendrier import PARIS
from config import RACINE, env

FICHIER_ENV = RACINE / ".env"

# Clés envoyées sur GitHub (les clés temporaires de configuration restent en local)
SECRETS_GITHUB = [
    "NOTION_TOKEN", "NOTION_DATABASE_ID", "NOTION_THEMES_ID", "TEXTES_MOTEUR", "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_API_KEY", "CLAUDE_MODEL", "GEMINI_API_KEY", "GEMINI_MODEL", "IMGBB_API_KEY",
    "IMAGES_MOTEUR", "FAL_KEY", "FAL_MODEL", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "META_PAGE_ID", "META_PAGE_TOKEN",
    "INSTAGRAM_ACCOUNT_ID", "LINKEDIN_TOKEN", "RESEAUX_ACTIFS", "MIN_IDEES", "IDEES_PAR_LOT",
    "RYTHME_JOURS", "RYTHME_HEURE", "RYTHME_DELAI_HEURES",
]


def ecrire_env(cle, valeur):
    """Ajoute ou remplace une ligne CLE=valeur dans .env."""
    lignes = FICHIER_ENV.read_text(encoding="utf-8").splitlines() if FICHIER_ENV.exists() else []
    motif = re.compile(rf"^\s*#?\s*{re.escape(cle)}\s*=")
    nouvelle = f"{cle}={valeur}"
    for i, ligne in enumerate(lignes):
        if motif.match(ligne):
            lignes[i] = nouvelle
            break
    else:
        lignes.append(nouvelle)
    FICHIER_ENV.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    os.environ[cle] = valeur


def lire_env_fichier():
    valeurs = {}
    if FICHIER_ENV.exists():
        for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#") and "=" in ligne:
                cle, valeur = ligne.split("=", 1)
                valeur = valeur.strip().strip('"').strip("'")
                if valeur:
                    valeurs[cle.strip()] = valeur
    return valeurs


# --- Meta -------------------------------------------------------------------

def configurer_meta(page_id=None):
    """Transforme le jeton utilisateur de l'Explorateur Graph (valable 1 h) en jeton
    de Page permanent, et retrouve le compte Instagram relié."""
    version = env("META_GRAPH_VERSION", "v23.0")
    graph = f"https://graph.facebook.com/{version}"

    r = requests.get(f"{graph}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": env("META_APP_ID", requis=True),
        "client_secret": env("META_APP_SECRET", requis=True),
        "fb_exchange_token": env("META_USER_TOKEN", requis=True),
    }, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Échange du jeton refusé : {r.text[:300]}\n"
                           "Le jeton de l'Explorateur expire au bout d'1 h : regénère-le.")
    jeton_long = r.json()["access_token"]

    r = requests.get(f"{graph}/me/accounts", params={
        "access_token": jeton_long,
        "fields": "id,name,access_token,instagram_business_account{id,username}",
    }, timeout=30)
    r.raise_for_status()
    pages = r.json().get("data", [])
    if not pages:
        raise RuntimeError("Aucune Page Facebook trouvée : as-tu bien coché ta Page lors de la génération du jeton ?")

    if page_id is None and len(pages) > 1:
        print("Plusieurs Pages trouvées, relance avec l'identifiant voulu :")
        for p in pages:
            print(f"   python agent.py meta {p['id']}   ({p['name']})")
        return
    page = next((p for p in pages if p["id"] == page_id), None) if page_id else pages[0]
    if page is None:
        raise RuntimeError(f"Page {page_id} introuvable parmi : {', '.join(p['name'] for p in pages)}")

    ecrire_env("META_PAGE_ID", page["id"])
    ecrire_env("META_PAGE_TOKEN", page["access_token"])
    print(f"✅ Page Facebook : {page['name']} (jeton permanent enregistré dans .env)")

    instagram = page.get("instagram_business_account")
    if instagram:
        ecrire_env("INSTAGRAM_ACCOUNT_ID", instagram["id"])
        print(f"✅ Instagram : @{instagram.get('username', instagram['id'])}")
    else:
        print("⚠️  Aucun compte Instagram professionnel relié à cette Page.")

    # Le jeton temporaire n'a plus d'utilité
    ecrire_env("META_USER_TOKEN", "")


# --- LinkedIn ---------------------------------------------------------------

LINKEDIN_PORT = 8765
LINKEDIN_REDIRECTION = f"http://localhost:{LINKEDIN_PORT}/callback"


def connecter_linkedin():
    """Connexion OAuth à LinkedIn sans le générateur de jetons : ouvre la page d'autorisation,
    récupère le code sur un petit serveur local, l'échange contre un jeton (60 jours) et
    l'écrit dans .env."""
    client_id = env("LINKEDIN_CLIENT_ID", requis=True)
    client_secret = env("LINKEDIN_CLIENT_SECRET", requis=True)
    etat = secrets.token_urlsafe(24)
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id, "redirect_uri": LINKEDIN_REDIRECTION,
        "state": etat, "scope": "openid profile w_member_social",
    })
    recu = {}

    class Retour(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            adresse = urllib.parse.urlparse(self.path)
            if adresse.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            recu.update({k: v[0] for k, v in urllib.parse.parse_qs(adresse.query).items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>Connexion LinkedIn reçue ✅</h2><p>Tu peux fermer cet onglet "
                             "et revenir à Claude Code.</p>".encode("utf-8"))

        def log_message(self, *args):
            pass

    serveur = http.server.HTTPServer(("127.0.0.1", LINKEDIN_PORT), Retour)
    serveur.timeout = 5
    print("Ouverture de LinkedIn dans le navigateur. Si rien ne s'ouvre, copie cette adresse :")
    print(f"   {url}", flush=True)
    webbrowser.open(url)
    limite = datetime.now() + timedelta(minutes=5)
    while not recu and datetime.now() < limite:
        serveur.handle_request()
    serveur.server_close()

    if not recu:
        raise RuntimeError("Pas de réponse de LinkedIn en 5 minutes : relance la commande.")
    if recu.get("state") != etat:
        raise RuntimeError("Réponse LinkedIn inattendue (paramètre state différent) : relance la commande.")
    if "error" in recu:
        raise RuntimeError(f"LinkedIn a refusé : {recu.get('error_description', recu['error'])}")

    r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code", "code": recu["code"],
        "redirect_uri": LINKEDIN_REDIRECTION,
        "client_id": client_id, "client_secret": client_secret,
    }, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Échange du code refusé par LinkedIn : {r.text[:300]}")
    reponse = r.json()
    ecrire_env("LINKEDIN_TOKEN", reponse["access_token"])
    expire = datetime.now() + timedelta(seconds=int(reponse.get("expires_in", 5184000)))
    print(f"✅ Jeton LinkedIn enregistré dans .env (valable jusqu'au {expire:%d/%m/%Y}).")


# --- GitHub -----------------------------------------------------------------

def envoyer_secrets_github():
    """Copie les valeurs de .env dans les secrets du dépôt GitHub via la commande gh."""
    if not shutil.which("gh"):
        raise RuntimeError("La commande gh (GitHub CLI) est introuvable : https://cli.github.com")
    valeurs = lire_env_fichier()
    envoyes = []
    for cle in SECRETS_GITHUB:
        if cle in valeurs:
            subprocess.run(["gh", "secret", "set", cle], input=valeurs[cle], text=True,
                           cwd=RACINE, check=True, capture_output=True)
            envoyes.append(cle)
    print(f"✅ {len(envoyes)} secrets envoyés sur GitHub : {', '.join(envoyes)}")


# --- Planification ----------------------------------------------------------

WORKFLOW = RACINE / ".github" / "workflows" / "agent.yml"
DEBUT_PLANIF = "  # >>> planification"
FIN_PLANIF = "  # <<< planification"


def _crons(jours, heure):
    """Expressions cron (UTC) pour une heure de Paris, en été comme en hiver."""
    groupes = {}
    for reference in (date(2026, 1, 5), date(2026, 7, 6)):  # deux lundis : hiver, été
        for jour in jours:
            local = datetime.combine(reference + timedelta(days=jour), heure, PARIS)
            utc = local.astimezone(timezone.utc)
            jour_cron = (utc.weekday() + 1) % 7  # cron : 0 = dimanche
            groupes.setdefault((utc.minute, utc.hour), set()).add(jour_cron)
    return [f"{m} {h} * * {','.join(str(j) for j in sorted(js))}"
            for (m, h), js in sorted(groupes.items(), key=lambda x: (x[0][1], x[0][0]))]


def planifier_workflow():
    """Réécrit la planification du workflow GitHub à partir du rythme de publication :
    un passage à chaque créneau + un passage de sécurité le lundi à 7 h."""
    r = calendrier.rythme()
    if r:
        jours, heure = r
        crons = _crons(jours, heure) + _crons([0], time(7, 0))
        noms = ", ".join(calendrier.JOURS[j][:3] + "." for j in jours)
        resume = (f"Publication aux créneaux ({noms} {heure:%H:%M}, heure de Paris, été comme hiver)\n"
                  "  # + passage de sécurité le lundi à 07:00.")
    else:
        # Dates choisies à la main : un passage par heure en journée
        crons = ["7 5-19 * * *"]
        resume = "Rythme coupé : un passage par heure, de 7 h à 21 h (heure de Paris)."

    bloc = [DEBUT_PLANIF + " : générée par `python agent.py planifier` à partir du rythme",
            f"  # {resume}", "  schedule:"] + [f'    - cron: "{c}"' for c in crons] + [FIN_PLANIF]
    texte = WORKFLOW.read_text(encoding="utf-8")
    debut = texte.index(DEBUT_PLANIF)
    fin = texte.index(FIN_PLANIF) + len(FIN_PLANIF)
    WORKFLOW.write_text(texte[:debut] + "\n".join(bloc) + texte[fin:], encoding="utf-8")
    print("✅ Planification mise à jour :")
    print("   " + resume.replace("\n  # ", "\n   "))
    print("   Pense à pousser le changement sur GitHub (/reseaux:github).")


def ajouter_lien_notion(depot):
    """Ajoute en haut de la page Notion un lien pour lancer l'agent à la demande."""
    parent = notion.decrire_base()["parent"]
    if parent.get("type") != "page_id":
        raise RuntimeError("La base n'est pas dans une page : lien non ajouté.")
    url = f"https://github.com/{depot}/actions/workflows/agent.yml"
    notion.ajouter_blocs(parent["page_id"], [{
        "object": "block", "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "▶️"},
            "rich_text": [
                {"type": "text", "text": {"content": "Lancer l'agent maintenant", "link": {"url": url}},
                 "annotations": {"bold": True}},
                {"type": "text", "text": {"content": " : ouvre GitHub, puis « Run workflow ». "
                 "À faire après avoir demandé une rédaction, une réécriture ou une nouvelle "
                 "image, ou validé un post dont l'heure est passée."}},
            ],
        },
    }])
    print(f"✅ Lien « Lancer l'agent maintenant » ajouté dans la page Notion ({url})")
