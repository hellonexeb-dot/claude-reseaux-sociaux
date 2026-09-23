# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ce qu'est ce dépôt

Un plugin Claude Code (`reseaux`), publié dans sa propre marketplace (`reseaux-sociaux`). Il
installe pas à pas, en conversation, un agent Python qui propose, rédige, illustre et publie des
posts LinkedIn, Facebook et Instagram, validés dans Notion. Public visé : indépendants et TPE,
pas des développeurs. Code, commentaires, commandes et documentation sont en français.

Le dépôt contient deux choses très différentes :

- **`reseaux/commands/*.md`** : les commandes `/reseaux:*`. Ce sont des instructions que Claude
  suit en dialoguant avec l'utilisateur. `start.md` orchestre les autres via l'outil Skill et
  tient la progression dans `.reseaux/state.json` (clés : `etapes_faites`, `dossier`, `python`,
  `depot_github`, `rythme`, `linkedin_jeton_le`…), dans le dossier de l'utilisateur.
- **`reseaux/template/`** : l'agent lui-même. Il est **copié** chez l'utilisateur
  (`${CLAUDE_PLUGIN_ROOT}/template/`), qui le pousse dans son propre dépôt GitHub privé, où il
  tourne sur GitHub Actions. Une modification du template **n'atteint pas** les agents déjà
  installés : il n'existe aucun mécanisme de mise à jour.

## Valider une modification

Il n'y a ni tests ni linter. Avant de publier :

```
claude plugin validate .            # marketplace.json
claude plugin validate reseaux      # plugin.json
```

Il faut aussi `py_compile` les fichiers de `reseaux/template/*.py` et vérifier que
`template/.github/workflows/agent.yml` reste un YAML valide.

Le seul vrai test est un parcours complet. On installe la copie locale
(`claude plugin marketplace add ./`, `claude plugin install reseaux@reseaux-sociaux`, puis
`/reload-plugins`) et on lance `/reseaux:start` dans un dossier vide. Après une modification :
`claude plugin marketplace update reseaux-sociaux`. Dans un agent installé,
`python agent.py verifier` teste toutes les connexions réelles.

Pour une publication : incrémenter la version à **trois endroits** (`reseaux/.claude-plugin/plugin.json`,
et `metadata.version` + `plugins[0].version` dans `.claude-plugin/marketplace.json`), puis
compléter `CHANGELOG.md`.

## Ce qui doit rester cohérent

- **Variables d'environnement.** Une variable ajoutée ou renommée doit l'être partout :
  - `template/.env.example` ;
  - `SECRETS_GITHUB` dans `template/outils.py`, qui liste ce qui est copié vers GitHub ;
  - le bloc `env:` de `template/.github/workflows/agent.yml` ;
  - le tableau « Réglages » du README ;
  - les commandes qui la mentionnent.

  Les variables purement locales (`META_APP_*`, `META_USER_TOKEN`, `LINKEDIN_CLIENT_*`) ne vont
  **pas** dans GitHub.
- **Sous-commandes de `agent.py`** (`installer`, `linkedin`, `meta`, `github`, `planifier`,
  `lien-notion`, `calendrier`, `importer`…) : elles sont appelées par les commandes `.md` sous la
  forme `<python> <sous-commande>`, `<python>` étant la commande Python enregistrée dans l'état.
- **Schéma Notion** (`template/schema.py`) : les noms de colonnes et de statuts sont le contrat
  avec les bases existantes des utilisateurs. `installer` peut être relancé : il crée ce qui
  manque et ajoute les colonnes nouvelles (`notion.mettre_a_jour_base`). En revanche, renommer une
  colonne casse les installations existantes.
- **Sécurité, dans toutes les commandes** : ne jamais demander de clé dans la conversation, ne
  jamais lire le `.env` de l'utilisateur. On vérifie une clé avec `grep -cE '^CLE=.+' .env`,
  l'utilisateur colle lui-même ses clés, et les scripts écrivent dans `.env` via
  `outils.ecrire_env`.

## Architecture de l'agent (`reseaux/template/`)

Notion est la machine à états :
💡 Idée → ✍️ À rédiger → 👀 À valider → ✅ Validé → 🚀 Publié, ou ⚠️ Erreur.
L'API Notion est utilisée en version `2022-06-28`, avec les endpoints `databases`.
`agent.py tout` enchaîne publier, puis rédiger, puis proposer des idées.

- **Rédaction** : traite les lignes « À rédiger » **et** celles dont la colonne `Action` est
  remplie (réécrire le texte, nouvelle image, tout refaire, guidés par la colonne `Consignes`).
  Sans action, seuls les champs vides sont complétés. Une ligne sans date reçoit le prochain
  créneau libre du rythme (`calendrier.py`, fuseau Europe/Paris, un post par jour au maximum).
- **Publication** : réseau par réseau. `Publié sur` est écrit **après chaque succès**, pour qu'une
  reprise après erreur ne republie jamais sur un réseau déjà servi.
- **Textes** (`ia.py`) : `TEXTES_MOTEUR=claude` appelle `claude -p` avec un contexte minimal
  (`--tools ""`, `--setting-sources ""`, `--strict-mcp-config`, `--disable-slash-commands`) :
  environ 500 jetons au lieu de près de 100 000. Ne **pas** utiliser `--bare`, qui ignore
  `CLAUDE_CODE_OAUTH_TOKEN`, le jeton d'abonnement utilisé sur GitHub Actions. Gemini sert
  d'alternative. Les réponses sont en JSON, extrait par `_extraire_json`.
- **Contexte de marque** : `themes.contexte_marque()` renvoie le `marque.md` de l'utilisateur,
  dont la section « Piliers » est remplacée par les thèmes actifs de la base Notion « Thèmes de
  contenu ». Une fois cette base créée, les thèmes se gèrent dans Notion.
- **Images** : fal.ai, Cloudflare Workers AI ou Pollinations, puis `preparer_pour_reseaux`
  (JPEG, ratio accepté par Instagram), puis hébergement sur ImgBB.
- **Planification** : le bloc `schedule:` du workflow, entre les marqueurs `# >>> planification`
  et `# <<<`, est **généré** par `outils.planifier_workflow` à partir du rythme : deux crons par
  créneau (heure d'été et d'hiver de Paris), plus un passage le lundi à 7 h. En dehors de ça,
  l'agent se lance à la demande (`workflow_dispatch`).

## Pièges connus (découverts en test réel)

- **LinkedIn** : le générateur de jetons officiel échoue (« state parameter was modified »).
  L'agent fait donc l'OAuth lui-même (`python agent.py linkedin`), avec retour sur
  `http://localhost:8765/callback`. Le navigateur ne s'ouvre pas toujours depuis Claude Code :
  il faut alors ouvrir l'URL affichée. Le jeton dure 60 jours.
- **Meta** : Meta ne récupère pas toujours les images hébergées sur ImgBB. Facebook reçoit donc
  le fichier lui-même. Instagram exige une URL ; sur l'erreur 2207003 (délai dépassé), l'image
  est recopiée sur les serveurs de Meta, en photo de Page non publiée, puis Instagram réessaie.
  L'application doit être en mode **Live**. L'option de création d'app « Autre » est annoncée
  comme bientôt supprimée par Meta.
- **GitHub** : la connexion `gh` doit avoir l'autorisation `workflow` pour pousser le workflow.
  Sous Windows, `gh` n'est pas dans le PATH juste après son installation
  (`C:\Program Files\GitHub CLI`). Enfin, les journaux masquent (`***`) tout ce qui ressemble à
  la valeur d'un secret, y compris des réglages comme `claude` ou `fal`.
