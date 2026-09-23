---
name: meta
description: Connecte la Page Facebook et le compte Instagram professionnel via une application Meta - jeton de Page permanent obtenu automatiquement, passage de l'application en mode Live.
---

# /reseaux:meta : Facebook et Instagram

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier`, `python` et `reseaux`. Travaille dans `dossier`.
Règles : ne demande jamais de clé dans la conversation, ne lis jamais `.env`, vérifie
une clé avec `grep -cE '^CLE=.+' .env`.

C'est l'étape la plus longue (environ 30 min) : annonce-le et avance point par point, en
attendant un « c'est fait » à chaque fois. Les menus de Meta changent souvent : si
l'utilisateur ne trouve pas un bouton, demande-lui ce qu'il voit et adapte-toi.

## 0. Prérequis

- Être **administrateur** de la Page Facebook.
- Pour Instagram : un compte **professionnel** (Business ou Créateur) **relié à la Page**.
  Vérification : Page Facebook → Paramètres → Comptes liés → Instagram.

## 1. Créer l'application Meta

1. Ouvrir https://developers.facebook.com, se connecter et accepter de devenir développeur si c'est demandé.
2. **Mes apps** → **Créer une app**.
3. Cas d'usage : dans le filtre de gauche, choisir **Autres**, puis tout en bas l'option
   **Autre** (« Votre application sera créée dans l'ancienne expérience »). Type d'app :
   **Entreprise** (Business). Si Meta demande un portefeuille business, le choisir s'il existe,
   sinon passer. Meta annonce que l'option « Autre » va disparaître : si elle n'existe plus,
   demande à l'utilisateur ce qu'il voit et cherche un cas d'usage de gestion de Page qui
   donne accès à `pages_manage_posts` et `instagram_content_publish`.
4. Nom : « Agent réseaux sociaux », puis créer.
5. Dans l'app : **Paramètres de l'app** → **Général**. Copier dans `.env` :
   - l'**ID de l'app** → `META_APP_ID=`
   - la **Clé secrète** (bouton Afficher) → `META_APP_SECRET=`

## 2. Générer un jeton dans l'Explorateur

1. Ouvrir https://developers.facebook.com/tools/explorer
2. À droite, **Application Meta** : choisir « Agent réseaux sociaux ».
   **Utilisateur ou Page** : « Obtenir un token utilisateur ».
3. **Autorisations** : ajouter
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `business_management`,
   plus `instagram_basic` et `instagram_content_publish` si Instagram est utilisé.
4. Cliquer sur **Generate Access Token**. Dans la fenêtre Facebook :
   - si elle propose « Continuer en tant que… », cliquer sur **Modifier les paramètres** (sinon
     les anciens choix sont repris, parfois sans la Page) ;
   - choisir **« Activer pour ces éléments actuels uniquement »** et cocher **seulement sa
     Page** (puis, sur l'écran suivant, son compte Instagram) ;
   - accepter toutes les autorisations.
5. Copier le jeton affiché dans `.env` → `META_USER_TOKEN=`.
   ⏱️ Ce jeton ne vit qu'une heure : passer tout de suite au point 3.

## 3. Obtenir le jeton permanent automatiquement

Vérifie les 3 clés avec grep, puis lance : `<python> meta`

Le script échange le jeton contre un **jeton de Page qui n'expire jamais**, retrouve la
Page et le compte Instagram, écrit `META_PAGE_ID`, `META_PAGE_TOKEN` et
`INSTAGRAM_ACCOUNT_ID` dans `.env`, puis efface le jeton temporaire.

- Plusieurs Pages : le script les liste. Demande laquelle utiliser, puis relance
  `<python> meta <id>`.
- « Aucun compte Instagram » : le compte n'est pas professionnel ou pas relié à la Page
  (voir le point 0), ou `instagram_basic` n'a pas été coché au point 2.
- Jeton expiré : refaire le point 2.

## 4. Passer l'application en mode Live

Sans ça, les publications risquent de n'être visibles que par l'utilisateur lui-même.

1. En haut de l'écran de l'app, basculer l'interrupteur **Mode de l'application :
   Développement** → **Live**. C'est souvent tout.
2. Si Meta refuse en signalant des informations manquantes : **Paramètres de l'app** →
   **Général**, renseigner l'**URL de la politique de confidentialité** (sa page mentions
   légales / confidentialité), une **catégorie** et une **icône**, enregistrer, puis rebasculer.

Aucune validation par Meta (App Review) n'est nécessaire : l'application ne publie que
sur les comptes de son propre administrateur.

## 5. Tester

Lance `<python> verifier`. Les lignes Facebook et Instagram doivent afficher le nom de la
Page et le @ du compte.

Ajoute `"meta"` à `etapes_faites`.
