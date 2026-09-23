---
name: statut
description: Bilan de santé de l'agent réseaux sociaux - progression de l'installation, test de toutes les connexions, dernières exécutions GitHub, alerte d'expiration du jeton LinkedIn.
---

# /reseaux:statut : tout va bien ?

Lis `.reseaux/state.json` (si absent : propose `/reseaux:start`). Travaille dans `dossier`.
Ne lis jamais `.env`.

Fais ces vérifications et présente un bilan court :

1. **Installation** : les étapes faites et celles qui restent (ordre : preparation,
   marque, notion, ia, linkedin, meta, github, test ; ignore linkedin et meta si le réseau
   n'est pas choisi).
2. **Connexions** : lance `<python> verifier` et reprends les lignes ✅ / ❌.
3. **Jeton LinkedIn** (si LinkedIn est actif) : compare `linkedin_jeton_le` avec la date du
   jour. Au-delà de 50 jours, alerte : « ⚠️ Ton jeton LinkedIn expire dans X jours :
   lance /reseaux:linkedin ».
4. **Exécutions en ligne** (si `depot_github` est rempli) :
   `gh run list --workflow agent.yml -L 10`. Signale les échecs récents et, s'il y en a,
   affiche l'erreur du dernier (`gh run view <id> --log-failed`, résumé en une ou deux
   lignes). Rappel : GitHub désactive les tâches planifiées d'un dépôt resté 60 jours
   sans activité. Si c'est le cas, un simple `/reseaux:github` (ou un commit) les relance.

Termine par l'action recommandée, s'il y en a une.
