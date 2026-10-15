# Sounsouni Studio

Transforme un **script détaillé** (format : `docs/GUIDE_SCENARISTE.md`) en épisode animé vertical 1080×1920,
voix comprises, sans intervention humaine.

## Chaîne de fabrication
1. `script.py` — lit le script (décors, plans, répliques, émotions `{…}`, réactions et bruitages `[…]`).
2. `voices.py` + `tts_worker.py` — voix des personnages (Chatterbox multilingue, voix de référence dans `assets/voix`),
   contrôle automatique par Whisper (relance si la phrase est mal prononcée), horaires de chaque mot.
3. `director.py` — mise en scène : choix des poses dans `assets/catalog.json` selon l'émotion, plans d'ensemble
   (même sol, profondeur, pas de chevauchement), gros plans centrés sur le visage, réactions en contre-champ, objets, écrans.
4. `render.py` + `gfx.py` — images (bouche qui bouge avec la voix, marche, effets, bulles), rendu en parallèle par morceaux.
5. `audio.py` + `music.py` — voix placées, bruitages, ambiances, musique balafon, mixage et version légère < 28 Mo.

## Installation
```
pip install -r studio/requirements.txt
python3 -m venv ~/tts && ~/tts/bin/pip install -r studio/requirements-voix.txt
export STUDIO_TTS_PY=~/tts/bin/python
```

## Utilisation
```
python -m studio exemples/episode14_retour_expediteur.txt -o sortie_ep14
python -m studio mon_script.txt --plans-seulement     # aperçu rapide des plans
STUDIO_FAUSSES_VOIX=1 python -m studio mon_script.txt # essai sans voix réelles
```
Machine minimale : 2 processeurs, 8 Go de mémoire, pas de carte graphique nécessaire.

## Outils de préparation (une seule fois)
`catalog_src.py` + `build_assets.py` reconstruisent les poses et décors à partir des images des épisodes ;
`automouth.py` crée les bouches ouvertes manquantes (LivePortrait).
