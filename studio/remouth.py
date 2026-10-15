"""Refait toutes les images « bouche ouverte » à partir de l'image fermée (LivePortrait), en ne gardant que la bouche :
les yeux, la tête et le corps restent exactement identiques, donc rien ne « danse » quand le personnage parle."""
import json, os, subprocess, sys, shutil
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); W = '/tmp/claude-0/remouth'; os.makedirs(W, exist_ok=True)
LP = os.environ.get('STUDIO_LIVEPORTRAIT', '/home/claude/lp/lpgen.py')
cat = json.load(open(A + '/catalog.json')); P = cat['poses']; jobs = []; boxes = {}
only = sys.argv[1:]
for k, p in P.items():
    if only and k not in only: continue
    if p['char'] == 'OBJET' or '+' in p['char'] or p['posture'] == 'dos' or 'cycle' in ' '.join(p['tags']): continue
    im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); w, h = im.size
    frac = {'pied': 0.42, 'buste': 0.75, 'visage': 1.0}.get(p['frame'], 0.5); box = (0, 0, w, int(h * frac)); boxes[k] = box
    b = Image.new('RGBA', box[2:], (200, 200, 200, 255)); b.alpha_composite(im.crop(box)); b.convert('RGB').save(f'{W}/{k}.png')
    sm = 0 if set(p['tags']) & {'sourire', 'rire', 'content', 'grand_sourire'} else -0.25
    jobs.append(f'{W}/{k}_o.png|{W}/{k}.png|x|0.38|0|0|0|{sm}|0|0|0|0|0|0|0')
open(W + '/jobs.txt', 'w').write('\n'.join(jobs) + '\n'); print(len(jobs), 'poses', flush=True)
subprocess.run([sys.executable, LP, W + '/jobs.txt'], cwd=os.path.dirname(LP), capture_output=True)
from render import mouth_only
os.makedirs(W + '/ancien', exist_ok=True); n = 0
for k, box in boxes.items():
    o = f'{W}/{k}_o.png'
    if not os.path.exists(o): print('échec', k); continue
    mouth_only(f'{W}/{k}.png', o)
    base = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); f = Image.open(o).convert('RGBA').resize(box[2:]); f.putalpha(base.crop(box).getchannel('A'))
    old = f'{A}/poses/{k}_o.webp'
    if os.path.exists(old): shutil.copy(old, f'{W}/ancien/{k}_o.webp')
    im = base.copy(); im.paste(f, box[:2]); im.save(old, 'WEBP', quality=90); P[k]['mouth'] = True; n += 1
json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1); print('bouches refaites', n)
