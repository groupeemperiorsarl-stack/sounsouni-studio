# Sounsouni Studio — notes pour Claude (à lire en premier)

## Qui, quoi
- Propriétaire : **Issa Haidara**, fondateur de Sounsouni (Bamako). Répondre **toujours en français simple**, sans jargon.
- Projet : série animée verticale **« Les Plans de Bakary »** (1080×1920, TikTok / Facebook / YouTube, 3 à 4 min, publicité pour l'application Sounsouni).
- **Sounsouni Studio** (`studio/`) : application 100 % autonome. Un script détaillé (format `docs/GUIDE_SCENARISTE.md`) → vidéo finie (voix, poses, plans, regards, bruitages, rires, musique). Ce que l'application sait montrer : `docs/CAPACITES.md` (régénéré par `python studio/capacites.py`).
- But d'Issa : que **l'application** fasse tout elle-même. Toute correction doit être une **règle dans le code**, jamais une retouche à la main sur une vidéo ou une image.

## Façon de travailler demandée par Issa (important)
1. **Valider sur des images fixes avant toute vidéo** : c'est **l'application** qui fabrique les planches A / B / C / D (`--planches`, voir « Fabriquer »). Claude n'a pas besoin de regarder ces images lui-même : il envoie `planches/planches.html` (page à cocher) à Issa, qui répond « 1B 3C ». Ne fabriquer la vidéo qu'après son accord.
2. **Ne refaire que les secondes concernées** d'un épisode déjà fait (rendre le morceau, puis le recoller avec ffmpeg), jamais tout l'épisode.
3. **Économiser** ses crédits Claude. Le dépôt est **public depuis le 21/10/2026** : les minutes GitHub sont gratuites et sans limite (au plus 20 machines en même temps sur le compte gratuit). Les essais rapides restent en local.
4. Chercher soi-même des outils libres (GitHub) plutôt que de lui demander des images ou de passer par des services payants. Il ne télécharge rien lui-même.
5. **Sécurité** : ne jamais écrire de clé ou de jeton dans le dépôt. Kaggle : jeton seulement en variable d'environnement `KAGGLE_API_TOKEN`, fourni par Issa dans la conversation. Supabase : lecture libre, aucune modification sans son accord explicite. GitHub : ne déposer que ce qu'il demande.

## Fabriquer
- **Formulaire « Nouvel épisode »** (sans Claude) : `https://github.com/groupeemperiorsarl-stack/sounsouni-studio/issues/new?template=nouvel-episode.yml`. Il donne d'abord l'aperçu ; un commentaire d'un seul mot, « vidéo » ou « aperçu », lance la suite (`.github/workflows/demande.yml` → `episode.yml`, 20 machines ; vidéo publiée en *release*).
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

## Assistant (travaille sans Claude, depuis le téléphone d'Issa)
- Page **Studio mobile** (`outils/studio_mobile.html`). Clés (Groq, Cerebras, OpenRouter, **Gemini**) et jeton GitHub **seulement sur le téléphone d'Issa** (`localStorage`), jamais dans le dépôt ni la conversation. Jeton GitHub : Issues RW, **Contents RW**, Actions R.
- **Mettre au format** (onglet 🤖 Assistant) : Groq `openai/gpt-oss-120b` (puis Cerebras / OpenRouter), consignes `docs/ASSISTANT.md`, corrections automatiques dans la page (chiffres en lettres, émotions, absent du décor = au téléphone, objets inconnus retirés…). Puis extrait 40 s / aperçu / épisode complet.
- **💬 Discuter** (chaque épisode) : Gemini Flash (clé gratuite AI Studio, modèle choisi tout seul) voit l'aperçu, regarde la vidéo, écoute ; consignes `docs/ASSISTANT_ACTIONS.md` (+ ASSISTANT.md) ; reçoit le script, `plans_resume.json` (liste minutée des plans, branche `fichiers`), les choix, `studio/reglages.json`, la liste des poses. Répond en JSON avec des **actions** qu'Issa coche puis applique :
  script (remplacement exact) · cadrage d'un plan (seul / epaule / large) · pose · place et taille d'un acteur (`acteurs`: dx, dy, taille, retourner, cacher → `demandes/episode_N.choix.json`, `director.apply_corrections`) · durée d'un plan muet · prononciation (`studio/lexique.txt`) · réglage général (`studio/reglages.json` : bouche, rangs, decor_large) · relancer aperçu / vidéo / planches · fiche Gemini · **code** (studio/*.py seulement : mis sur une branche `assistant-N-…`, commentaire « essai code … » → `.github/workflows/essai-code.yml` fabrique l'aperçu de l'épisode + ép. 17 + ép. 15 ; Issa **Accepter** (fusion dans main) ou **Refuser**).
- **🧩 Renvoyer les images Gemini** : Issa choisit les images, met le numéro de demande, « Vérifier avec l'IA » (Gemini les regarde), puis envoi → `demandes/gemini/N/` + commentaire « importer 1=… » → `.github/workflows/import.yml` (découpe, détourage, bouches, catalogue, planche `import.png`) ; « annuler import <code> » le retire.
- Quand Claude revient : relire les commits « (assistant de la page Studio mobile) » et les branches `assistant-*`, transformer en règles propres ce qui revient souvent.

## Scénariste (onglet ✍️ de la page, 28/10/2026)
- Idée (liste `docs/SAISON.md` : histoire jusqu'ici + idées 23 à 67, ou idée libre) → Gemini écrit l'épisode complet → corrections → « Envoyer » = mise au format (onglet 🤖) puis aperçu.
- Consignes `docs/SCENARISTE.md` (l'animation d'abord, la pub Sounsouni glissée dedans ; suivre l'idée d'Issa). Mémoire : `docs/EPISODES.md` (scripts complets de tous les épisodes faits, refait par `.github/scripts/archive.py` à chaque script enregistré) + GUIDE, ASSISTANT, RELECTEUR, CAPACITES, carnet. Essai sur GitHub : workflow « Essai du scénariste ».
- Si Gemini (clé de la page) est occupé : la page écrit « scénario … » sur la demande « ✍️ Scénariste » (n° 19) → `scenariste.yml` → `.github/scripts/scenariste.py` essaie Gemini, Mistral, NVIDIA, Zhipu, Cerebras, OpenRouter (mémoire complète), puis GitHub Models et Groq (résumé) → réponse en commentaire, lue par la page. Le 28/10 : NVIDIA et Zhipu sans secret GitHub.
- Longueur (28/10) : au moins 600 mots de dialogue (3 min 10 pour YouTube, ≈ 145 mots/min mesuré) ; trop court → l'IA rallonge toute seule (page `scAllonger`, GitHub `MINI`). Correction qui ne change presque rien → refaite sur GitHub par une autre IA, nombre de lignes changées affiché.
- Épisodes 1 à 13 : pas dans le dépôt.

## Oreille du studio (son) — 22/10/2026
- **earshot** (libre, MIT, github.com/Leonxlnx/earshot, figé au commit 925ebe5, processeur, sans clé) : `studio/oreille.py vidéo plans.json -o ecoute.txt` ; job `ecoute` d'episode.yml après chaque vidéo (ne retarde pas la vidéo) → `ecoute.txt` dans la branche fichiers + commentaire « 👂 » s'il y a une alerte (aigus perçants d'une scène, saturation, scène trop forte). Lu par l'assistant (💬 Discuter) et le technicien (outil `ecouter`). Local : `python -m venv ~/ear && ~/ear/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu && ~/ear/bin/pip install "earshot @ git+https://github.com/Leonxlnx/earshot@925ebe5"` puis `EARSHOT=~/ear/bin/earshot`.
- **Ambiances** (règle d'Issa : jamais stressantes) : grillons / cigales fabriqués en code (`studio/ambiances.py`, earshot les entend « crickets at night » ; l'ancien cricket.wav = « alarme / erreur », gardé seulement pour ne pas changer les poses) ; `audio.build` les tient `ambiance_sous_voix` dB sous les voix (24) et `ambiance_baisse_parole` dB de plus pendant les répliques (8), réglables dans `studio/reglages.json`.
- `poses.stamp` ne compte plus `poses/tourne/` (têtes tournées refaites à chaque vidéo : sinon aucun morceau de 12 s n'était jamais repris).

## Personnages : autres noms
- « Van » = Modibo (Bakary l'appelle ainsi) ; « Bakarin » = Bakary. Alias dans `script.CHAR_ALIASES`.

## Fichiers clés
- **Attention** : les machines « voix » n'installent que numpy, pillow, soundfile, librosa. Tout autre outil (cv2, torch…) s'importe **dans la fonction** qui s'en sert, jamais en haut de `render.py` / `director.py` / `audio.py` (sinon toutes les vidéos s'arrêtent à l'étape des voix — arrivé le 23/10/2026).
- `studio/script.py` lecture du script · `voices.py` voix + vérification Whisper + fins de phrase jamais coupées + rires + `lexique.txt` (prononciations « écrit = prononcé », ex. « Kôrôbalé wou = Kôrôbaléou ») et « plus » négatif sans S.
- `studio/planches.py` planches A / B / C / D (questions, images, page à cocher, lecture de la réponse).
- `studio/director.py` mise en scène : choix des poses, plans larges, champ / contre-champ, regards. `render.py` images (têtes tournées LivePortrait, détourage), `audio.py` son.
- `studio/assets/catalog.json` poses (étiquettes, objets reconnus par `autotag.py` / OWLv2, orientation `yaw`). Outils de préparation : `autotag.py`, `autoyaw.py`, `autosmile.py`, `remouth.py`, `build_assets.py`.

## Publication automatique (règle validée, paquet « scénariste » du 21/10/2026)
- À la fin de chaque vidéo (`__main__.versions` → `studio/publication.py`) : `_youtube` (complet), `_tiktok` (3:00, bandeau 2:50), `_shorts` (2:58, bandeau 2:50), `_facebook` (1:00, bandeau 0:50). Bandeau YouTube + voix off `studio/assets/publication/voix_youtube.wav` (voix VOIX_OFF de la série, 4,2 s). Publiées dans la *release* ; boutons de téléchargement dans la page. `STUDIO_SANS_VERSIONS=1` pour s'en passer. Guide §11.
- Scripts du paquet : ép. 15–17 déjà plus à jour dans `exemples/` (gardés) ; ép. 18 « L'avis » ajouté (`exemples/episode18_l_avis.txt`, à passer par l'assistant avant fabrication).

## Place sur GitHub (ménage automatique, demandé par Issa)
- `.github/workflows/menage.yml` (chaque nuit + après chaque épisode) → `.github/scripts/menage.py` : si les releases dépassent **60 % de 5 Go**, les plus anciennes sont supprimées ; jamais la dernière vidéo d'un épisode modifié depuis moins de 30 jours ni la toute dernière fabrication ; aperçus de plus de 14 jours supprimés. Essai sans rien supprimer : lancer avec `essai=1`.
- Mini-vidéos : retirées du dépôt dès que la planche est faite (`video.yml`). Dépôt (poses + historique) : 0,38 Go le 22/10/2026 ; au-delà de 3 Go, le script prévient.

## Règles de mise en scène validées par Issa (ne pas casser)
- **Regard** : le sens des yeux et de la tête est réglé sur le « test B » (`director.orient`, `sd = d if flip else -d`). En plan large, on regarde l'autre, y compris en haut / en bas (assis / debout).
- **Champ / contre-champ** (« test E ») : dès que deux personnes se parlent, la caméra est derrière l'épaule de celui qui écoute ; on garde l'image d'origine, retournée seulement si besoin. Pas d'image de dos → silhouette floue aux couleurs du personnage.
- **Quelqu'un arrive et parle au groupe** : il est au premier plan, de dos, face au groupe (si une image de dos existe, sinon il reste dans la rangée). Sa place reste libre dès le premier plan de la scène ; il entre en marchant si le script met des pas ou des talons.
- **Plans d'ensemble à 4 personnes et plus : deux rangées** (scène modèle Gemini validée par Issa, `docs/scenes_modeles/`, `director.deux_rangees`) : devant, les deux qui se parlent, grands, face à face (x 0,25 / 0,73) ; derrière, les autres plus petits dans les espaces libres (assis au centre). Remplace « de dos au premier plan » pour ces groupes. « Celui qui arrive » = le dernier arrivé (`stage.seq`) ou celui qui parle. Nouvelles scènes modèles : `studio/scene_modele.py` (mesure et compare).
- **Groupes avec gens assis** (moins de 4 personnes) : les assis au milieu, à taille normale ; les debout face à face sur les côtés ; les autres debout derrière le banc, un peu plus petits. Personne ne flotte, personne n'est coupé.
- **Tant que personne ne parle** : poses calmes de trois-quarts, sans geste (« pose D »). Les gestes viennent avec la parole.
- **Objets** (brochette, téléphone, larmes…) : jamais montrés si le script ne le demande pas. Objet écrit dans le PLAN (`[Karim, téléphone]`) : toujours montré.
- **Postures** respectées (assis reste assis), décor cohérent dans une scène, décors sans figurants, bouches ouvertes sans que les yeux bougent.

## Bulles et gifle (28/10/2026, règles d'Issa)
- **Une bulle ne cache jamais une tête** : `gfx.place_bulle` (en haut si possible, sinon au-dessus / sous les visages, sinon en bas) avec les visages de `render.zone_tete` (l'épaule de celui qui écoute ne compte pas) ; plus de 3 lignes → réplique montrée en morceaux (`gfx.morceaux`, temps au prorata). `render.RENDU_VERSION` : à changer quand le dessin change (sinon les anciens morceaux de 12 s sont repris).
- **`{gifle}`** dans la réplique de celui qui frappe (+ `regarde:` celui qui la reçoit) : pose main levée, bruit `clac`, éclair, « PAF ! », image qui tremble, puis plan de celui qui la reçoit (choc, joue rouge) 0,55 s après. Documenté dans le guide et ASSISTANT.md.
- Message d'aperçu : « Planches à valider » seulement s'il y a vraiment des planches (avant : `ls` vide sous nullglob = toujours vrai) ; sinon « vos choix sont appliqués ».
- Relecteur : si Groq et Gemini sont saturés, les autres IA gratuites (mêmes que le scénariste) relisent l'histoire.

## Cycle « Appliquer » (24/10/2026, règle d'Issa)
- Page : après « Appliquer » (relecture ou 💬 Discuter), l'aperçu se relance **tout seul** ; il refait la relecture et, s'il manque des images (`manques.json`), la fiche Gemini. Une note seule ne relance rien.
- Chaque correction de plan est gardée avec sa **signature** (`sig` = dernière réplique + écart) ; `__main__.recaler` la remet sur le bon plan si le script a bougé.
- Choix des planches (28/10) : gardés **par personnage** (`"poses": {"SALI": "sal_beignet"}`, lu par `director.poses_choisies`) avec la signature du plan (`planches.json` → `sigs`) ; le relecteur met aussi la signature dans ses actions. Avant, un choix sur Sali effaçait celui sur Fatim du même plan, et des signatures prises sur un aperçu plus récent envoyaient les choix sur le mauvais plan.
- Nouvel aperçu : `fichiers.sh` efface l'ancien `manques.json` et l'ancienne `relecture.json` (sinon fiches et relectures périmées).

## Où on en est (22/10/2026)
- Ép. 18 « L'avis » corrigé et monté à la main par Claude (exception demandée par Issa) ; corrections transformées en règles : contours blancs (`render.sans_frange`), objet non demandé −16, pas de geste « gifle » sans demande (étiquette `gifle`), arrivées jamais montrées avant (`Stage.ici`), gros plan muet = émotion de la réplique suivante, émotion sans image → visage calme + `manques.json` (+ fiche Gemini), `bouche_fixe`, `bouche_perso`, RUE : `rangs_decor`, debout ≠ banc / course.
- Relecteur automatique après chaque aperçu (`relecture.yml`, `.github/scripts/relecture.py`, `docs/RELECTEUR.md`) : histoire (Groq puis Gemini) + images (Gemini) → `relecture.json` + panneau « 🔎 Relecture » de la page (v22).
- Technicien (`technicien.yml`, onglet 🛠) + carnet partagé `technicien/carnet.md` ; oreille earshot (`ecoute`).
- Vitesse : ffmpeg sans apt, analyse des objets gardée (aperçu 2 min), vidéo ~30 min. Page : vidéo téléchargée par morceaux de 2 Mo.
- À faire par Issa : images Gemini de la fiche ép. 18 (Modibo inquiet / méfiant, Fatim contente, Awa méprisante…).

## Où on en est (21/10/2026)
- Assistant complet ajouté (Groq + Gemini) : format, discussion avec actions, images Gemini, essais de code. Tests sur la demande n° 5.
- Essai complet de la page (demande n° 9, comme sur le téléphone) : format → aperçu → planches (bouton « Envoyer ma réponse ») → discussion → corrections → aperçu → vidéo (19 min) → correction → vidéo (14 min : voix et morceaux de 12 s repris de la vidéo précédente). Bandeau « que faire maintenant » sur chaque épisode. Corrigé : les choix des planches n'étaient jamais enregistrés sur GitHub (pull --rebase sans autostash).
- Planches A / B / C automatiques ajoutées (local et GitHub) + rendu partiel automatique par morceaux.
- Épisode 15 « La rumeur » fini (v5) ; script : `exemples/episode15_la_rumeur.txt` (+ début réécrit : `exemples/episode15_debut_corrige.txt`).
- Plus tard : vues de dos des personnages qui n'en ont pas ; nettoyer le décor BUREAU (figurants) ; pose de Karim assis.
