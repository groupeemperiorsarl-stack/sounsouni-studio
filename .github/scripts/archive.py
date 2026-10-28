"""MÉMOIRE DU SCÉNARISTE : rassemble le script complet (dernière version) de chaque épisode déjà fait dans docs/EPISODES.md.
Lu par l'onglet ✍️ Scénariste de la page Studio mobile. Refait tout seul à chaque script enregistré (demande.yml).
Pour chaque numéro d'épisode : la demande la plus récemment modifiée (git), sinon le fichier d'exemples le plus complet. Les tests et extraits sont ignorés."""
import glob, os, re, subprocess
def date(f):
    try: return int(subprocess.check_output(['git', 'log', '-1', '--format=%ct', '--', f], text=True).strip() or 0)
    except Exception: return 0
choix = {}; ISSUE = os.environ.get('ISSUE', '')
if ISSUE and os.path.exists('docs/EPISODES.md'):   # sur GitHub (copie sans historique) : on garde l'archive et on remplace seulement l'épisode de cette demande
    for m in re.finditer(r'^## Épisode (\d+) : ([^\n]+)\n\(source : ([^\n]+?)\)\n```text\n(.*?)\n```', open('docs/EPISODES.md', encoding='utf-8').read(), re.S | re.M):
        choix[int(m.group(1))] = ((False, 0), m.group(3), m.group(2), m.group(4))
fichiers = [f'demandes/episode_{ISSUE}.txt'] if ISSUE else glob.glob('exemples/*.txt') + glob.glob('demandes/episode_*.txt')
for f in fichiers:
    if not os.path.exists(f): continue
    t = open(f, encoding='utf-8').read(); m = re.search(r'^TITRE:.*?[ÉE]pisode\s+(\d+)\s*:\s*(.+)$', t, re.M)
    if not m or re.search(r'test|extrait|essai', m.group(0), re.I) or len(t) < 3000: continue
    n = int(m.group(1)); cle = (True, 9e18) if ISSUE else (f.startswith('demandes'), date(f) if f.startswith('demandes') else len(t))
    if n not in choix or cle > choix[n][0]: choix[n] = (cle, f, m.group(2).strip(), t.strip())
out = ['# Les épisodes déjà faits (scripts complets, dernière version)',
       "Mémoire du scénariste : fabriqué tout seul par `.github/scripts/archive.py`. Ne pas modifier à la main.", '']
for n in sorted(choix):
    _, f, titre, t = choix[n]
    out += [f'## Épisode {n} : {titre}', f'(source : {f})', '```text', t, '```', '']
open('docs/EPISODES.md', 'w', encoding='utf-8').write('\n'.join(out))
print(f"docs/EPISODES.md : {len(choix)} épisodes ({', '.join(map(str, sorted(choix)))})")
