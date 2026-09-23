"""Agent réseaux sociaux : idées, rédaction et publication pilotées depuis Notion.

Usage :
    python agent.py tout        publier ce qui est dû, rédiger, proposer des idées (par défaut)
    python agent.py idees       proposer de nouvelles idées si le stock est bas
    python agent.py rediger     rédiger textes + image des lignes « À rédiger »
    python agent.py publier     publier les lignes « Validé » dont la date est passée
    python agent.py verifier    tester toutes les connexions

Calendrier éditorial :
    python agent.py calendrier <AAAA-MM>   créneaux libres et contexte du mois (JSON)
    python agent.py importer <plan.json>   créer dans Notion les posts d'un calendrier

Installation :
    python agent.py installer <lien de la page Notion>   créer la base éditoriale
    python agent.py linkedin            se connecter à LinkedIn (jeton de 60 jours)
    python agent.py meta [id de page]   obtenir le jeton Facebook/Instagram permanent
    python agent.py github              envoyer les clés de .env dans les secrets GitHub
    python agent.py planifier           caler les passages GitHub sur le rythme de publication
    python agent.py lien-notion <compte/depot>   lien « Lancer l'agent » dans la page Notion
"""
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import requests

import calendrier
import ia
import notion
import outils
import reseaux
import schema as s
import themes
from config import env

PARIS = calendrier.PARIS
PUBLIEURS = {
    s.LINKEDIN: reseaux.publier_linkedin,
    s.FACEBOOK: reseaux.publier_facebook,
    s.INSTAGRAM: reseaux.publier_instagram,
}


def reseaux_actifs():
    choisis = env("RESEAUX_ACTIFS", "linkedin,facebook,instagram").lower()
    return [r for r in s.TOUS_RESEAUX if r.lower() in choisis]


def log(message):
    print(message, flush=True)


def signaler_erreur(page, message):
    log(f"   ❌ {message}")
    notion.modifier(page["id"], {
        s.STATUT: notion.choix(s.ERREUR),
        s.ERREUR_DETAIL: notion.texte(message[:1900]),
    })


# --- 1. Idées ---------------------------------------------------------------

def etape_idees():
    stock = len(notion.par_statut(s.IDEE))
    minimum = int(env("MIN_IDEES", "5"))
    if stock >= minimum:
        log(f"💡 Idées : {stock} en attente, rien à faire.")
        return
    titres = [notion.lire(p, s.TITRE) for p in notion.chercher()]
    idees = ia.proposer_idees(titres, int(env("IDEES_PAR_LOT", "5")))
    for idee in idees:
        creer_idee(idee, s.IDEE)
        log(f"💡 Nouvelle idée : {idee['titre']}")


def creer_idee(idee, statut, quand=None):
    props = {
        s.TITRE: notion.texte(idee["titre"], titre=True),
        s.STATUT: notion.choix(statut),
        s.MOTS_CLES: notion.choix_multiples(idee.get("mots_cles", [])),
        s.ANGLE: notion.texte(idee.get("angle", "")),
        s.RESEAUX: notion.choix_multiples(reseaux_actifs()),
    }
    if idee.get("pilier"):
        props[s.PILIER] = notion.choix(idee["pilier"])
    if idee.get("consignes"):
        props[s.CONSIGNES] = notion.texte(idee["consignes"])
    if quand:
        props[s.DATE] = notion.date_heure(quand)
    notion.creer(props)


# --- 2. Rédaction -----------------------------------------------------------

def etape_rediger():
    """Rédige les lignes « À rédiger » et traite les actions demandées (colonne Action)."""
    pages = notion.chercher({"or": [
        {"property": s.STATUT, "select": {"equals": s.A_REDIGER}},
        {"property": s.ACTION, "select": {"is_not_empty": True}},
    ]})
    log(f"✍️  Rédaction : {len(pages)} publication(s) à rédiger ou à mettre à jour.")
    occupes = calendrier.jours_occupes(notion.chercher()) if pages else {}
    for page in pages:
        titre = notion.lire(page, s.TITRE)
        action = notion.lire(page, s.ACTION)
        log(f" → {titre}{f' ({action})' if action else ''}")
        if notion.lire(page, s.STATUT) == s.PUBLIE:
            log("   · déjà publiée : action ignorée")
            notion.modifier(page["id"], {s.ACTION: notion.choix(None)})
            continue
        try:
            quand = rediger(page, titre, occupes, action)
            prevue = f", prévue le {quand.astimezone(PARIS):%d/%m à %H:%M}" if quand else ""
            log(f"   ✅ prête à valider{prevue}")
        except Exception as e:
            signaler_erreur(page, f"Rédaction : {e}")


def rediger(page, titre, occupes, action=None):
    """Complète les champs vides, ou refait ce que demande l'action (réécriture en tenant
    compte des consignes, nouvelle image). Sans date, le post reçoit le prochain créneau
    libre du rythme de publication. Renvoie la date prévue."""
    maj = {s.ACTION: notion.choix(None)}
    refaire_texte = action in (s.REECRIRE, s.TOUT_REFAIRE)
    refaire_image = action in (s.NOUVELLE_IMAGE, s.TOUT_REFAIRE)
    textes = {r: (notion.lire(page, c) or "").strip() for r, c in s.TEXTE_PAR_RESEAU.items()}
    manquants = [c for r, c in s.TEXTE_PAR_RESEAU.items() if refaire_texte or not textes[r]]
    prompt_image = (notion.lire(page, s.PROMPT_IMAGE) or "").strip()

    if manquants or not prompt_image:
        contenu = ia.rediger(titre, notion.lire(page, s.MOTS_CLES) or [],
                             notion.lire(page, s.ANGLE), notion.lire(page, s.PILIER),
                             consignes=(notion.lire(page, s.CONSIGNES) or "").strip(),
                             precedent=textes if refaire_texte and any(textes.values()) else None)
        for reseau, colonne in s.TEXTE_PAR_RESEAU.items():
            if colonne in manquants:
                maj[colonne] = notion.texte(contenu[reseau.lower()].strip())
        if not prompt_image:
            prompt_image = contenu["prompt_image"].strip()
            maj[s.PROMPT_IMAGE] = notion.texte(prompt_image)

    if refaire_image or not notion.lire(page, s.IMAGE):
        image = ia.preparer_pour_reseaux(ia.generer_image(prompt_image))
        maj[s.IMAGE] = notion.fichier_externe(ia.heberger_image(image))

    if not notion.lire(page, s.RESEAUX):
        maj[s.RESEAUX] = notion.choix_multiples(reseaux_actifs())

    quand = calendrier.date_de_publication(notion.lire(page, s.DATE))
    if quand is None:
        quand = calendrier.prochain_creneau(occupes)
        if quand:
            maj[s.DATE] = notion.date_heure(quand)
            occupes[quand.date()] = titre

    maj[s.STATUT] = notion.choix(s.A_VALIDER)
    maj[s.ERREUR_DETAIL] = notion.texte("")
    notion.modifier(page["id"], maj)
    return quand


# --- 3. Publication ---------------------------------------------------------

def etape_publier():
    maintenant = datetime.now(timezone.utc)
    pages = notion.par_statut(s.VALIDE)
    log(f"🚀 Publication : {len(pages)} publication(s) validée(s).")
    for page in pages:
        titre = notion.lire(page, s.TITRE)
        quand = calendrier.date_de_publication(notion.lire(page, s.DATE))
        if quand is None:
            log(f" · {titre} : pas de date de publication, ignorée.")
            continue
        if quand > maintenant:
            log(f" · {titre} : prévue le {quand.astimezone(PARIS):%d/%m à %H:%M}.")
            continue
        log(f" → {titre}")
        try:
            publier(page)
        except Exception as e:
            signaler_erreur(page, f"Publication : {e}")


def image_de(page):
    """Récupère l'image de la ligne (générée ou déposée à la main), la met au format
    accepté par les réseaux et l'héberge à une URL publique."""
    fichiers = notion.lire(page, s.IMAGE)
    if not fichiers:
        raise RuntimeError("aucune image dans la colonne Image")
    f = fichiers[0]
    source = f["external"]["url"] if f["type"] == "external" else f["file"]["url"]
    r = requests.get(source, timeout=120)
    r.raise_for_status()
    image = ia.preparer_pour_reseaux(r.content)
    return ia.heberger_image(image), image


def publier(page):
    voulus = notion.lire(page, s.RESEAUX) or []
    deja = set(notion.lire(page, s.PUBLIE_SUR) or [])
    liens = (notion.lire(page, s.LIENS) or "").strip()
    image_url, image = image_de(page)

    erreurs = []
    for reseau in voulus:
        if reseau in deja or reseau not in PUBLIEURS:
            continue
        try:
            contenu = (notion.lire(page, s.TEXTE_PAR_RESEAU[reseau]) or "").strip()
            if not contenu:
                raise RuntimeError("texte vide")
            lien = PUBLIEURS[reseau](contenu, image_url, image)
        except Exception as e:
            erreurs.append(f"{reseau} : {e}")
            log(f"   ❌ {reseau} : {e}")
            continue
        # Enregistré tout de suite pour ne jamais republier deux fois
        deja.add(reseau)
        liens = f"{liens}\n{reseau} : {lien}".strip()
        notion.modifier(page["id"], {
            s.PUBLIE_SUR: notion.choix_multiples(sorted(deja)),
            s.LIENS: notion.texte(liens),
        })
        log(f"   ✅ {reseau} : {lien}")

    notion.modifier(page["id"], {
        s.STATUT: notion.choix(s.ERREUR if erreurs else s.PUBLIE),
        s.ERREUR_DETAIL: notion.texte("\n".join(erreurs)[:1900]),
    })


# --- Outils -----------------------------------------------------------------

def etape_verifier():
    def tester_notion():
        base = notion.decrire_base()
        manquantes = [c for c in (s.ACTION, s.CONSIGNES) if c not in base["properties"]]
        if manquantes:
            raise RuntimeError(f"colonnes absentes : {', '.join(manquantes)} "
                               "(relance `installer` pour les ajouter)")
        source = "base Notion" if env("NOTION_THEMES_ID") else "marque.md"
        return (f"base « {base['title'][0]['plain_text']} », "
                f"{len(themes.themes_actifs())} thèmes actifs ({source})")

    def tester_textes():
        reponse = ia._ia_json('Réponds exactement {"ok": true}')
        return f"{ia.moteur_textes()}, réponse {reponse}"

    def tester_images():
        env("IMGBB_API_KEY", requis=True)
        noms = {"fal": f"fal.ai ({env('FAL_MODEL', 'fal-ai/nano-banana')})",
                "cloudflare": "Cloudflare Workers AI (FLUX)", "pollinations": "Pollinations (sans clé)"}
        moteur = ia.moteur_image()
        return f"{noms.get(moteur, moteur)}, hébergement ImgBB"

    tests = {"Notion": tester_notion, "Textes": tester_textes, "Images": tester_images}
    verifications = {
        s.FACEBOOK: reseaux.verifier_facebook,
        s.INSTAGRAM: reseaux.verifier_instagram,
        s.LINKEDIN: reseaux.verifier_linkedin,
    }
    for reseau in reseaux_actifs():
        tests[reseau] = verifications[reseau]
    echecs = 0
    for nom, test in tests.items():
        try:
            log(f"✅ {nom} : {test()}")
        except Exception as e:
            echecs += 1
            log(f"❌ {nom} : {e}")
    if echecs:
        raise RuntimeError(f"{echecs} connexion(s) à corriger")


def importer_calendrier(fichier):
    """Crée les posts d'un calendrier préparé avec /reseaux:calendrier.
    Format : {"statut": "a_rediger" | "idee", "posts": [{"date", "titre", "mots_cles", "consignes",
    "pilier", "angle"}]}"""
    plan = json.loads(Path(fichier).read_text(encoding="utf-8"))
    statut = s.A_REDIGER if plan.get("statut") == "a_rediger" else s.IDEE
    for post in plan["posts"]:
        quand = calendrier.date_de_publication(post["date"])
        creer_idee(post, statut, quand)
        log(f"📅 {quand:%d/%m %H:%M} : {post['titre']}")
    log(f"✅ {len(plan['posts'])} publication(s) ajoutée(s) en « {statut} ».")


def installer(lien_page):
    """Crée ce qui manque dans la page Notion : la base des publications (ou ses nouvelles
    colonnes) et la base des thèmes. Peut être relancé sans risque."""
    parent = notion.extraire_id(lien_page)
    if env("NOTION_DATABASE_ID"):
        notion.mettre_a_jour_base(env("NOTION_DATABASE_ID"), s.PROPRIETES)
        log("✅ Base des publications : colonnes à jour.")
    else:
        base = notion.creer_base(parent, "Publications réseaux sociaux", s.PROPRIETES)
        outils.ecrire_env("NOTION_DATABASE_ID", base["id"].replace("-", ""))
        log("✅ Base des publications créée.")
    if env("NOTION_THEMES_ID"):
        log("✅ Base des thèmes : déjà présente.")
    else:
        base_id, nombre = themes.creer_base_themes(parent)
        outils.ecrire_env("NOTION_THEMES_ID", base_id)
        log(f"✅ Base des thèmes créée, avec les {nombre} thèmes de marque.md.")
    log("   Identifiants enregistrés dans .env.")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    commande = sys.argv[1] if len(sys.argv) > 1 else "tout"
    argument = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    if commande == "installer":
        if not argument:
            sys.exit("Usage : python agent.py installer <lien de la page Notion>")
        installer(argument)
        return
    if commande == "linkedin":
        outils.connecter_linkedin()
        return
    if commande == "meta":
        outils.configurer_meta(argument)
        return
    if commande == "github":
        outils.envoyer_secrets_github()
        return
    if commande == "planifier":
        outils.planifier_workflow()
        return
    if commande == "lien-notion":
        if not argument:
            sys.exit("Usage : python agent.py lien-notion <compte/depot>")
        outils.ajouter_lien_notion(argument)
        return
    if commande == "calendrier":
        mois = argument or f"{datetime.now(PARIS):%Y-%m}"
        print(json.dumps(calendrier.contexte_mois(mois), ensure_ascii=False, indent=2))
        return
    if commande == "importer":
        if not argument:
            sys.exit("Usage : python agent.py importer <plan.json>")
        importer_calendrier(argument)
        return

    etapes = {"idees": etape_idees, "rediger": etape_rediger,
              "publier": etape_publier, "verifier": etape_verifier}
    a_lancer = ["publier", "rediger", "idees"] if commande == "tout" else [commande]
    if any(e not in etapes for e in a_lancer):
        sys.exit(__doc__)

    echec = False
    for nom in a_lancer:
        try:
            etapes[nom]()
        except Exception:
            traceback.print_exc()
            echec = True
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
