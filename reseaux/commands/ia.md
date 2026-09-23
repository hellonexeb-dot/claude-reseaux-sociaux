---
name: ia
description: Configure les IA de l'agent - Claude (inclus dans l'abonnement Pro/Max) ou Google Gemini (gratuit) pour les idées et les textes ; pour les images, au choix FLUX schnell gratuit (Cloudflare ou Pollinations) ou Nano Banana via fal.ai (payant, meilleure qualité) ; ImgBB pour les héberger - puis teste la génération.
---

# /reseaux:ia : textes et images

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier` et `python`. Travaille dans `dossier`.
Règles : ne demande jamais de clé dans la conversation, ne lis jamais `.env`, vérifie
une clé avec `grep -cE '^CLE=.+' .env`.

Ouvre `.env` pour l'utilisateur au début de l'étape : il y collera les 3 ou 4 clés au fur
et à mesure.

## 1. La rédaction des textes

Demande à l'utilisateur avec AskUserQuestion :

| Option | Coût | Qualité |
|---|---|---|
| **Claude (recommandé)** | Inclus dans son abonnement Claude Pro ou Max, environ 500 jetons de contexte par appel | Excellente, style naturel, respecte finement `marque.md` |
| **Gemini** | Gratuit (clé Google) | Bonne, style parfois plus « IA » |

**Claude** (2 min) :
1. Demande-lui d'ouvrir **un autre terminal** (pas `!` dans cette conversation : le jeton
   s'afficherait ici) et d'y lancer `claude setup-token`. Il suit la connexion dans le
   navigateur et obtient un jeton `sk-ant-oat…`, valable 1 an.
2. Copier le jeton dans `.env` → `CLAUDE_CODE_OAUTH_TOKEN=`.
3. Écris `TEXTES_MOTEUR=claude` dans `.env`.
   S'il utilise Claude Code avec une clé API au lieu d'un abonnement, il met plutôt sa clé
   dans `ANTHROPIC_API_KEY=` (payant à l'usage, quelques centimes par post).
4. Écris dans `state.json` → `claude_jeton_le` la date du jour : le jeton sera à renouveler
   dans un an.

**Gemini** (2 min, aussi utile en secours) :
1. Ouvrir https://aistudio.google.com/apikey avec un compte Google.
2. Cliquer sur **Create API key**, copier la clé dans `.env` → `GEMINI_API_KEY=`, puis écrire
   `TEXTES_MOTEUR=gemini` si c'est son choix principal.
   Précise honnêtement : l'offre gratuite suffit largement, mais Google peut utiliser les
   requêtes gratuites pour améliorer ses modèles. Donc pas d'informations confidentielles
   dans `marque.md`.

## 2. ImgBB, pour héberger les images (obligatoire, 2 min)

Instagram et Facebook exigent une image accessible en ligne.
1. Créer un compte sur https://imgbb.com.
2. Ouvrir https://api.imgbb.com, cliquer sur **Get API key**, puis copier la clé dans `.env` → `IMGBB_API_KEY=`.

## 3. Le générateur d'images

Demande à l'utilisateur avec AskUserQuestion :

| Option | Modèle | Coût | Qualité |
|---|---|---|---|
| **Gratuit (recommandé pour commencer)** | FLUX schnell sur Cloudflare | 0 € (≈ 100 images/jour) | Bonne pour des photos d'ambiance, détails parfois ratés (mains, objets) |
| **Gratuit sans inscription** | FLUX schnell sur Pollinations | 0 € | Même modèle, mais service parfois lent ou indisponible |
| **Payant, meilleure qualité** | Nano Banana (Google) sur fal.ai | ≈ 0,04 $ l'image, soit ≈ 1 $ pour 25 posts | Très réaliste, respecte bien les consignes |

S'il hésite ou ne veut rien payer, propose **FLUX schnell sur Cloudflare**. Il pourra
changer plus tard en modifiant une seule ligne de `.env` (`IMAGES_MOTEUR`), puis en
lançant `/reseaux:github`.

**Cloudflare** (5 min) :
1. Créer un compte sur https://dash.cloudflare.com.
2. Menu **AI** → **Workers AI** → **Use REST API**.
3. Copier l'**Account ID** dans `.env` → `CLOUDFLARE_ACCOUNT_ID=`.
4. Cliquer sur **Create a Workers AI API Token**, puis copier le jeton dans `.env` → `CLOUDFLARE_API_TOKEN=`.
5. Écris `IMAGES_MOTEUR=cloudflare` dans `.env`.

**Pollinations** : rien à créer. Écris `IMAGES_MOTEUR=pollinations` dans `.env`.

**fal.ai** (5 min) :
1. Créer un compte sur https://fal.ai, puis ajouter quelques dollars de crédit (**Billing**).
   5 $ suffisent pour plus de 100 images.
2. Ouvrir https://fal.ai/dashboard/keys, cliquer sur **Add key**, puis copier la clé dans `.env` → `FAL_KEY=`.
3. Écris `IMAGES_MOTEUR=fal` dans `.env`.
4. Facultatif : un autre modèle fal avec `FAL_MODEL=` (par défaut `fal-ai/nano-banana`,
   ou `fal-ai/flux/schnell` à environ 0,003 $ l'image, par exemple).

## 4. Test

Vérifie avec grep que les clés sont remplies, puis lance : `<python> idees`

Des idées doivent apparaître dans Notion. Montre-les à l'utilisateur (le journal de la
commande affiche les titres) et demande s'il les trouve pertinentes. Si le ton ou les
sujets ne conviennent pas, propose d'ajuster `marque.md`, supprime les idées depuis
Notion, puis relance.

Erreurs fréquentes :
- `Gemini 400 API key not valid` : la clé est mal copiée.
- `Gemini 429` : le quota gratuit est momentanément atteint, réessayer dans une minute.
- `fal.ai 403` : crédit épuisé, recharger sur fal.ai (ou repasser en `IMAGES_MOTEUR=cloudflare`).
- `Gemini 404` sur le modèle : ajouter `GEMINI_MODEL=gemini-2.5-flash` (ou le modèle
  Flash actuel) dans `.env`.

Ajoute `"ia"` à `etapes_faites`.
