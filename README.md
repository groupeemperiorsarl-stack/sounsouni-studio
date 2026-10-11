# Sounsouni Studio

Atelier de fabrication de la série animée **« Les Plans de Bakary »** (Sounsouni, Bamako) :
TikTok, Facebook Reels, YouTube.

Objectif : à partir **d'un script** (écrit par le scénariste, avec expressions et réactions au mot près)
et **d'une image par personnage**, fabriquer automatiquement l'épisode :

1. **Voix** de chaque personnage (voix copiée sur ses anciens vocaux, émotion par réplique) — Chatterbox (open source, MIT).
2. **Visages animés** : synchronisation des lèvres, regard, sourcils, mouvements de tête — JoyVASA + LivePortrait (open source).
3. **Corps** : respiration, balancement qui suit la voix, réactions écrites dans le script.
4. **Montage** : décors, plans, sous-titres, bruitages, musique, écran de fin, version légère (< 30 Mo).

> État actuel : **prototype**. Les outils fonctionnent séparément (voir `tools/`), l'application qui
> lit le script et enchaîne tout est en cours de construction (voir `docs/FEUILLE_DE_ROUTE.md`).

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `docs/` | Décisions, guide du scénariste, installation, feuille de route |
| `tools/voices/` | Génération des voix (Chatterbox), découpage, vérification par transcription |
| `tools/faces/` | Expressions et animation des visages (LivePortrait, JoyVASA) |
| `tools/render/` | Montage des plans, mixage audio |
| `tools/prep/` | Agrandissement + détourage des images, paires de bouches (ancienne méthode) |
| `patches/` | Modifications apportées au code open source (JoyVASA, LivePortrait) |
| `assets/personnages/` | Une image de référence par personnage et par posture |
| `assets/decors/` | Décors (kiosque, marché, atelier, cabine de Fatim) |
| `assets/voix_reference/` | Extraits de voix servant à copier la voix des personnages |
| `assets/planches_originales/` | Planches d'images d'origine (ChatGPT / Gemini) — sources de tout |

Les gros fichiers de modèles d'IA ne sont **pas** dans le dépôt : ils se téléchargent automatiquement
(voir `docs/INSTALLATION.md`).
