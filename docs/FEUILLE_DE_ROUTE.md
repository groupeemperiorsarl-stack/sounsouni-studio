# Feuille de route — Sounsouni Studio

## Étape 1 — Sauvegarde ✅
Scripts, réglages, images de référence, voix de référence et planches d'origine rangés dans ce dépôt.

## Étape 2 — Guide du scénariste
`docs/GUIDE_SCENARISTE.md` : format du script avec expressions, réactions et décors accrochés aux mots,
liste complète des expressions et actions reconnues.

## Étape 3 — Application `studio`
Une commande unique : `python -m studio episode.txt` →
1. **Lecture du script** : scènes, plans, répliques, balises `{expression}` et `[RÉACTION/BRUITAGE]`.
2. **Voix** : génération (Chatterbox) + vérification par transcription, nouvelle tentative si un mot est faux.
3. **Alignement mot à mot** : horodatage de chaque mot (faster-whisper) → position exacte des balises.
4. **Visages** : JoyVASA (lèvres + tête) + ajouts LivePortrait aux instants des balises
   (sourire, colère, choc, regard vers l'interlocuteur…), cadence réglable (2 / 4 / 6 images/s).
5. **Corps** : respiration, balancement suivant l'énergie de la voix, actions des balises
   (recule, avance, hoche la tête, sursaut…), réactions des personnages qui écoutent.
6. **Montage** : décors, plans larges / gros plans, sous-titres, bruitages, musique, écran de fin.
7. **Sorties** : version pleine qualité + version légère (< 30 Mo) + description.
8. **Corrections partielles** : ne recalculer que les répliques/plans modifiés.

## Étape 4 — Améliorations
- Remplacer le détecteur de visage InsightFace (non commercial) par un équivalent libre.
- Gestes simples du corps à partir d'une image (épaules, bras) si faisable sans carte graphique.
- Vitesse : cache des visages, calcul en arrière-plan, reprise après coupure.
