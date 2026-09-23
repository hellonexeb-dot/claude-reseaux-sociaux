---
name: lancer
description: Lance l'agent tout de suite (rédaction, réécritures, nouvelles images, publications en retard) sans attendre son prochain passage planifié, puis résume ce qu'il a fait.
---

# /reseaux:lancer : l'agent, maintenant

Lis `.reseaux/state.json` pour connaître `dossier`, `python` et `depot_github`.
Travaille dans `dossier`.

L'agent ne passe tout seul qu'aux **créneaux de publication** et le **lundi matin** (sécurité).
Cette commande sert quand l'utilisateur a demandé une rédaction, une réécriture ou une
nouvelle image dans Notion, ou validé un post dont l'heure est déjà passée.

## Où le lancer

- **Sur GitHub (par défaut)** si `depot_github` est rempli :
  `gh workflow run agent.yml -f etape=tout`, puis récupère l'exécution
  (`gh run list --workflow agent.yml -L 1`), suis-la avec `gh run watch <id>` et affiche
  les lignes utiles du journal (`gh run view <id> --log`, uniquement les lignes → ✅ ❌ 💡 📅).
- **En local** sinon, ou si l'utilisateur le préfère (plus rapide à démarrer) :
  `<python> tout`.

Si l'utilisateur ne veut qu'une partie, passe l'étape voulue : `rediger` (rédaction et
actions), `publier`, `idees`.

## Résumé

Termine par un résumé court : posts rédigés ou mis à jour (avec leur date prévue), posts
publiés (avec les liens), erreurs éventuelles et quoi faire. Rappelle que les posts
rédigés attendent sa relecture en **👀 À valider**.

Astuce à rappeler : sans Claude Code, il peut aussi lancer l'agent depuis Notion avec le
lien **▶️ Lancer l'agent maintenant** en haut de sa page (puis « Run workflow » sur GitHub),
y compris depuis son téléphone.
