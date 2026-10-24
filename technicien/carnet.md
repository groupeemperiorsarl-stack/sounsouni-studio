# Carnet du studio — leçons apprises en travaillant
Lu par toutes les IA du studio (technicien, assistant de discussion, mise au format) avant de travailler. Une leçon = symptôme → cause → remède.
Écrit par le technicien (outil « noter » et bilan de fin de recherche) et par l'assistant de discussion (action « note »). Rangé automatiquement quand il devient trop long.

## fabrication
- 2026-10-22 · Claude · Étape « voix » bloquée plus de 30 min dans « Outils » → l'installation pip attendait un serveur sans fin → arrêter la fabrication et la relancer ; depuis, cache des outils + délai maximum de 25 min sur l'installation.
- 2026-10-22 · Claude · Le commentaire « vidéo » lançait une mini-vidéo → deux modes portaient le même nom → le mode des mini-vidéos s'appelle « minivideo » ; vérifier le mode lu dans le journal de « Demande d'épisode ».
- 2026-10-21 · Claude · Choix des planches jamais gardés sur GitHub → « git pull --rebase » sans « --autostash » échouait en silence → toujours « --autostash » quand on enregistre pendant une fabrication.
- 2026-10-22 · Claude · « Bloqué par GitHub » / fabrications refusées → plus de minutes ou problème de facturation → le dépôt est public (minutes gratuites) ; si ça revient, regarder la page de facturation, ce n'est pas le code.
- 2026-10-21 · Claude · Une vidéo refaite après une petite correction ne refait que les morceaux de 12 s changés → si tout est refait, regarder si les poses ont changé (poses.stamp) : c'est normal après un import d'images.
- 2026-10-22 · Gemini · Outil `demande` renvoie 404 pour un numéro d'épisode → le numéro d'épisode n'est pas le numéro du ticket GitHub → utiliser `demandes` pour trouver le vrai numéro de ticket.
- 2026-10-22 · Claude · Une étape attend longtemps dans « Outils » alors que le travail lui-même dure quelques secondes → « apt-get install ffmpeg » mettait jusqu'à 16 min sur certaines machines (serveur Ubuntu lent), et toute la fabrication attend la plus lente → ffmpeg est maintenant pris tout prêt sur GitHub (.github/scripts/ffmpeg.sh, 16 s) ; pour vérifier, comparer l'heure de début de « Outils » et la fin de l'installation dans le journal de chaque machine.
- 2026-10-22 · Gemini · Aperçu bloqué par JSONDecodeError → une virgule en trop dans le fichier .choix.json de l'épisode → enlever la virgule dans le JSON.
- 2026-10-23 · Gemini · Étape voix qui plante avec ModuleNotFoundError cv2 → un outil image importé en haut d'un fichier commun → importer cv2 et render uniquement au besoin dans les fonctions de rendu (déjà intégré par Claude).
- 2026-10-23 · Gemini · L'aperçu réussit mais la vidéo échoue → l'étape voix n'est pas testée lors de la génération d'aperçu → vérifier les imports dans le moteur audio indépendamment du succès des images.

## format
- 2026-10-22 · Claude · Groq répond 429 « try again in Xs » → limite par minute → attendre le temps demandé ; « per day » → passer à l'IA suivante (Cerebras, OpenRouter, Gemini, puis modèle libre sur la machine).
- 2026-10-22 · Claude · Réplique « Je… je… » prise pour une réplique inventée → mots trop courts → ne compter que les mots de 3 lettres et plus.
- 2026-10-22 · Claude · Un personnage absent du décor qui parle → il est mis « au téléphone » (écran d'appel), jamais dans le décor.

## ia
- 2026-10-22 · Claude · Gemini 503 / « surchargé » → les modèles gratuits changent souvent de nom → essayer la liste des modèles « flash » l'un après l'autre, et attendre 30 s entre deux tours.
- 2026-10-22 · Claude · Modèle libre sur la machine : les fichiers tout prêts de llama.cpp ne sont plus publiés → le compiler depuis les sources ; réponse longue coupée par Node après 5 min → lire la réponse petit à petit (streaming).
- 2026-10-23 · Gemini · Quota journalier Gemini épuisé → limite de l'offre gratuite → attendre le reset de 8h du matin (heure Bamako) ou changer de modèle.

## images
- 2026-10-22 · Claude · LivePortrait plante sans « onnx » → paquet manquant → ajouté à l'installation (studio/lp/install.sh).
- 2026-10-22 · Claude · Boutons « 🎞 Planche » qui montraient planche_1 / planche_2 (planches d'épisode) → nom mal filtré → seules les planches « planche_<perso>_<tour|action>_… » sont des mini-vidéos.
- 2026-10-23 · Costumier (gemini-3.8-flash) · Lors d'une fête ou d'une cérémonie, toujours prévoir une tenue habillée pour chaque invité régulier et garder les couples ensemble dans les plans larges.
- 2026-10-23 · Costumier (gemini-3.8-flash) · Pour une fête ou un mariage, penser à habiller tous les invités principaux dès l'écriture du script.
- 2026-10-23 · Costumier (gemini-3.8-flash) · Pour une soirée de fête, toujours déclarer une tenue d'invité pour chaque personnage présent dès le début de la scène.

## mise-en-scene
- 2026-10-24 · Assistant · Réplique qui répond à une pensée → un personnage ne peut pas entendre la pensée d'un autre → faire dire la réplique à voix haute si quelqu'un doit y réagir.

## son
- 2026-10-22 · Claude · Cri des grillons / cigales trop fort et stressant (épisode 18, scène de nuit d'Awa) → l'ancien son cricket.wav ressemblait à une alarme (earshot : « error buzz ») et restait à 10 dB seulement sous les voix → grillons fabriqués en code (studio/ambiances.py) et ambiance toujours 24 dB sous les voix (réglage ambiance_sous_voix) ; l'oreille (ecoute.txt) signale une scène aux aigus perçants.

## pour-claude
