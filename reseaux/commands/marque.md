---
name: marque
description: Crée ou met à jour marque.md, le contexte que l'IA lit avant chaque idée et chaque texte (activité, cible, ton, piliers de contenu, style des images), à partir du site web de l'utilisateur et de quelques questions.
---

# /reseaux:marque : le contexte de marque

## Contexte

Lis `.reseaux/state.json` dans le dossier courant pour connaître `dossier` (où se trouve
l'agent). S'il n'existe pas, propose de lancer `/reseaux:start` d'abord.

`marque.md` est **le fichier le plus important pour la qualité des posts** : l'IA le lit
avant chaque idée et chaque rédaction. Explique-le en une phrase à l'utilisateur.

## 1. Comprendre l'activité

Demande l'adresse du site web (ou, s'il n'en a pas, une description libre de l'activité).

Si un site est fourni, lis la page d'accueil et les 3 à 5 pages principales (services,
à propos, réalisations, contact) avec WebFetch. Relève : l'activité, les services ou
produits, la cible, la zone géographique, les arguments différenciants, le vocabulaire
utilisé et les URL utiles.

## 2. Poser les questions qui manquent

Pose au maximum 4 questions avec AskUserQuestion, en proposant des options déduites du site :

- **Ton** : simple et chaleureux / expert et pédagogue / dynamique et décalé / premium et sobre
- **Tu ou vous** ?
- **Emojis** : jamais / avec modération / volontiers
- **Sujets à éviter** ou message à pousser en ce moment (offre, saison, événement)

Ne redemande pas ce que le site dit déjà clairement.

## 3. Rédiger marque.md

Pars de la structure de `marque.exemple.md` (dans `dossier`) et écris `marque.md` :

- **Qui est [nom]** : 2 à 4 phrases, services, arguments, pages utiles avec leurs URL.
- **À qui on parle** : la cible, son quotidien, ses freins, ce qu'elle veut vraiment.
- **Ton** : 5 à 7 règles concrètes et applicables (pas « être engageant » mais « phrases
  courtes, zéro jargon, un exemple du quotidien par post »).
- **Piliers de contenu** : 5 ou 6 thèmes récurrents propres à cette activité, chacun avec
  une ligne d'explication. Varie les types : conseil pratique, coulisses, question fréquente,
  avant/après ou résultat, local ou saisonnier, présentation d'un service.
- **Règles strictes** : garde toujours les deux premières (ne rien inventer, ne rien
  promettre) et ajoute celles de l'utilisateur.
- **Style des images** : un paragraphe visuel précis (type d'image, ambiance, lumière,
  lieux, personnes), cohérent avec l'activité. Termine par « Aucun texte, aucun logo,
  aucune interface lisible à l'écran. » : les générateurs d'images écrivent mal le texte.

## 4. Valider

Montre à l'utilisateur un résumé (ton, cible, piliers, style d'image) et demande s'il
veut ajuster quelque chose. Précise qu'il pourra modifier `marque.md` à tout moment
(puis lancer `/reseaux:github` pour mettre l'agent en ligne à jour).

**Thèmes** : à l'étape Notion, les piliers de `marque.md` sont recopiés dans la base Notion
« Thèmes de contenu ». Ensuite, c'est **dans Notion** qu'on ajoute, corrige, met en pause ou
supprime un thème et ses mots-clés : la section piliers de `marque.md` n'est plus lue. Si
cette commande est relancée après l'installation, ne modifie pas les piliers dans
`marque.md` : renvoie l'utilisateur vers la base Notion.

Ajoute `"marque"` à `etapes_faites` dans `.reseaux/state.json`.
