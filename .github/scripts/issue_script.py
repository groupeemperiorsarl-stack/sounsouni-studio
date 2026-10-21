"""Lit la demande (issue) : écrit le script dans un fichier et dit quoi faire (apercu / video)."""
import json, os, re, sys
ev = json.load(open(os.environ['GITHUB_EVENT_PATH']))
issue = ev['issue']; body = issue.get('body') or ''
m = re.search(r"### Script de l'épisode\s*\n+```(?:text)?\n(.*?)\n```", body, re.S) or re.search(r"### Script de l'épisode\s*\n+(.*)$", body, re.S)
script = (m.group(1) if m else body).strip()
mode = 'video' if re.search(r'Vidéo complète', body) else 'apercu'
auto = 'true' if re.search(r'Mise au format par l.assistant puis aperçu', body) else 'false'
if not ev.get('comment') and re.search(r'Mise au format par l.assistant', body): mode = 'format'   # le téléphone envoie le script brut, GitHub le met au format
reponse = de = fin = arg = ''
if ev.get('comment'):   # commentaire « vidéo », « aperçu », « planches 1:20-1:45 » ou réponse aux planches « 1B 3C »
    c = ((ev['comment'].get('body') or '').strip().splitlines() or [''])[0].lower().strip(' .!')   # 1re ligne seulement (une signature peut suivre)
    m = re.fullmatch(r'planches?(?:\s+(?:de\s+)?(\d+:\d\d)\s*(?:-|à|a)\s*(\d+:\d\d))?', c)
    brut = ((ev['comment'].get('body') or '').strip().splitlines() or [''])[0].strip()
    if re.match(r'importer\s+\d+\s*=', c): mode = 'importer'; arg = re.sub(r'(?i)^importer\s+', '', brut)   # images Gemini envoyées depuis la page
    elif re.match(r'annuler import\s+[0-9a-f]{7,40}$', c): mode = 'annuler'; arg = c.split()[-1]
    elif re.match(r'essai code\s+[\w./-]+$', c): mode = 'essai'; arg = brut.split()[-1]   # modification du code proposée par l'assistant, sur une branche à part
    elif re.fullmatch(r'vid[ée]o', c): mode = 'video'
    elif re.fullmatch(r'fiches?( gemini)?', c): mode = 'fiche'
    elif re.fullmatch(r'(aper[çc]u|refaire)', c): mode = 'apercu'
    elif m: mode = 'apercu'; de, fin = m.group(1) or '', m.group(2) or ''
    elif re.fullmatch(r'(\d+\s*[:=]?\s*[a-d][\s,;]*)+', c): mode = 'apercu'; reponse = ' '.join(re.findall(r'\d+\s*[:=]?\s*[a-d]', c)).upper()
    else: mode = 'rien'
os.makedirs('demandes', exist_ok=True)
path = f"demandes/episode_{issue['number']}.txt"
open(path, 'w', encoding='utf-8').write(script + '\n')
with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"mode={mode}\npath={path}\nnumber={issue['number']}\nreponse={reponse}\nde={de}\nfin={fin}\narg={arg}\nauto={auto}\n")
print(mode, path, len(script), 'caractères', reponse, de, fin)
