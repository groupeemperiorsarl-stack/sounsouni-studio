"""Crée automatiquement la bouche ouverte des poses qui n'en ont pas (outil d'expressions LivePortrait)."""
import json, os, subprocess, sys
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); W = '/tmp/claude-0/automouth'; os.makedirs(W, exist_ok=True)
cat = json.load(open(A + '/catalog.json')); jobs = []; regions = {}
try: _R = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reglages.json'), encoding='utf-8'))
except Exception: _R = {}
OUV = os.environ.get('STUDIO_BOUCHE', str(_R.get('bouche', 0.2)))   # ouverture de la bouche (barbe épaisse : plus grand)
SEUL = set(filter(None, os.environ.get('STUDIO_POSES', '').split(',')))   # refaire seulement ces poses
for k, p in cat['poses'].items():
    if SEUL and k not in SEUL: continue
    if (p['mouth'] and not SEUL) or p['char'] in ('OBJET',) or '+' in p['char'] or p['posture'] in ('dos',) or 'cycle_marche' in ' '.join(p['tags']): continue
    im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); w, h = im.size
    frac = {'pied': 0.42, 'buste': 0.75, 'visage': 1.0}.get(p['frame'], 0.5)
    box = (0, 0, w, int(h * frac)); regions[k] = box
    b = Image.new('RGBA', (box[2], box[3]), (200, 200, 200, 255)); b.alpha_composite(im.crop(box)); b.convert('RGB').save(f'{W}/{k}.png')
    jobs.append(f'{W}/{k}_o.png|{W}/{k}.png|x|{OUV}|0|0|0|-0.25|0|0|0|0|0|0|0')
open(W + '/jobs.txt', 'w').write('\n'.join(jobs) + '\n'); json.dump(regions, open(W + '/regions.json', 'w'))
print(len(jobs), 'poses à traiter', flush=True)
subprocess.run([sys.executable, os.environ.get('STUDIO_LIVEPORTRAIT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp', 'lpgen.py')), W + '/jobs.txt'])
n = 0
for k, box in regions.items():
    o = f'{W}/{k}_o.png'
    if not os.path.exists(o): continue
    base = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); f = Image.open(o).convert('RGBA').resize((box[2], box[3]))
    f.putalpha(base.crop(box).getchannel('A')); im = base.copy(); im.paste(f, box[:2]); im.save(f'{A}/poses/{k}_o.webp', 'WEBP', quality=88)
    cat['poses'][k]['mouth'] = True; cat['poses'][k]['mouth_auto'] = True; n += 1
json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1); print('bouches créées', n)
