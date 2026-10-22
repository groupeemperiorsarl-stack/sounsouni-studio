#!/bin/bash
# Grand ménage de l'historique du dépôt (automatique, sans Claude) : on retire de l'HISTORIQUE les fichiers qui n'existent plus
# aujourd'hui (anciennes mini-vidéos, anciennes images remplacées, essais). Les fichiers actuels ne changent pas.
# Utilisation : grand_menage.sh <dossier du clone complet> [essai]   (essai = calcule le gain sans rien envoyer)
set -e; D=$1; MODE=${2:-essai}; cd "$D"
AVANT=$(git count-objects -vH | grep size-pack | cut -d: -f2 | tr -d ' ')
git log --all --pretty=format: --name-only --diff-filter=AD | sort -u | grep -v '^$' > /tmp/tous.txt
git ls-tree -r --name-only HEAD | sort -u > /tmp/actuels.txt
comm -23 /tmp/tous.txt /tmp/actuels.txt | grep -vE '^\.github/|^docs/|^outils/|\.py$|\.md$|\.json$|\.ya?ml$|\.txt$|\.sh$|\.html$' > /tmp/a_retirer.txt || true   # seulement les gros fichiers (images, sons, vidéos) disparus
echo "fichiers disparus à retirer de l'historique : $(wc -l < /tmp/a_retirer.txt)"
[ -s /tmp/a_retirer.txt ] || { echo "rien à retirer"; exit 0; }
git filter-repo --force --invert-paths --paths-from-file /tmp/a_retirer.txt > /dev/null
git reflog expire --expire=now --all && git gc -q --prune=now --aggressive
APRES=$(git count-objects -vH | grep size-pack | cut -d: -f2 | tr -d ' ')
echo "historique : $AVANT → $APRES"
if [ "$MODE" = "vrai" ]; then git remote add origin "$URL" 2>/dev/null || git remote set-url origin "$URL"; git push -q --force origin main && echo "historique allégé envoyé"; fi
