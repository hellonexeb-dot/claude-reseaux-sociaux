---
name: start
description: Commande MASTER. Installe pas à pas un agent qui propose des idées de posts, rédige les textes, génère les images et publie sur LinkedIn, Facebook et Instagram après validation dans Notion. Sans frais en plus de l'abonnement Claude. Reprenable via .reseaux/state.json.
---

# /reseaux:start : l'agent réseaux sociaux, de A à Z

Tu accompagnes l'utilisateur dans l'installation complète de son agent réseaux sociaux.
Il n'est pas forcément développeur : explique simplement, une étape à la fois, et attends
sa confirmation avant de passer à la suivante. Il peut dire STOP à tout moment : la
progression est gardée dans `.reseaux/state.json`.

## Règles de sécurité (à respecter pendant TOUTES les étapes)

- **Ne demande jamais une clé ou un jeton dans la conversation.** L'utilisateur les colle
  lui-même dans le fichier `.env` (ouvre-le pour lui : `notepad .env` sous Windows,
  `open -e .env` sous macOS, `xdg-open .env` sous Linux).
- **Ne lis jamais le contenu de `.env`** (ni Read, ni cat). Pour savoir si une clé est
  remplie, utilise uniquement : `grep -cE '^CLE=.+' .env` (renvoie 1 si remplie, 0 sinon).
- Si l'utilisateur colle quand même une clé dans la conversation, ne la répète pas :
  écris-la dans `.env` avec l'outil Edit et rappelle-lui la règle.
- Les commandes Python passent par `python agent.py …` : c'est le script de l'agent qui lit
  les clés, jamais toi.

## Étape 0 : état

Si `.reseaux/state.json` existe dans le dossier courant, lis-le et propose :
reprendre à la prochaine étape non faite, recommencer, ou sauter à une étape précise.

Sinon, crée-le :

```json
{
  "cree_le": "<date ISO>",
  "etapes_faites": [],
  "reseaux": ["linkedin", "facebook", "instagram"],
  "dossier": null,
  "python": null,
  "depot_github": null,
  "linkedin_jeton_le": null,
  "claude_jeton_le": null,
  "rythme": {"jours": ["mardi", "jeudi"], "heure": "12:15"}
}
```

## Étape 1 : annonce du parcours

Affiche :

```
🚀 Agent réseaux sociaux : installation pas à pas

Le résultat : un tableau Notion où l'IA te propose des idées de posts, rédige les
textes (LinkedIn, Facebook, Instagram) et crée les images. L'agent place chaque post
sur ton rythme de publication, tu valides, et il publie tout seul. Sans frais en plus
de ton abonnement Claude.

 1. Préparation du projet             (5 min)
 2. Ta marque : ton, cible, sujets    (10 min)   /reseaux:marque
 3. Notion : le tableau de validation (10 min)   /reseaux:notion
 4. L'IA : textes et images           (10 min)   /reseaux:ia
 5. LinkedIn                          (15 min)   /reseaux:linkedin
 6. Facebook et Instagram             (30 min)   /reseaux:meta
 7. Mise en ligne sur GitHub          (10 min)   /reseaux:github
 8. Premier post de test              (10 min)   /reseaux:test

Durée totale : environ 1 h 30, à faire une seule fois.
```

Puis demande avec AskUserQuestion (multiSelect) **sur quels réseaux** publier :
LinkedIn (profil personnel), Facebook (Page), Instagram (compte professionnel).
Enregistre le choix dans `state.json` → `reseaux`.

Si Instagram est choisi, préviens : il faut un compte Instagram **professionnel**
(Business ou Créateur) **relié à une Page Facebook**. Sinon, explique comment le
convertir (Instagram → Paramètres → Type de compte et outils → Passer à un compte pro,
puis le relier à la Page depuis les paramètres de la Page Facebook).

Si LinkedIn est choisi, explique en 3 lignes pourquoi on publie sur le **profil perso** :
bien plus de portée qu'une page entreprise, les gens suivent des personnes, et l'API
pour les pages entreprise demande une validation de LinkedIn longue et incertaine.

Puis demande le **rythme de publication** avec AskUserQuestion. Explique d'abord que chaque
post rédigé sera placé automatiquement sur le prochain créneau libre (modifiable dans Notion) :
- **2 par semaine : mardi et jeudi à 12 h 15 (recommandé)** : la régularité compte plus que le
  volume, c'est tenable dans la durée (environ 20 min de relecture par semaine), et le midi
  fonctionne bien sur les 3 réseaux.
- **3 par semaine : lundi, mercredi et vendredi à 12 h 15** : si l'utilisateur a beaucoup de
  matière (réalisations, actualités).
- **1 par semaine : mardi à 12 h 15** : pour démarrer en douceur.
- **Je choisis chaque date moi-même** : rythme automatique coupé.
Il peut aussi donner ses propres jours et son heure. Enregistre dans `state.json` → `rythme`.

## Étape 2 : préparation du projet

1. **Dossier** : demande où installer l'agent (par défaut : un sous-dossier
   `agent-reseaux` du dossier courant). Il deviendra un dépôt GitHub.
   Enregistre son chemin absolu dans `state.json` → `dossier`. Toutes les commandes
   suivantes s'exécutent dans ce dossier.
2. **Copie des fichiers** : copie tout le contenu du dossier `${CLAUDE_PLUGIN_ROOT}/template/`
   (fichiers cachés `.github`, `.gitignore`, `.env.example` compris) dans ce dossier.
   Si `${CLAUDE_PLUGIN_ROOT}` n'est pas remplacé par un vrai chemin, retrouve le dossier
   `template` du plugin avec Glob : `~/.claude/plugins/**/reseaux/template/agent.py`.
3. Copie `.env.example` en `.env`, puis écris dans `.env` : `RESEAUX_ACTIFS=<réseaux choisis, séparés par des virgules>`,
   `RYTHME_JOURS=<jours séparés par des virgules, ou aucun>` et `RYTHME_HEURE=<HH:MM>`.
4. **Python** : l'agent tourne avec Python. Vérifie dans cet ordre :
   - `uv --version` → si présent, la commande Python sera
     `uv run -q --with-requirements requirements.txt python agent.py`. S'il n'est pas dans le
     PATH, cherche-le aussi dans `~/.local/bin`, `~/.cargo/bin` et (Windows)
     `%LOCALAPPDATA%` (Glob `**/uv.exe`) : s'il existe, utilise son chemin complet.
   - sinon `python --version` ou `python3 --version` (3.10 minimum) → crée un
     environnement : `python -m venv .venv`, puis installe `requirements.txt` ; la commande sera
     `.venv/Scripts/python agent.py` (Windows) ou `.venv/bin/python agent.py`
   - sinon, propose d'installer uv (le plus simple, il installe Python tout seul) :
     Windows `winget install astral-sh.uv`, macOS/Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`
   Enregistre la commande retenue dans `state.json` → `python`. Toutes les étapes suivantes
   l'utilisent à la place de `python agent.py`.
5. Vérifie aussi `git --version` et `gh --version` (GitHub CLI, utile à l'étape 7 :
   https://cli.github.com). S'ils manquent, note-le et propose de les installer maintenant.

Ajoute `"preparation"` à `etapes_faites`.

## Étapes 3 à 8

Enchaîne les commandes suivantes, dans l'ordre, en les lançant avec l'outil Skill
(`reseaux:marque`, `reseaux:notion`, etc.) :

| Étape | Commande | Condition |
|---|---|---|
| marque | `/reseaux:marque` | toujours |
| notion | `/reseaux:notion` | toujours |
| ia | `/reseaux:ia` | toujours |
| linkedin | `/reseaux:linkedin` | si LinkedIn est choisi |
| meta | `/reseaux:meta` | si Facebook ou Instagram est choisi |
| github | `/reseaux:github` | toujours |
| test | `/reseaux:test` | toujours |
| calendrier | `/reseaux:calendrier` | proposé à la fin : « On prépare ton premier mois ? » |

Après chaque étape : vérifie qu'elle a été ajoutée à `etapes_faites`, affiche un point
d'étape court (✅ ce qui est fait, ➡️ la suite, temps restant estimé) et demande
« On continue ? » avant de lancer la suivante.

## Fin

Quand tout est fait, affiche le mode d'emploi quotidien :

```
🎉 Ton agent est en place !

Au quotidien, dans ton tableau Notion :
 💡 Idée        → l'agent en propose dès qu'il en reste moins de 5
 ✍️ À rédiger   → TOI : choisis les idées qui te plaisent
 👀 À valider   → l'agent a écrit les textes, créé l'image et daté le post
                  sur ton prochain créneau libre
 ✅ Validé      → TOI : relis, corrige (la date aussi si besoin), valide
 🚀 Publié      → l'agent publie à l'heure prévue (il passe à chaque créneau)
 ⚠️ Erreur      → lis la colonne Erreur, corrige, repasse en Validé

Astuces :
 • Pour retoucher un post : écris tes Consignes, puis Action → 🔄 Réécrire le texte,
   🎨 Nouvelle image ou ✨ Tout refaire.
 • Pour que l'agent s'y mette tout de suite : ▶️ « Lancer l'agent maintenant » en haut
   de ta page Notion (ou /reseaux:lancer). Sinon il passe aux créneaux et le lundi matin.
 • Pour un sujet précis : une ligne avec juste le titre, statut « À rédiger ».
 • Tes thèmes (ajouter, corriger, mettre en pause, supprimer, mots-clés) :
   directement dans la base Notion « Thèmes de contenu ».
 • Pour utiliser ta propre photo : dépose-la dans la colonne Image.
 • Pour changer de ton : modifie marque.md puis /reseaux:github.
 • Chaque fin de mois : /reseaux:calendrier prépare le planning du mois suivant.
 • Pour changer de rythme : RYTHME_JOURS et RYTHME_HEURE dans .env, puis /reseaux:github
   (les passages de l'agent se recalent automatiquement).
 • /reseaux:statut pour vérifier que tout fonctionne.
```

Si LinkedIn est actif, rappelle que **le jeton LinkedIn expire tous les 60 jours** et
propose de créer un rappel dans son agenda (date = `linkedin_jeton_le` + 55 jours).
