"""Lit la demande (issue) : écrit le script dans un fichier et dit quoi faire (apercu / video)."""
import json, os, re, sys
ev = json.load(open(os.environ['GITHUB_EVENT_PATH']))
issue = ev['issue']; body = issue.get('body') or ''
m = re.search(r"### Script de l'épisode\s*\n+```(?:text)?\n(.*?)\n```", body, re.S) or re.search(r"### Script de l'épisode\s*\n+(.*)$", body, re.S)
script = (m.group(1) if m else body).strip()
mode = 'video' if re.search(r'Vidéo complète', body) else 'apercu'
if ev.get('comment'):   # commentaire « vidéo » ou « refaire » sur la demande
    c = (ev['comment'].get('body') or '').lower().strip(' .!\n')   # seulement un commentaire d'un seul mot
    if re.fullmatch(r'vid[ée]o', c): mode = 'video'
    elif re.fullmatch(r'(aper[çc]u|refaire)', c): mode = 'apercu'
    else: mode = 'rien'
os.makedirs('demandes', exist_ok=True)
path = f"demandes/episode_{issue['number']}.txt"
open(path, 'w', encoding='utf-8').write(script + '\n')
with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"mode={mode}\npath={path}\nnumber={issue['number']}\n")
print(mode, path, len(script), 'caractères')
