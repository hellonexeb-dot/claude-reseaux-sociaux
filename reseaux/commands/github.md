---
name: github
description: Met l'agent en ligne sur GitHub (dépôt privé + GitHub Actions calé sur le rythme de publication) et y envoie les clés en secrets. À relancer après toute modification de marque.md ou de .env (rythme, renouvellement du jeton LinkedIn…).
---

# /reseaux:github : mise en ligne

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier`, `python` et `depot_github`.
Travaille dans `dossier`. Règles : ne demande jamais de clé dans la conversation, ne lis
jamais `.env`.

GitHub Actions lance l'agent **seulement quand c'est utile** : à chaque créneau de
publication (ex. mardi et jeudi à 12 h 15), un passage de sécurité le lundi à 7 h, et **à la
demande** (lien dans Notion ou `/reseaux:lancer`). Environ 30 min par mois sur les 2 000
offertes pour un dépôt privé. Rien ne tourne sur l'ordinateur de l'utilisateur.

## 1. GitHub CLI

- `gh --version` : s'il est absent, proposer de l'installer (Windows `winget install GitHub.cli`,
  macOS `brew install gh`), puis de rouvrir le terminal.
- `gh auth status` : s'il n'est pas connecté, demande à l'utilisateur de taper
  `! gh auth login -s workflow` (GitHub.com → HTTPS → navigateur). L'autorisation `workflow`
  est indispensable pour envoyer le fichier de planification. S'il est déjà connecté sans
  elle (erreur « refusing to allow an OAuth App to create or update workflow »), demande
  `! gh auth refresh -h github.com -s workflow`, puis refais le `git push`.
- Sous Windows, juste après l'installation, `gh` n'est pas encore dans le PATH de la session :
  utilise `"C:\Program Files\GitHub CLI\gh.exe"`, et ajoute ce dossier au PATH des commandes
  que tu lances (`<python> github` appelle `gh`).

## 2. Dépôt

D'abord, cale la planification sur le rythme de `.env` : `<python> planifier`
(à refaire à chaque changement de `RYTHME_JOURS` ou `RYTHME_HEURE`).

**Si `depot_github` est vide (première fois) :**
1. Vérifie que `.env` est bien ignoré : `git check-ignore .env` doit répondre `.env`. Sinon,
   arrête-toi et corrige `.gitignore`. Les clés ne doivent jamais partir sur GitHub.
2. `git init`, `git add .`, puis vérifie avec `git status` qu'aucun `.env` n'est suivi.
   Ensuite `git commit -m "Agent réseaux sociaux"`.
3. Demande un nom de dépôt (défaut : `agent-reseaux`) et crée-le **privé** :
   `gh repo create <nom> --private --source . --push`
4. Enregistre `<compte>/<nom>` dans `state.json` → `depot_github`.

**Sinon (mise à jour) :** s'il y a des changements, `git add .`, puis
`git commit -m "Mise à jour de l'agent"` et `git push`.

## 3. Secrets

Lance `<python> github` : les clés de `.env` sont copiées dans les secrets du dépôt, sans
jamais être affichées. Le script liste les noms envoyés : vérifie qu'on y trouve bien
`NOTION_TOKEN`, `NOTION_DATABASE_ID`, `GEMINI_API_KEY`, `IMGBB_API_KEY` et les clés des
réseaux choisis.

## 4. Vérification en ligne

```
gh workflow run agent.yml -f etape=verifier
```

Attends quelques secondes, récupère l'exécution (`gh run list --workflow agent.yml -L 1`),
suis-la avec `gh run watch <id>`, puis affiche le résultat avec `gh run view <id> --log`
(ne garde que les lignes ✅ / ❌). Toutes les lignes doivent être ✅.

## 5. Le lien « Lancer l'agent » dans Notion

Première fois seulement : `<python> lien-notion <depot_github>`. Un encadré
**▶️ Lancer l'agent maintenant** apparaît en haut de sa page Notion. Explique quand s'en servir :
après avoir passé un post en « À rédiger », demandé une Action (réécriture, nouvelle image),
ou validé un post dont l'heure est déjà passée. Le lien ouvre GitHub : cliquer sur
**Run workflow** (ça marche aussi depuis le navigateur du téléphone). Depuis Claude Code,
`/reseaux:lancer` fait la même chose.

Ajoute `"github"` à `etapes_faites`.
