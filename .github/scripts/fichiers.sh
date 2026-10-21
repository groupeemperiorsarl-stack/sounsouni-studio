#!/bin/bash
# Range les fichiers d'une demande (aperçu, planches, vidéo légère) dans la branche « fichiers », lue par la page Studio mobile.
# Une seule version gardée (branche réécrite), et seulement les 6 dernières demandes, pour ne pas alourdir le dépôt.
# Utilisation : fichiers.sh <numéro de demande> <fichier> [<fichier>…]   (GH_TOKEN et GITHUB_REPOSITORY fournis par GitHub)
set -u; N=$1; shift; D=$(mktemp -d); U="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git clone -q --depth 1 --branch fichiers "$U" "$D" 2>/dev/null || { rm -rf "$D"; mkdir -p "$D"; git -C "$D" init -q; git -C "$D" checkout -q -b fichiers; }
mkdir -p "$D/$N"
for f in "$@"; do [ -f "$f" ] || continue; case "$f" in *_leger.mp4) cp "$f" "$D/$N/video.mp4";; *) cp "$f" "$D/$N/";; esac; done
date -u +%FT%TZ > "$D/$N/maj.txt"
cd "$D" && ls -d [0-9]* 2>/dev/null | sort -n | head -n -6 | xargs -r rm -rf
rm -rf .git && git init -q && git checkout -q -b fichiers && git add -A
git -c user.name=sounsouni-studio -c user.email=studio@sounsouni.pro commit -qm "Fichiers de la demande $N" && git push -qf "$U" fichiers && echo "fichiers rangés pour la demande $N"
