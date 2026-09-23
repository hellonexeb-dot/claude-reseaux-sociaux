"""IA : idées et textes (Claude via Claude Code, ou Google Gemini), images (fal.ai, Cloudflare Workers AI ou Pollinations), hébergement (ImgBB)."""
import base64
import io
import json
import shutil
import subprocess
import tempfile
import time
import urllib.parse
from datetime import date

import requests
from PIL import Image

import themes
from config import env

STYLE_IMAGE = (", realistic photograph, natural warm light, soft colors, full-bleed image with no border, "
               "no frame, no text, no letters, no logo, no watermark")


def _marque():
    return themes.contexte_marque()


# --- Textes : moteur -------------------------------------------------------

CONSIGNE_SYSTEME = ("Tu es un community manager francophone expérimenté. Tu réponds "
                    "uniquement avec du JSON valide, sans texte autour ni bloc de code.")


def moteur_textes():
    """Claude si Claude Code est installé (abonnement Pro/Max ou clé API), sinon Gemini."""
    choix = (env("TEXTES_MOTEUR") or "").lower()
    if choix:
        return choix
    return "claude" if shutil.which("claude") else "gemini"


def _ia_json(consigne):
    moteur = moteur_textes()
    if moteur == "claude":
        return _claude_json(consigne)
    if moteur == "gemini":
        return _gemini_json(consigne)
    raise RuntimeError(f"TEXTES_MOTEUR inconnu : {moteur} (claude ou gemini)")


def _claude_json(consigne):
    """Claude Code en mode non interactif, sans outils ni extensions : seulement la
    consigne, pour consommer le moins possible du quota de l'abonnement."""
    executable = shutil.which("claude")
    if not executable:
        raise RuntimeError("Claude Code introuvable (https://claude.com/claude-code)")
    commande = [executable, "-p", "--output-format", "json", "--tools", "",
                "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands",
                "--setting-sources", "", "--system-prompt", CONSIGNE_SYSTEME]
    if env("CLAUDE_MODEL"):
        commande += ["--model", env("CLAUDE_MODEL")]
    r = subprocess.run(commande, input=consigne, capture_output=True, text=True,
                       encoding="utf-8", timeout=600, cwd=tempfile.gettempdir())
    try:
        sortie = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Claude Code : {(r.stderr or r.stdout).strip()[:500]}")
    if sortie.get("is_error"):
        raise RuntimeError(f"Claude : {str(sortie.get('result', ''))[:500]}")
    return _extraire_json(sortie.get("result", ""))


def _extraire_json(texte):
    """Récupère le JSON d'une réponse, même entourée de texte ou d'un bloc de code."""
    debuts = [i for i in (texte.find("["), texte.find("{")) if i >= 0]
    if not debuts:
        raise RuntimeError(f"Réponse sans JSON : {texte[:300]}")
    return json.JSONDecoder().raw_decode(texte[min(debuts):])[0]


def _gemini_json(consigne):
    modele = env("GEMINI_MODEL", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
    corps = {
        "contents": [{"parts": [{"text": consigne}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
    }
    entetes = {"x-goog-api-key": env("GEMINI_API_KEY", requis=True)}
    for essai in range(4):
        r = requests.post(url, headers=entetes, json=corps, timeout=180)
        # Quota gratuit momentanément dépassé ou serveur saturé : on patiente et on réessaie
        if r.status_code in (429, 500, 503) and essai < 3:
            time.sleep(30 * (essai + 1))
            continue
        if not r.ok:
            raise RuntimeError(f"Gemini {r.status_code} : {r.text[:500]}")
        parties = r.json()["candidates"][0]["content"]["parts"]
        return json.loads("".join(p.get("text", "") for p in parties))


def proposer_idees(titres_existants, nombre):
    deja = "\n".join(f"- {t}" for t in titres_existants if t) or "(aucun)"
    consigne = f"""{_marque()}

---
Tu es le community manager de la marque décrite ci-dessus. Nous sommes le
{date.today():%d/%m/%Y} : tiens compte de la saison et des temps forts du moment si c'est pertinent.

Propose {nombre} nouvelles idées de publications pour les réseaux sociaux.
Varie les piliers de contenu. Chaque titre doit être accrocheur, concret et parler
au quotidien de la cible décrite dans le contexte de marque.
Ne propose aucun sujet qui suppose un client, un projet, un témoignage ou un chiffre réels
(« ce logo d'il y a 15 ans… », « un client nous a dit… ») : l'IA ne les connaît pas.
Ces sujets-là, c'est l'auteur qui les ajoute lui-même, avec les vrais détails.

Titres déjà utilisés (ne pas répéter ni paraphraser) :
{deja}

Réponds uniquement en JSON : une liste d'objets
{{"titre": "...", "mots_cles": ["3 à 5 mots-clés courts"], "pilier": "le nom exact d'un pilier de contenu de la marque", "angle": "1 à 2 phrases : le message clé et ce que le lecteur retient"}}"""
    idees = _ia_json(consigne)
    return idees if isinstance(idees, list) else idees.get("idees", [])


def rediger(titre, mots_cles, angle, pilier, consignes="", precedent=None):
    """precedent : {réseau: texte actuel} pour une réécriture qui part de la version existante."""
    reecriture = ""
    if precedent:
        versions = "\n\n".join(f"[{reseau}]\n{texte}" for reseau, texte in precedent.items() if texte)
        reecriture = f"""
C'est une RÉÉCRITURE. Voici la version actuelle, à améliorer en appliquant les consignes
ci-dessous (sans consigne : propose une version nettement différente, même sujet) :

{versions}
"""
    consigne = f"""{_marque()}

---
Rédige une publication sur ce sujet, déclinée pour chaque réseau.

Titre : {titre}
Mots-clés : {", ".join(mots_cles)}
Pilier : {pilier or "libre"}
Angle : {angle or "libre"}
Consignes de l'auteur (prioritaires) : {consignes or "aucune"}
{reecriture}
Consignes par réseau :
- linkedin : 800 à 1300 caractères. Première ligne = accroche forte (elle s'affiche seule).
  Paragraphes très courts séparés par une ligne vide. Termine par une question ouverte.
  3 hashtags maximum tout à la fin.
- facebook : 400 à 700 caractères. Ton conversationnel, 1 à 3 emojis. Termine par une
  invitation à commenter ou un lien vers la page la plus pertinente du site de la marque.
- instagram : 500 à 900 caractères. Première ligne accrocheuse, emojis dosés, paragraphes
  courts. Les liens ne sont pas cliquables : dire « lien en bio » si besoin.
  Termine par 10 à 15 hashtags (mélange métier, cible et zone géographique de la marque).
- prompt_image : description EN ANGLAIS d'une photo carrée qui illustre le sujet,
  selon le style d'image de la marque. Décris la scène, pas de texte dans l'image.

Réponds uniquement en JSON :
{{"linkedin": "...", "facebook": "...", "instagram": "...", "prompt_image": "..."}}"""
    return _ia_json(consigne)


# --- Images -----------------------------------------------------------------

def moteur_image():
    """Générateur choisi via IMAGES_MOTEUR, sinon le meilleur dont la clé est remplie."""
    choix = (env("IMAGES_MOTEUR") or "").lower()
    if choix:
        return choix
    if env("FAL_KEY"):
        return "fal"
    if env("CLOUDFLARE_ACCOUNT_ID") and env("CLOUDFLARE_API_TOKEN"):
        return "cloudflare"
    return "pollinations"


def generer_image(prompt):
    prompt = prompt.strip() + STYLE_IMAGE
    moteurs = {"fal": _image_fal, "cloudflare": _image_cloudflare,
               "pollinations": _image_pollinations}
    moteur = moteur_image()
    if moteur not in moteurs:
        raise RuntimeError(f"IMAGES_MOTEUR inconnu : {moteur} (fal, cloudflare ou pollinations)")
    return moteurs[moteur](prompt)


def _image_fal(prompt):
    """fal.ai (payant, environ 0,04 $ l'image) : Nano Banana de Google par défaut."""
    modele = env("FAL_MODEL", "fal-ai/nano-banana")
    if "nano-banana" in modele:
        parametres = {"aspect_ratio": "1:1"}
    else:  # FLUX et la plupart des autres modèles fal
        parametres = {"image_size": "square_hd"}
    r = requests.post(f"https://fal.run/{modele}",
                      headers={"Authorization": f"Key {env('FAL_KEY', requis=True)}"},
                      json={"prompt": prompt, "num_images": 1, "output_format": "jpeg", **parametres},
                      timeout=300)
    if not r.ok:
        raise RuntimeError(f"fal.ai {r.status_code} : {r.text[:500]}")
    image = requests.get(r.json()["images"][0]["url"], timeout=120)
    image.raise_for_status()
    return image.content


def _image_cloudflare(prompt):
    url = (f"https://api.cloudflare.com/client/v4/accounts/{env('CLOUDFLARE_ACCOUNT_ID')}"
           "/ai/run/@cf/black-forest-labs/flux-1-schnell")
    r = requests.post(url, headers={"Authorization": f"Bearer {env('CLOUDFLARE_API_TOKEN')}"},
                      json={"prompt": prompt[:2000], "steps": 8}, timeout=180)
    if not r.ok:
        raise RuntimeError(f"Cloudflare AI {r.status_code} : {r.text[:500]}")
    return base64.b64decode(r.json()["result"]["image"])


def _image_pollinations(prompt):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:1500])
    params = {"width": 1080, "height": 1080, "nologo": "true", "model": "flux",
              "seed": int(time.time())}
    r = requests.get(url, params=params, timeout=300)
    if not r.ok or not r.headers.get("content-type", "").startswith("image"):
        raise RuntimeError(f"Pollinations {r.status_code} : {r.text[:300]}")
    return r.content


def preparer_pour_reseaux(image):
    """Convertit en JPEG et recadre au centre si le format sort des limites d'Instagram (4:5 à 1.91:1)."""
    img = Image.open(io.BytesIO(image)).convert("RGB")
    largeur, hauteur = img.size
    ratio = largeur / hauteur
    if ratio < 0.8:
        nouvelle_hauteur = int(largeur / 0.8)
        haut = (hauteur - nouvelle_hauteur) // 2
        img = img.crop((0, haut, largeur, haut + nouvelle_hauteur))
    elif ratio > 1.91:
        nouvelle_largeur = int(hauteur * 1.91)
        gauche = (largeur - nouvelle_largeur) // 2
        img = img.crop((gauche, 0, gauche + nouvelle_largeur, hauteur))
    sortie = io.BytesIO()
    img.save(sortie, "JPEG", quality=92)
    return sortie.getvalue()


def heberger_image(image):
    """Met l'image en ligne (URL publique exigée par Instagram et Facebook)."""
    r = requests.post("https://api.imgbb.com/1/upload",
                      data={"key": env("IMGBB_API_KEY", requis=True),
                            "image": base64.b64encode(image).decode()},
                      timeout=120)
    if not r.ok:
        raise RuntimeError(f"ImgBB {r.status_code} : {r.text[:300]}")
    return r.json()["data"]["url"]
