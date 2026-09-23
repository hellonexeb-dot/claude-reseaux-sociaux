---
name: calendrier
description: Prépare le calendrier éditorial d'un mois - un sujet par créneau du rythme de publication, temps forts vérifiés (saison, fêtes, événements locaux), thèmes équilibrés - puis crée les posts datés dans Notion après validation.
---

# /reseaux:calendrier : le planning du mois

## Contexte

Lis `.reseaux/state.json` pour connaître `dossier` et `python`. Travaille dans `dossier`.
S'il n'existe pas, propose `/reseaux:start`. C'est toi qui construis le plan, pendant la
conversation : l'agent en ligne se chargera ensuite de la rédaction.

## 1. Quel mois ?

Par défaut, le **mois suivant**. Si on est avant le 15 du mois et qu'il reste des créneaux
libres, propose aussi de compléter le mois en cours. L'utilisateur peut donner un autre mois.

## 2. Récupérer les créneaux

Lance `<python> calendrier AAAA-MM`. Le JSON renvoyé contient :
- `rythme` : les jours et l'heure de publication (`null` si le rythme est coupé) ;
- `creneaux_libres` : les dates disponibles, **un post par créneau** ;
- `deja_prevus` : les posts déjà datés ce mois-ci (à ne pas doubler) ;
- `titres_recents` : les 40 derniers sujets (à ne pas répéter ni paraphraser) ;
- `themes` : les **thèmes actifs** de la base Notion « Thèmes de contenu » (nom, description,
  fréquence, mots-clés). C'est la référence : l'utilisateur les gère dans Notion.

Si `rythme` est `null` ou qu'il n'y a aucun créneau libre, demande combien de posts et à
quelles dates (propose mardi et jeudi, 12 h 15).

## 3. Comprendre la marque et le moment

1. Lis `marque.md` : cible, ton, zone géographique, règles strictes. Pour les thèmes, utilise
   `themes` du JSON (et non la section piliers de `marque.md`, qui n'est plus à jour une fois
   la base Notion créée).
2. Cherche les **temps forts du mois** avec WebSearch, en priorisant ce qui parle à la cible :
   - saison, météo, rythme d'activité de la cible (rentrée, haute saison, période creuse) ;
   - fêtes et dates commerciales (Noël, fête des mères, soldes, Black Friday, Saint-Valentin…) ;
   - vacances scolaires de la zone ;
   - **événements locaux** de la zone de la marque (salons, festivals, courses, marchés) ;
   - journées thématiques **seulement si elles concernent vraiment l'activité**.
   Vérifie chaque date sur une source fiable. Si tu n'es pas sûr, marque le temps fort
   « à confirmer » plutôt que de l'affirmer.

## 4. Construire le plan

Un sujet par créneau libre, en respectant ces règles :
- **Alterner les thèmes** : jamais deux fois le même d'affilée, et tous représentés sur le mois
  s'il y a assez de créneaux.
- **Respecter les fréquences** : un thème « Souvent » revient environ deux fois plus qu'un
  « Normal », un thème « Rarement » au plus une fois par mois.
- **Utiliser les mots-clés** de chaque thème dans les `mots_cles` des posts correspondants.
- **Anticiper** : un post lié à un temps fort sort 1 à 2 semaines **avant** l'événement,
  pas le jour même.
- **Raconter une progression** sur le mois quand c'est possible (ex. préparer les fêtes :
  prise de conscience → conseils → passage à l'action).
- **Ne pas répéter** les `titres_recents` ni les `deja_prevus`.
- Respecter les **règles strictes** de `marque.md` : aucun chiffre, client ou témoignage inventé.
- Titres concrets et accrocheurs, dans le vocabulaire de la cible.

## 5. Présenter et ajuster

Affiche le plan sous forme de tableau : **Date | Pilier | Titre | Angle (une phrase)**.
Puis la liste des temps forts utilisés, avec leur date et leur source (et les « à confirmer »).
Termine par un bilan de l'équilibre (nombre de posts par pilier).

Demande s'il veut ajuster : remplacer un sujet, déplacer une date, changer l'équilibre.
Itère jusqu'à ce qu'il valide.

## 6. Créer les posts dans Notion

Demande avec AskUserQuestion comment les créer :
- **✍️ À rédiger (recommandé)** : puisque le plan est validé, l'agent rédige tout (textes et
  images) au prochain passage. Il ne reste plus qu'à relire et valider chaque post.
- **💡 Idée** : les posts restent en idées datées. L'utilisateur choisira au fil de l'eau
  lesquels passer en « À rédiger ».

Écris le plan dans `calendriers/AAAA-MM.json` :

```json
{
  "statut": "a_rediger",
  "posts": [
    {
      "date": "2026-10-06T12:15:00+02:00",
      "titre": "…",
      "mots_cles": ["…", "…", "…"],
      "pilier": "nom exact d'un thème actif",
      "angle": "1 à 2 phrases : le message clé et ce que le lecteur retient"
    }
  ]
}
```

Les dates reprennent **exactement** les valeurs de `creneaux_libres`. Pour une date choisie
à la main, utilise le format ISO avec le fuseau de Paris.

Lance ensuite `<python> importer calendriers/AAAA-MM.json`.

## 7. Et ensuite

- En « À rédiger » : propose de lancer la rédaction tout de suite en local
  (`<python> rediger`, environ 1 minute par post) ou via `/reseaux:lancer`. Sinon, l'agent s'en
  chargera à son prochain passage (au plus tard lundi matin). Rappelle que **chaque post doit ensuite être relu et passé en ✅ Validé**.
  Un post validé après l'heure de son créneau part au passage suivant : pour ne pas attendre,
  lien **▶️ Lancer l'agent maintenant** dans Notion.
- Suggère d'ouvrir la **vue Calendrier** de Notion pour voir le mois d'un coup d'œil.
- Propose un rappel vers le 25 de chaque mois pour relancer `/reseaux:calendrier`.
