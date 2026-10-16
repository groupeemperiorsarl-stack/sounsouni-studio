"""Crée automatiquement une pose « sourire » (bouche fermée + ouverte) pour les personnages qui n'en ont pas,
en modifiant l'expression d'une pose existante avec LivePortrait. Utilisation : python autosmile.py [PERSO ...]"""
import json, os, subprocess, sys
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); W = '/tmp/claude-0/autosmile'; os.makedirs(W, exist_ok=True)
LP = os.environ.get('STUDIO_LIVEPORTRAIT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp', 'lpgen.py'))
cat = json.load(open(A + '/catalog.json')); P = cat['poses']
HAPPY = {'sourire', 'content', 'rire', 'grand_sourire'}
SOURCE = {'AWA': 'awa_bras_croises', 'MIMI': 'mim_machine'}   # visage de face, expression calme
def source_for(ch):
    if ch in SOURCE: return SOURCE[ch]
    c = [k for k, p in P.items() if p['char'] == ch and p['posture'] not in ('dos', 'tombe', 'marche') and 'cycle' not in ' '.join(p['tags'])]
    c.sort(key=lambda k: (('neutre' not in P[k]['tags']), P[k]['frame'] != 'buste', P[k]['frame'] != 'pied'))
    return c[0] if c else None
chars = sys.argv[1:] or sorted({p['char'] for p in P.values() if '+' not in p['char'] and p['char'] != 'OBJET'
                                and not any(set(q['tags']) & HAPPY for q in P.values() if q['char'] == p['char'] and 'mange' not in q['tags'])})
jobs, todo = [], {}
for ch in chars:
    k = source_for(ch)
    if not k: continue
    p = P[k]; im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); w, h = im.size
    frac = {'pied': 0.42, 'buste': 0.75, 'visage': 1.0}.get(p['frame'], 0.5); box = (0, 0, w, int(h * frac))
    b = Image.new('RGBA', box[2:], (200, 200, 200, 255)); b.alpha_composite(im.crop(box)); b.convert('RGB').save(f'{W}/{k}.png')
    new = ch.lower()[:3] + '_sourire_auto'; todo[new] = (k, box)
    jobs.append(f'{W}/{new}.png|{W}/{k}.png|x|x|0|0|0|1.3|12|0|0|0|0|0|0')
    jobs.append(f'{W}/{new}_o.png|{W}/{k}.png|x|0.18|0|0|0|1.3|12|0|0|0|0|0|0')
open(W + '/jobs.txt', 'w').write('\n'.join(jobs) + '\n'); print(len(todo), 'personnages :', ', '.join(todo), flush=True)
subprocess.run([sys.executable, LP, W + '/jobs.txt'])
for new, (k, box) in todo.items():
    if not all(os.path.exists(f'{W}/{new}{s}.png') for s in ('', '_o')): print('échec', new); continue
    base = Image.open(f'{A}/poses/{k}.webp').convert('RGBA')
    for s in ('', '_o'):
        f = Image.open(f'{W}/{new}{s}.png').convert('RGBA').resize(box[2:]); f.putalpha(base.crop(box).getchannel('A'))
        im = base.copy(); im.paste(f, box[:2]); im.save(f'{A}/poses/{new}{s}.webp', 'WEBP', quality=88)
    P[new] = dict(P[k], tags=['sourire', 'content', 'grand_sourire', 'rougit', 'fier', 'neutre'], mouth=True, auto=True)
    print('pose créée', new)
json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1)
