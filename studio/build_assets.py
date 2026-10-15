"""Construit studio/assets/ (poses, bouches, décors, voix) et studio/assets/catalog.json à partir des images des épisodes."""
import os, json, shutil
from PIL import Image
from catalog_src import P, DECORS, HEIGHT, VOICES, VOICE_SRC, H
OUT = os.path.join(os.path.dirname(__file__), 'assets')
ORIG_OPEN = {'ep1/hd/B1', 'ep2/hd/W7'}
EXTRA_ALT = {'ep11/hd/A20': 'ep13/hd/A20~alt', 'ep7/hd/AH1': 'ep13/hd/AH1~alt', 'ep8/hd/MO': 'ep14/hd/MOUo',
             'ep13/hd/KADI': 'ep13/hd/KADI~alt', 'ep13/hd/KADIS': 'ep13/hd/KADIS~alt', 'ep13/hd/KADIB': 'ep13/hd/KADIB~alt',
             'ep12/hd/MI': 'ep12/hd/MI~alt', 'ep10/hd/ME': 'ep12/hd/ME~alt'}
def ex(p): return os.path.exists(H + p + '.png')
def save(src, dst, maxh=1600):
    im = Image.open(H + src + '.png').convert('RGBA'); bb = im.getbbox()
    if bb: im = im.crop(bb)
    if im.height > maxh: im = im.resize((int(im.width * maxh / im.height), maxh), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=88, method=4); return im.size
os.makedirs(OUT + '/poses', exist_ok=True); os.makedirs(OUT + '/decors', exist_ok=True); os.makedirs(OUT + '/voix', exist_ok=True)
cat = {'poses': {}, 'decors': {}, 'height': HEIGHT, 'voices': VOICES}
for key, ch, frame, posture, tags, src in P:
    if not ex(src) and not (ex(src + 'c') and ex(src + 'o')): print('MANQUE', key, src); continue
    closed, opened = src, None
    if ex(src + 'c') and ex(src + 'o'): closed, opened = src + 'c', src + 'o'
    elif src in EXTRA_ALT and ex(EXTRA_ALT[src]): opened = EXTRA_ALT[src]
    elif ex(src + '~alt'):
        if src in ORIG_OPEN: closed, opened = src + '~alt', src
        else: opened = src + '~alt'
    # bbox commun pour que bouche ouverte/fermée se superposent exactement
    base = Image.open(H + closed + '.png').convert('RGBA'); bb = base.getbbox()
    def cut(p, d):
        im = Image.open(H + p + '.png').convert('RGBA').resize(base.size).crop(bb)
        if im.height > 1600: im = im.resize((int(im.width * 1600 / im.height), 1600), Image.LANCZOS)
        im.save(d, 'WEBP', quality=88, method=4); return im.size
    size = cut(closed, f'{OUT}/poses/{key}.webp')
    if opened: cut(opened, f'{OUT}/poses/{key}_o.webp')
    cat['poses'][key] = {'char': ch, 'frame': frame, 'posture': posture, 'tags': tags.split(), 'mouth': bool(opened), 'size': size}
for k, src in DECORS.items():
    im = Image.open(H + src + '.png').convert('RGB'); im.save(f'{OUT}/decors/{k}.jpg', quality=88); cat['decors'][k] = im.size
for v, src in VOICE_SRC.items():
    if os.path.exists(H + src): shutil.copy(H + src, f'{OUT}/voix/{v}')
for v in ('ref_bakary.wav', 'ref_awa2.wav', 'ref_modibo.wav', 'ref_diasabi.wav'): shutil.copy(H + 'tts/' + v, f'{OUT}/voix/{v}')
import numpy as np
for k, p in cat['poses'].items():
    a = np.asarray(Image.open(f'{OUT}/poses/{k}.webp'))[..., 3] > 100; ys, xs = np.nonzero(a[:max(5, int(a.shape[0] * 0.12))])
    p['head_x'] = round(float(xs.mean() / a.shape[1]), 3) if len(xs) else 0.5
json.dump(cat, open(OUT + '/catalog.json', 'w'), ensure_ascii=False, indent=1)
print(len(cat['poses']), 'poses', sum(1 for p in cat['poses'].values() if p['mouth']), 'avec bouche')
