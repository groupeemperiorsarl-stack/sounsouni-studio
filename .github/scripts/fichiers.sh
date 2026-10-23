#!/bin/bash
# Range les fichiers d'une demande (aperçu, planches, vidéo légère, fiche, essais…) dans la branche « fichiers », lue par la page Studio mobile.
# Une seule version gardée (branche réécrite), et seulement les 6 dernières demandes, pour ne pas alourdir le dépôt.
# Plusieurs fabrications peuvent finir en même temps : on ne pousse que si la branche n'a pas bougé depuis qu'on l'a lue (sinon on recommence).
# Utilisation : fichiers.sh <numéro de demande> <fichier> [<fichier>…]   (GH_TOKEN et GITHUB_REPOSITORY fournis par GitHub)
set -u; N=$1; shift; U="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
for essai in 1 2 3 4 5 6; do
  D=$(mktemp -d); AVANT=$(git ls-remote "$U" refs/heads/fichiers | cut -f1)
  if [ -n "$AVANT" ]; then git clone -q --depth 1 --branch fichiers "$U" "$D"; else git -C "$D" init -q; fi
  mkdir -p "$D/$N"
  case " $* " in *apercu_plans.png*) rm -f "$D/$N"/planche_*.png "$D/$N/planches.html" "$D/$N/planches.json";; esac
  case " $* " in *fiche_gemini.html*) rm -f "$D/$N"/image_*.jpg;; esac   # nouvelle fiche : les images à joindre de l'ancienne fiche disparaissent   # nouvel aperçu : les anciennes planches (déjà répondues) disparaissent
  for f in "$@"; do [ -f "$f" ] || continue; case "$f" in *_leger.mp4) cp "$f" "$D/$N/video.mp4";; *) cp "$f" "$D/$N/";; esac; done
  date -u +%FT%TZ > "$D/$N/maj.txt"
  ( cd "$D" && ls -d [0-9]* 2>/dev/null | sort -n | head -n -6 | xargs -r rm -rf
    rm -rf .git && git init -q && git checkout -q -b fichiers && git add -A
    git -c user.name=sounsouni-studio -c user.email=studio@sounsouni.pro commit -qm "Fichiers de la demande $N"
    git push -q --force-with-lease="fichiers:${AVANT}" "$U" fichiers ) && { echo "fichiers rangés pour la demande $N"; rm -rf "$D"; exit 0; }
  rm -rf "$D"; echo "la branche a bougé pendant l'envoi, nouvel essai ($essai)"; sleep $((RANDOM % 10 + 5))
done
echo "fichiers NON rangés pour la demande $N"; exit 1
