#!/bin/bash
# Allume le technicien de garde (un seul ordinateur, 6 h) s'il n'y en a pas déjà un. $1 = message d'Issa à traiter (facultatif).
# Code de sortie 0 = un technicien de garde s'occupe de tout ; 1 = impossible de l'allumer.
R=$GITHUB_REPOSITORY
N=$(gh api "repos/$R/actions/workflows/technicien-garde.yml/runs?per_page=10" --jq '[.workflow_runs[] | select(.status=="in_progress" or .status=="queued")] | length' 2>/dev/null || echo x)
[ "$N" = "x" ] && exit 1
if [ "$N" != "0" ]; then echo "technicien de garde déjà allumé"; exit 0; fi
gh workflow run technicien-garde.yml -f message="${1:-}" && echo "technicien de garde allumé (6 h)"
