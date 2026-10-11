# Décisions et état du projet

_Dernière mise à jour : 11 octobre 2026_

## Équipe et rôles
- **Issa Haidara** (fondateur de Sounsouni) : producteur, valide tout.
- **Claude scénariste** (autre conversation) : écrit les scripts.
- **Claude réalisateur** (ce dépôt) : images, voix, animation, montage, descriptions, miniatures.

## Série « Les Plans de Bakary »
- Format : mini-épisodes vertical 1080×1920, **3 à 4 minutes** (toujours > 3 min).
- Épisodes livrés : 1 à 11. Ép.10 : titre à remplacer (« Le pari » ne correspond pas ; proposé : « La commande secrète »).
- Ép.11 « Le haut-parleur » v2 livré (4 min 51).
- Livraison : version légère < 30 Mo (envoi), version pleine qualité gardée.
- Descriptions : titre + description YouTube/Facebook + version courte TikTok + hashtags.

## Règles de mise en scène (retours d'Issa)
- **Plans d'ensemble obligatoires** quand plusieurs personnages sont impliqués (appel, dispute…) : tout le monde doit être visible.
- Gros plans sur les objets importants (téléphone, brochettes qui brûlent…).
- Une action ne doit pas être « dite » si le personnage ne peut pas la savoir (pensées intérieures = bulle « pensée »).
- Quand on corrige : ne re-rendre que la partie modifiée (point A → point B) et recoller.

## Visages et corps (nouvelle méthode, en cours)
- **Une seule image par personnage**, de face, **regard droit devant**, bouche fermée, expression neutre.
- Quand un personnage **parle** : mouvements de lèvres/mâchoire, **pas de dents** (les dents seulement quand il rit ou sourit franchement).
- Le personnage **regarde son interlocuteur** (pas le ciel).
- **Pas de clignements artificiels** (effet « tic » rejeté).
- Le **corps doit suivre la voix et le contexte** (mots forts, mots choquants → réaction).
- Animation du visage : JoyVASA (mouvements appris sur de vraies personnes) rendue par LivePortrait.
- **Cadence du visage** : Issa veut léger ; test à **2 images/seconde** livré (le corps et la caméra restent fluides).
  À valider : 2, 4 ou 6 images/seconde.

## Voix
- Chatterbox multilingue (MIT, usage commercial OK), langue `fr`, voix copiée sur les vocaux Gemini existants
  (`assets/voix_reference/`). **Validé par Issa** (« la voix ça va »).
- Réglages : `n_cfm_timesteps=5` (≈ 1,4× plus rapide), exaggeration 0,4–0,8 selon l'émotion, cfg 0,4–0,5.
- Noms propres parfois mal prononcés → régénérer la réplique et vérifier par transcription (`tools/voices/chk.py`).

## Script : format décidé (voir `GUIDE_SCENARISTE.md`)
- Expressions et réactions **accrochées à un mot** de la réplique (`{…}` et `[…]`), décor et plan en tête de scène.

## Contraintes techniques
- Machine de calcul : 2 processeurs, 8 Go, **pas de carte graphique**.
- Voix et visages ne peuvent pas tourner **en même temps** (mémoire insuffisante).
- Visage : ~8 s par image calculée. Voix : ~30 s par réplique.
- Licence : le détecteur de visage d'InsightFace (utilisé par LivePortrait) est **non commercial** → à remplacer par un équivalent libre avant usage commercial.
- L'espace de travail peut être effacé : **tout ce qui compte doit être dans ce dépôt**.
