"""Publication sur Facebook, Instagram (API Meta Graph) et LinkedIn (profil personnel)."""
import time

import requests

from config import env

# --- Meta : Facebook et Instagram --------------------------------------------

def _graph(methode, chemin, fichier=None, **params):
    params["access_token"] = env("META_PAGE_TOKEN", requis=True)
    url = f"https://graph.facebook.com/{env('META_GRAPH_VERSION', 'v23.0')}/{chemin}"
    if methode == "POST":
        fichiers = {"source": ("image.jpg", fichier, "image/jpeg")} if fichier else None
        r = requests.post(url, data=params, files=fichiers, timeout=120)
    else:
        r = requests.get(url, params=params, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Meta {r.status_code} : {r.text[:500]}")
    return r.json()


def publier_facebook(texte, _image_url, image):
    # Le fichier est envoyé directement : Meta n'a pas à aller chercher l'image ailleurs
    rep = _graph("POST", f"{env('META_PAGE_ID', requis=True)}/photos", fichier=image, message=texte)
    return f"https://www.facebook.com/{rep.get('post_id') or rep['id']}"


def _url_chez_meta(image):
    """Envoie l'image sur la Page en photo non publiée et temporaire, et renvoie son adresse
    sur les serveurs de Meta : Instagram la récupère alors sans délai dépassé."""
    photo = _graph("POST", f"{env('META_PAGE_ID', requis=True)}/photos", fichier=image,
                   published="false", temporary="true")
    images = _graph("GET", photo["id"], fields="images")["images"]
    return max(images, key=lambda i: i.get("width", 0))["source"]


def _creer_conteneur(compte, image_url, image, texte):
    """Instagram télécharge l'image lui-même et abandonne parfois (« délai expiré ») :
    on lui fournit alors une copie hébergée chez Meta, et on réessaie."""
    source = image_url
    for essai in range(3):
        try:
            return _graph("POST", f"{compte}/media", image_url=source, caption=texte)["id"]
        except RuntimeError as e:
            passager = "2207003" in str(e) or '"is_transient":true' in str(e)
            if not passager or essai == 2:
                raise
            if env("META_PAGE_ID"):
                source = _url_chez_meta(image)
            time.sleep(5)


def publier_instagram(texte, image_url, image):
    compte = env("INSTAGRAM_ACCOUNT_ID", requis=True)
    conteneur = _creer_conteneur(compte, image_url, image, texte)
    # Instagram télécharge et traite l'image avant de pouvoir la publier
    for _ in range(30):
        etat = _graph("GET", conteneur, fields="status_code").get("status_code")
        if etat == "FINISHED":
            break
        if etat in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram a refusé l'image (statut {etat})")
        time.sleep(3)
    else:
        raise RuntimeError("Instagram : traitement de l'image trop long")
    media = _graph("POST", f"{compte}/media_publish", creation_id=conteneur)["id"]
    return _graph("GET", media, fields="permalink").get("permalink", media)


def verifier_facebook():
    page = _graph("GET", env("META_PAGE_ID", requis=True), fields="name")
    return f"Page « {page['name']} »"


def verifier_instagram():
    compte = _graph("GET", env("INSTAGRAM_ACCOUNT_ID", requis=True), fields="username")
    return f"@{compte['username']}"


# --- LinkedIn : profil personnel --------------------------------------------

LINKEDIN_API = "https://api.linkedin.com/v2"


def _linkedin(methode, url, **kwargs):
    entetes = {"Authorization": f"Bearer {env('LINKEDIN_TOKEN', requis=True)}",
               "X-Restli-Protocol-Version": "2.0.0"}
    entetes.update(kwargs.pop("headers", {}))
    r = requests.request(methode, url, headers=entetes, timeout=60, **kwargs)
    if r.status_code == 401:
        raise RuntimeError("LinkedIn : jeton expiré ou invalide. Regénère-le (commande /reseaux:linkedin) "
                           "et mets à jour le secret LINKEDIN_TOKEN.")
    if not r.ok:
        raise RuntimeError(f"LinkedIn {r.status_code} : {r.text[:500]}")
    return r


def _auteur():
    profil = _linkedin("GET", f"{LINKEDIN_API}/userinfo").json()
    return f"urn:li:person:{profil['sub']}", profil.get("name", "")


def publier_linkedin(texte, _image_url, image):
    auteur, _ = _auteur()

    # 1. Réserver un emplacement pour l'image puis l'envoyer
    envoi = _linkedin("POST", f"{LINKEDIN_API}/assets?action=registerUpload", json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": auteur,
            "serviceRelationships": [{"relationshipType": "OWNER",
                                      "identifier": "urn:li:userGeneratedContent"}],
        }
    }).json()["value"]
    url_envoi = envoi["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    _linkedin("PUT", url_envoi, data=image, headers={"Content-Type": "image/jpeg"})

    # 2. Publier le post avec l'image
    rep = _linkedin("POST", f"{LINKEDIN_API}/ugcPosts", json={
        "author": auteur,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": texte},
            "shareMediaCategory": "IMAGE",
            "media": [{"status": "READY", "media": envoi["asset"]}],
        }},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    })
    urn = rep.headers.get("x-restli-id") or rep.json().get("id", "")
    return f"https://www.linkedin.com/feed/update/{urn}/"


def verifier_linkedin():
    _, nom = _auteur()
    return f"profil de {nom}"
