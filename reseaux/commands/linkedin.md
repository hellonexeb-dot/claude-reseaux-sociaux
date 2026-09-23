---
name: linkedin
description: Connecte le profil LinkedIn personnel de l'utilisateur (application LinkedIn, produits Share on LinkedIn + OpenID, jeton de 60 jours). Sert aussi à renouveler le jeton quand il expire.
---

# /reseaux:linkedin : publier sur son profil

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier` et `python`. Travaille dans `dossier`.
Règles : ne demande jamais de clé dans la conversation, ne lis jamais `.env`, vérifie
une clé avec `grep -cE '^CLE=.+' .env`.

**Renouvellement** : si l'étape `linkedin` est déjà dans `etapes_faites`, l'utilisateur
vient sûrement renouveler son jeton. Va directement au point 3, puis au point 5.

## 1. Page entreprise (prérequis LinkedIn)

LinkedIn exige que toute application soit rattachée à une **page entreprise**, même pour
publier sur un profil perso. Demande à l'utilisateur s'il en a une. Sinon : LinkedIn →
**Pour les entreprises** → **Créer une page entreprise** (5 min, nom + logo suffisent).

## 2. Créer l'application

1. Ouvrir https://www.linkedin.com/developers/apps, puis cliquer sur **Create app**.
2. Nom : « Agent réseaux sociaux ». Page LinkedIn : sa page entreprise. Ajouter un logo, cocher les conditions et valider.
3. Onglet **Settings** → **Verify** à côté de la page : ouvrir le lien généré en tant
   qu'admin de la page et approuver.
4. Onglet **Products** → **Request access** sur ces deux produits (accordés immédiatement) :
   - **Share on LinkedIn**
   - **Sign In with LinkedIn using OpenID Connect**

## 3. Générer le jeton

N'utilise pas le générateur de jetons de LinkedIn : il échoue souvent (« state parameter
was modified »). L'agent fait la connexion lui-même.

Première fois seulement :
1. Onglet **Auth** de l'application → **Authorized redirect URLs for your app** → crayon ✏️ →
   **+ Add redirect URL** → `http://localhost:8765/callback` → **Update**.
2. Toujours dans l'onglet **Auth** : copier le **Client ID** dans `.env` → `LINKEDIN_CLIENT_ID=`
   et le **Primary Client Secret** (icône œil) → `LINKEDIN_CLIENT_SECRET=`.

Puis (et à chaque renouvellement) : lance `<python> linkedin` **en arrière-plan**, récupère
l'adresse `https://www.linkedin.com/oauth/...` affichée dans sa sortie et ouvre-la pour
l'utilisateur dans son navigateur (`Start-Process "<url>"` sous Windows, `open` sous macOS,
`xdg-open` sous Linux) : le lancement automatique du navigateur ne marche pas toujours depuis
Claude Code. Il clique sur **Autoriser** ; le jeton est écrit tout seul dans `.env`.
En cas de « Pas de réponse en 5 minutes », relance simplement.

## 4. Tester

Vérifie avec grep que la clé est remplie, puis lance `<python> verifier`.
La ligne LinkedIn doit afficher « ✅ LinkedIn : profil de <nom> ».

## 5. Retenir la date

Écris la date du jour dans `.reseaux/state.json` → `linkedin_jeton_le`.

Explique clairement : **ce jeton expire au bout de 60 jours.** Il faudra relancer
`/reseaux:linkedin` (1 minute : un clic sur « Autoriser »), puis `/reseaux:github`.
Propose de créer un rappel à J+55 dans son agenda. Si le jeton expire quand même, les
publications LinkedIn passent en ⚠️ Erreur avec un message clair, et rien n'est perdu.

Si c'était un renouvellement et que le dépôt GitHub existe déjà, enchaîne avec
`/reseaux:github` pour mettre le secret à jour.

Ajoute `"linkedin"` à `etapes_faites`.
