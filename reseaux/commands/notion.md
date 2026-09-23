---
name: notion
description: Connecte Notion à l'agent - création de l'intégration, de la page, puis création automatique de la base éditoriale (statuts, textes par réseau, image, date de publication) et des vues conseillées.
---

# /reseaux:notion : le tableau de validation

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier` et `python` (la commande qui lance
l'agent). Travaille dans `dossier`.
Règles : ne demande jamais de clé dans la conversation, ne lis jamais `.env`, vérifie
une clé avec `grep -cE '^CLE=.+' .env`.

## 1. Créer l'intégration Notion

Guide l'utilisateur :

1. Ouvrir https://www.notion.so/profile/integrations et cliquer sur **Nouvelle intégration**.
2. La nommer « Agent réseaux sociaux », choisir son espace de travail, type **Interne**, puis valider.
3. Copier le **secret d'intégration** (`ntn_…`).

Ouvre `.env` pour lui et demande-lui de coller le secret après `NOTION_TOKEN=`, puis
d'enregistrer. Vérifie avec `grep -cE '^NOTION_TOKEN=.+' .env`.

## 2. Créer la page et la relier

1. Dans Notion, créer une page vide, par exemple « Réseaux sociaux ».
2. En haut à droite, **•••** → **Connexions** → ajouter « Agent réseaux sociaux ».
   (Sans ça, l'agent ne voit pas la page : c'est l'oubli le plus fréquent.)
3. **•••** → **Copier le lien**, puis coller le lien ici, dans la conversation (ce
   n'est pas une clé).

## 3. Créer les bases automatiquement

Lance : `<python> installer "<lien de la page>"`

Deux bases sont créées dans la page, et leurs identifiants sont écrits tout seuls dans `.env`
(`NOTION_DATABASE_ID`, `NOTION_THEMES_ID`) :
- **Publications réseaux sociaux** : une ligne par post.
- **Thèmes de contenu** : pré-remplie avec les thèmes de `marque.md`. **À partir de
  maintenant, c'est ici que l'utilisateur gère ses thèmes** : ajouter une ligne, corriger un
  nom, une description ou des mots-clés, décocher « Actif » pour mettre un thème en pause,
  supprimer une ligne, régler la fréquence (Souvent / Normal / Rarement). L'agent relit les
  thèmes à chaque passage : aucune autre manipulation n'est nécessaire.

La commande peut être relancée sans risque : elle ne crée que ce qui manque (par exemple les
colonnes ajoutées par une nouvelle version du plugin).

En cas d'erreur :
- `401` : le secret est incorrect ou mal collé.
- `404` : l'intégration n'est pas connectée à la page (étape 2.2).

## 4. Les vues conseillées

La base est créée avec une vue tableau. Guide l'utilisateur pour ajouter 3 vues
(bouton **+** à côté du nom de la vue) :

- **Tableau (Board)** groupé par « Statut » : son espace de validation, en glisser-déposer.
- **Calendrier** sur « Date de publication » : son planning éditorial.
- **Galerie** avec « Aperçu de la carte » réglé sur « Image » : pour voir les visuels.

Conseil : dans la vue Board, masquer les colonnes techniques (Prompt image, Publié sur,
Liens, Erreur) pour garder des cartes lisibles.

## 5. Mettre un post à jour d'un clic

Explique les deux colonnes prévues pour ça, sur chaque ligne :
- **Action** : 🔄 Réécrire le texte, 🎨 Nouvelle image ou ✨ Tout refaire. L'agent traite la
  demande à son prochain passage (ou tout de suite avec le lien **▶️ Lancer l'agent
  maintenant** ajouté plus tard dans la page, ou `/reseaux:lancer`), vide la colonne et repasse le post en
  **👀 À valider**, même s'il était validé : rien ne part sans relecture.
- **Consignes** : ce que l'IA doit changer (« plus court », « parle de l'offre de rentrée »,
  « moins d'emojis »). La réécriture part de la version actuelle. Les mots-clés de la ligne
  sont aussi modifiables avant de réécrire.

**Le vrai bouton, en option (1 min).** L'API Notion ne sait pas créer de bouton, mais
l'utilisateur peut en ajouter un qui remplit la colonne Action à sa place :
1. Dans la base Publications : **+** (nouvelle propriété) → **Bouton**, nommé « 🔄 Réécrire ».
2. Action du bouton : **Modifier la propriété** → Action → « 🔄 Réécrire le texte ».
3. Recommencer pour « 🎨 Nouvelle image » si souhaité.

Pour un **sujet précis** à traiter tout de suite : créer une ligne avec seulement le titre (et
éventuellement des consignes), statut **✍️ À rédiger**. L'agent fait tout le reste.

Ajoute `"notion"` à `etapes_faites`.
