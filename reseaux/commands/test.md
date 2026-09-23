---
name: test
description: Fait le premier cycle complet avec l'utilisateur - choisir une idée, rédaction et image par l'IA, relecture, validation, publication réelle sur les réseaux choisis.
---

# /reseaux:test : le premier post

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier`, `python` et `depot_github`.
Travaille dans `dossier`. C'est l'utilisateur qui agit dans Notion : c'est
l'apprentissage du geste quotidien.

## 1. Choisir une idée

Demande à l'utilisateur d'ouvrir son tableau Notion, de choisir l'idée qui lui plaît le
plus et de passer son statut à **✍️ À rédiger**.

## 2. Rédaction

Lance `<python> rediger` (en local, c'est plus rapide que d'attendre le prochain passage).
Compte 30 secondes à 2 minutes : l'image est la partie la plus longue.

Demande-lui ensuite d'ouvrir la ligne dans Notion : les 3 textes et l'image sont remplis,
avec le statut **👀 À valider**. Recueille son avis :
- **Texte à retoucher** : il écrit ce qu'il veut dans la colonne **Consignes** (« plus court »,
  « moins d'emojis », « parle du devis gratuit »…) et choisit **🔄 Réécrire le texte** dans la
  colonne **Action** (ou clique sur le bouton, s'il l'a créé). Relance `<python> rediger` : Claude
  repart de la version actuelle et applique les consignes. Il peut aussi corriger à la main
  directement dans les textes, ou modifier les mots-clés avant de réécrire.
- **Image décevante** : il peut modifier la description dans **Prompt image**, puis choisir
  **🎨 Nouvelle image** dans Action et relancer. Il peut aussi déposer sa propre photo.
- **Si le ton ne convient pas du tout** : ajuste `marque.md` avec lui (règle générale), puis
  **✨ Tout refaire**.

## 3. Validation

1. Corriger ce qu'il veut directement dans les textes.
2. Mettre la **Date de publication** à aujourd'hui, avec une heure déjà passée (pour un
   test immédiat).
3. Passer le statut à **✅ Validé**.

## 4. Publication par GitHub (la vraie chaîne)

```
gh workflow run agent.yml -f etape=publier
```

Suis l'exécution (`gh run list --workflow agent.yml -L 1`, puis `gh run watch <id>`), et
affiche les lignes ✅ / ❌ du journal.

- Tout est ✅ : la ligne passe en **🚀 Publié**, avec les liens dans la colonne Liens.
  Demande-lui d'aller voir ses posts. 🎉
- Un ❌ : lis le message dans la colonne Erreur ou le journal. Corrige (souvent un jeton
  ou le mode Live de Meta), puis repasse en **✅ Validé** et relance. Les réseaux déjà
  publiés ne seront **pas** republiés.

## 5. Et maintenant

Explique que tout est automatique : l'agent passe **à chaque créneau** pour publier et le **lundi matin** pour préparer la semaine. Pour les
prochains posts, il suffit de choisir des idées, relire et valider. Pour une rédaction ou une
retouche immédiate : le lien **▶️ Lancer l'agent maintenant** dans Notion, ou `/reseaux:lancer`.

Ajoute `"test"` à `etapes_faites`.
