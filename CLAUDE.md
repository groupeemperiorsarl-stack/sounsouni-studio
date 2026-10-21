# Sounsouni Studio — notes pour Claude (à lire en premier)

## Qui, quoi
- Propriétaire : **Issa Haidara**, fondateur de Sounsouni (Bamako). Répondre **toujours en français simple**, sans jargon.
- Projet : série animée verticale **« Les Plans de Bakary »** (1080×1920, TikTok / Facebook / YouTube, 3 à 4 min, publicité pour l'application Sounsouni).
- **Sounsouni Studio** (`studio/`) : application 100 % autonome. Un script détaillé (format `docs/GUIDE_SCENARISTE.md`) → vidéo finie (voix, poses, plans, regards, bruitages, rires, musique). Ce que l'application sait montrer : `docs/CAPACITES.md` (régénéré par `python studio/capacites.py`).
- But d'Issa : que **l'application** fasse tout elle-même. Toute correction doit être une **règle dans le code**, jamais une retouche à la main sur une vidéo ou une image.

## Façon de travailler demandée par Issa (important)
1. **Valider sur des images fixes avant toute vidéo** : c'est **l'application** qui fabrique les planches A / B / C / D (`--planches`, voir « Fabriquer »). Claude n'a pas besoin de regarder ces images lui-même : il envoie `planches/planches.html` (page à cocher) à Issa, qui répond « 1B 3C ». Ne fabriquer la vidéo qu'après son accord.
2. **Ne refaire que les secondes concernées** d'un épisode déjà fait (rendre le morceau, puis le recoller avec ffmpeg), jamais tout l'épisode.
3. **Économiser** : ses crédits Claude et les minutes GitHub (2 000 minutes gratuites par mois ; un épisode complet sur 15 machines ≈ 170 minutes). Les essais se font en local, GitHub sert aux vrais épisodes.
4. Chercher soi-même des outils libres (GitHub) plutôt que de lui demander des images ou de passer par des services payants. Il ne télécharge rien lui-même.
5. **Sécurité** : ne jamais écrire de clé ou de jeton dans le dépôt. Kaggle : jeton seulement en variable d'environnement `KAGGLE_API_TOKEN`, fourni par Issa dans la conversation. Supabase : lecture libre, aucune modification sans son accord explicite. GitHub : ne déposer que ce qu'il demande.

## Fabriquer
- **Formulaire « Nouvel épisode »** (sans Claude) : `https://github.com/groupeemperiorsarl-stack/sounsouni-studio/issues/new?template=nouvel-episode.yml`. Il donne d'abord l'aperçu ; un commentaire d'un seul mot, « vidéo » ou « aperçu », lance la suite (`.github/workflows/demande.yml` → `episode.yml`, 15 machines ; vidéo publiée en *release*).
- **Tableau de bord des minutes** : issue n° 2 (`.github/workflows/tableau.yml`).
- **En local** :
  - aperçu sans voix : `STUDIO_FAUSSES_VOIX=1 python -m studio script.txt -o sortie --plans-seulement` → `sortie/apercu_plans.png` ;
  - vidéo complète : `python -m studio script.txt -o sortie` ;
  - une seule étape : `--etape voix|plans|rendu|final --part i/n`.
  - **planches à valider** : `STUDIO_FAUSSES_VOIX=1 python -m studio script.txt -o sortie --planches` → `sortie/planches/planches.html` (page à cocher, téléphone) + `planche_N.png`. Sans précision : seulement les plans où l'application hésite entre deux poses (12 questions au plus, une même hésitation sur plusieurs plans = une question). Sur un passage : `--de 1:20 --a 1:45` ou `--plans 12,14-16` → questions de pose **et** de cadrage (épaule / gros plan seul / plan large).
  - **réponse d'Issa** : `--choix "1B 3C"` → gardée dans `script.choix.json` (à côté du script, par numéro de plan) ; la mise en scène la suit ensuite (`director.CHOIX`). Si le même choix revient d'un épisode à l'autre, en faire une règle dans `director.py`.
  - **secondes concernées** : le rendu est fait par morceaux de 12 s ; seuls les morceaux dont les plans ont changé sont refaits, puis tout est recollé (`render.seg_hash`). Rien à faire à la main.
  - **Sur GitHub** : l'aperçu arrive avec ses planches. Issa répond en commentaire « 1B 3C » (nouvel aperçu avec ses choix, choix gardés dans `demandes/episode_N.choix.json`) ou « planches 1:20-1:45 ».
- **Images manquantes (Gemini, gratuit, fait par Issa)** : `python -m studio.gemini script16.txt script17.txt -o sortie_gemini` → `fiche_gemini.html` (pour chaque image : référence à joindre + demande à coller dans Gemini). Images renvoyées : `python -m studio.gemini -o sortie_gemini --importer "1=a.png 2=b.jpg"` (détourage + catalogue). Kaggle T4 abandonné (images noires) ; Molab non retenu.
- **Rires** (`studio/rires.py`, Chatterbox Turbo MIT, vrais rires `[laugh]`/`[chuckle]` avec la voix du personnage) : type par personnage (homme, homme d'âge mûr, femme, demoiselle, enfant/ado ; clé `age` du catalogue) et 2 sortes (éclat, petit rire retenu). Page d'écoute A/B/C/D : `python -m studio.rires -o sortie_rires` ; choix : `--choix "1B 2A"` → `assets/rires/<PERSO>_<sorte>.wav`, réutilisés à chaque épisode.
- **Installer en local** (session neuve) :
  - `pip install -r studio/requirements.txt` ;
  - voix : `python -m venv ~/tts && ~/tts/bin/pip install -r studio/requirements-voix.txt`, puis `export STUDIO_TTS_PY=~/tts/bin/python` ;
  - LivePortrait (têtes tournées, bouches) : `bash studio/lp/install.sh`.
  - Machine : 2 processeurs, 8 Go → lancer la voix (Chatterbox) **seule**, sinon la mémoire sature.

## Assistant de secours (quand Claude n'est pas disponible)
- Dans la page **Studio mobile** (`outils/studio_mobile.html`), onglet **🤖 Assistant** : Issa colle le script validé → « Mettre au format » → l'IA gratuite (Groq `openai/gpt-oss-120b`, puis Cerebras, puis OpenRouter si Groq est saturé) le met au format, scène par scène.
- Ses consignes = **`docs/ASSISTANT.md`** (lu dans le dépôt à chaque fois). Toute nouvelle règle de format validée par Issa doit y être ajoutée aussi.
- La page corrige ensuite toute seule (émotions sans accent, indications inconnues retirées, réplique vide → RÉACTION, DÉCOR en double, postures), affiche les alertes, la durée estimée et les scripts de voix par personnage.
- Issa relit, coche « J'ai relu et je valide », puis lance : **Extrait de 40 s** (vidéo courte pour tester), **Aperçu des plans** ou **Épisode complet** (crée la demande GitHub comme le formulaire).
- Bouton **🖼 Fiche Gemini** de chaque épisode = commentaire « fiche » → `.github/workflows/fiche.yml` → fiche + images à joindre affichées dans la page.
- Clés Groq / Cerebras / OpenRouter : **seulement sur le téléphone d'Issa** (onglet Assistant, `localStorage`), jamais dans le dépôt ni la conversation. L'assistant ne touche jamais au code : les corrections du studio restent pour Claude.

## Fichiers clés
- `studio/script.py` lecture du script · `voices.py` voix + vérification Whisper + fins de phrase jamais coupées + rires + `lexique.txt` (prononciations « écrit = prononcé », ex. « Kôrôbalé wou = Kôrôbaléou ») et « plus » négatif sans S.
- `studio/planches.py` planches A / B / C / D (questions, images, page à cocher, lecture de la réponse).
- `studio/director.py` mise en scène : choix des poses, plans larges, champ / contre-champ, regards. `render.py` images (têtes tournées LivePortrait, détourage), `audio.py` son.
- `studio/assets/catalog.json` poses (étiquettes, objets reconnus par `autotag.py` / OWLv2, orientation `yaw`). Outils de préparation : `autotag.py`, `autoyaw.py`, `autosmile.py`, `remouth.py`, `build_assets.py`.

## Règles de mise en scène validées par Issa (ne pas casser)
- **Regard** : le sens des yeux et de la tête est réglé sur le « test B » (`director.orient`, `sd = d if flip else -d`). En plan large, on regarde l'autre, y compris en haut / en bas (assis / debout).
- **Champ / contre-champ** (« test E ») : dès que deux personnes se parlent, la caméra est derrière l'épaule de celui qui écoute ; on garde l'image d'origine, retournée seulement si besoin. Pas d'image de dos → silhouette floue aux couleurs du personnage.
- **Quelqu'un arrive et parle au groupe** : il est au premier plan, de dos, face au groupe (si une image de dos existe, sinon il reste dans la rangée). Sa place reste libre dès le premier plan de la scène ; il entre en marchant si le script met des pas ou des talons.
- **Plans d'ensemble à 4 personnes et plus : deux rangées** (scène modèle Gemini validée par Issa, `docs/scenes_modeles/`, `director.deux_rangees`) : devant, les deux qui se parlent, grands, face à face (x 0,25 / 0,73) ; derrière, les autres plus petits dans les espaces libres (assis au centre). Remplace « de dos au premier plan » pour ces groupes. « Celui qui arrive » = le dernier arrivé (`stage.seq`) ou celui qui parle. Nouvelles scènes modèles : `studio/scene_modele.py` (mesure et compare).
- **Groupes avec gens assis** (moins de 4 personnes) : les assis au milieu, à taille normale ; les debout face à face sur les côtés ; les autres debout derrière le banc, un peu plus petits. Personne ne flotte, personne n'est coupé.
- **Tant que personne ne parle** : poses calmes de trois-quarts, sans geste (« pose D »). Les gestes viennent avec la parole.
- **Objets** (brochette, téléphone, larmes…) : jamais montrés si le script ne le demande pas. Objet écrit dans le PLAN (`[Karim, téléphone]`) : toujours montré.
- **Postures** respectées (assis reste assis), décor cohérent dans une scène, décors sans figurants, bouches ouvertes sans que les yeux bougent.

## Où on en est (21/10/2026)
- Assistant de secours ajouté (Groq gratuit) et testé sur un extrait de 40 s (demande n° 5).
- Planches A / B / C automatiques ajoutées (local et GitHub) + rendu partiel automatique par morceaux.
- Épisode 15 « La rumeur » fini (v5) ; script : `exemples/episode15_la_rumeur.txt` (+ début réécrit : `exemples/episode15_debut_corrige.txt`).
- Plus tard : passer de 15 à 5 machines (quand l'application sera bien réglée) ; vues de dos des personnages qui n'en ont pas ; nettoyer le décor BUREAU (figurants) ; pose de Karim assis.
