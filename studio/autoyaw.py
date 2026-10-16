"""Mesure l'orientation du visage (yaw, en degrés) de chaque pose avec LivePortrait et l'écrit dans le catalogue ('yaw').
yaw > 0 / < 0 : sens mesuré par LivePortrait (voir 'face_dir' : +1 = regarde vers la droite de l'image)."""
import json, os, subprocess, sys
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); W = '/tmp/claude-0/autoyaw'; os.makedirs(W, exist_ok=True)
LPY = os.environ.get('STUDIO_LIVEPORTRAIT_YAW', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp', 'lpyaw.py'))
cat = json.load(open(A + '/catalog.json')); P = cat['poses']; jobs = []
for k, p in P.items():
    if p['char'] == 'OBJET' or '+' in p['char'] or p['posture'] == 'dos' or 'yaw' in p: continue
    im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); w, h = im.size
    frac = {'pied': 0.42, 'buste': 0.75, 'visage': 1.0}.get(p['frame'], 0.5)
    b = Image.new('RGBA', (w, int(h * frac)), (200, 200, 200, 255)); b.alpha_composite(im.crop((0, 0, w, int(h * frac)))); b.convert('RGB').save(f'{W}/{k}.png')
    jobs.append(f'{k}|{W}/{k}.png')
open(W + '/jobs.txt', 'w').write('\n'.join(jobs) + '\n')
subprocess.run([sys.executable, LPY, W + '/jobs.txt', W + '/yaw.json'], cwd=os.path.dirname(LPY))
r = json.load(open(W + '/yaw.json'))
for k, v in r.items():
    if v: P[k]['yaw'] = round(v[0], 1)
json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1); print('orientations mesurées', sum(1 for v in r.values() if v))
