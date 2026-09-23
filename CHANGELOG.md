# Changelog

## 1.0.1 (2026-09-23)

- Images : découpe automatique des bordures blanches ajoutées par certains générateurs.
- Calendrier : chaque post importé peut porter des `consignes` pour l'IA.
- Idées : plus de sujets qui supposent un client, un projet ou un chiffre réels.

## 1.0.0 (2026-09-23)

Première version publique, testée de bout en bout (installation complète et publication
réelle sur LinkedIn, Facebook et Instagram).

- Installation guidée en 8 étapes, reprenable (`/reseaux:start`).
- Idées, rédaction par réseau et images générées, validées dans un tableau Notion.
- Rédaction par Claude (abonnement Pro/Max) ou Gemini (gratuit).
- Images : FLUX schnell (Cloudflare, Pollinations) ou Nano Banana (fal.ai).
- Rythme de publication automatique et calendrier éditorial mensuel (`/reseaux:calendrier`).
- Thèmes de contenu gérés dans Notion (fréquence, mots-clés, pause).
- Retouches en un clic : réécriture avec consignes, nouvelle image, tout refaire.
- Agent sur GitHub Actions : passages aux créneaux, sécurité le lundi, lancement à la demande
  depuis Notion ou `/reseaux:lancer`.
- Connexion LinkedIn directe (sans le générateur de jetons de LinkedIn), jeton Meta permanent
  obtenu automatiquement, envoi direct des images à Meta avec repli pour Instagram.
