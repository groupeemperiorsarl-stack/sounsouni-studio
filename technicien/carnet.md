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

## format
- 2026-10-22 · Claude · Groq répond 429 « try again in Xs » → limite par minute → attendre le temps demandé ; « per day » → passer à l'IA suivante (Cerebras, OpenRouter, Gemini, puis modèle libre sur la machine).
- 2026-10-22 · Claude · Réplique « Je… je… » prise pour une réplique inventée → mots trop courts → ne compter que les mots de 3 lettres et plus.
- 2026-10-22 · Claude · Un personnage absent du décor qui parle → il est mis « au téléphone » (écran d'appel), jamais dans le décor.

## ia
- 2026-10-22 · Claude · Gemini 503 / « surchargé » → les modèles gratuits changent souvent de nom → essayer la liste des modèles « flash » l'un après l'autre, et attendre 30 s entre deux tours.
- 2026-10-22 · Claude · Modèle libre sur la machine : les fichiers tout prêts de llama.cpp ne sont plus publiés → le compiler depuis les sources ; réponse longue coupée par Node après 5 min → lire la réponse petit à petit (streaming).

## images
- 2026-10-22 · Claude · LivePortrait plante sans « onnx » → paquet manquant → ajouté à l'installation (studio/lp/install.sh).
- 2026-10-22 · Claude · Boutons « 🎞 Planche » qui montraient planche_1 / planche_2 (planches d'épisode) → nom mal filtré → seules les planches « planche_<perso>_<tour|action>_… » sont des mini-vidéos.

## mise-en-scene

## pour-claude
