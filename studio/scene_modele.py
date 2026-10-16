"""Scène modèle : une image de plan d'ensemble bien composée (faite par Gemini et validée par Issa) est analysée par l'application.
Elle y retrouve chaque personnage (détecteur libre OWLv2 + couleurs de ses habits), mesure sa place (gauche / droite), sa taille,
la hauteur de ses pieds (devant / derrière), et compare avec sa propre mise en scène du même plan.
Lancer avec l'environnement des voix (torch + transformers) :
  $STUDIO_TTS_PY studio/scene_modele.py image.png BAKARY,MODIBO,DIASABI,FATIM,KARIM -o sortie   [--plans plans.json --plan 19]
→ sortie/mesures.json et sortie/comparaison.jpg (image modèle à gauche, plan de l'application à droite, mêmes étiquettes)."""
import os, sys, json, argparse, itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
CAT = json.load(open(f'{A}/catalog.json'))

def signature(im, mask=None):
    """Couleurs des habits (teinte × saturation), sans les gris ni les tons de peau trop sombres."""
    hsv = np.asarray(im.convert('RGB').convert('HSV')).reshape(-1, 3).astype(int)
    ok = (hsv[:, 1] > 60) & (hsv[:, 2] > 50)
    if mask is not None: ok &= mask.reshape(-1)
    h = np.histogram2d(hsv[ok, 0], hsv[ok, 1], bins=[18, 4], range=[[0, 256], [60, 256]])[0].ravel()
    return h / (h.sum() + 1e-6)
def ref_signature(char):
    """Signature d'un personnage, d'après ses poses debout (habits de tous les jours)."""
    hs = []
    for k, p in CAT['poses'].items():
        if p['char'] != char or '@' in k or p.get('tenue'): continue
        im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); a = np.asarray(im)[:, :, 3] > 200
        hs.append(signature(im, a))
        if len(hs) >= 4: break
    return np.mean(hs, 0)
def personnes(im, seuil=0.05):
    import torch
    from transformers import Owlv2Processor, Owlv2ForObjectDetection
    n = 'google/owlv2-base-patch16-ensemble'; proc = Owlv2Processor.from_pretrained(n); model = Owlv2ForObjectDetection.from_pretrained(n).eval()
    W = im.convert('RGB'); s = 960 / max(W.size); W2 = W.resize((int(W.width * s), int(W.height * s)))
    inp = proc(text=[['a cartoon person standing', 'a cartoon person sitting on a bench', 'a man', 'a woman']], images=W2, return_tensors='pt')
    with torch.no_grad(): out = model(**inp)
    side = max(W2.size)   # OWLv2 travaille sur une image carrée (remplie en bas / à droite)
    pp = getattr(proc, 'post_process_object_detection', None) or proc.post_process_grounded_object_detection
    r = pp(out, threshold=seuil, target_sizes=torch.tensor([[side, side]]))[0]
    boxes = [(float(sc), [float(v) / s for v in b]) for sc, b in zip(r['scores'], r['boxes'])]
    boxes.sort(key=lambda t: -t[0]); keep = []
    for sc, b in boxes:   # on garde la meilleure boîte quand deux se recouvrent beaucoup
        if all(iou(b, k[1]) < 0.5 for k in keep): keep.append((sc, b))
    return keep
def iou(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    i = max(0, x1 - x0) * max(0, y1 - y0); u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / (u + 1e-6)
def attribuer(im, boxes, chars):
    """Chaque personnage du plan ↔ une boîte, en choisissant l'ensemble où les couleurs se ressemblent le plus."""
    refs = {c: ref_signature(c) for c in chars}
    sig = [signature(im.crop(tuple(int(v) for v in b))) for _, b in boxes]
    sim = lambda c, i: float(np.minimum(refs[c], sig[i]).sum())
    best, bs, k = None, -1, min(len(chars), len(boxes))
    for sub in itertools.combinations(chars, k):   # moins de boîtes que de personnages : on place ceux qui ressemblent le mieux
        for perm in itertools.permutations(range(len(boxes)), k):
            s = sum(sim(c, i) for c, i in zip(sub, perm))
            if s > bs: best, bs = list(zip(sub, perm)), s
    return {c: boxes[i][1] for c, i in best}, {c: round(sim(c, i), 2) for c, i in best}
def mesures(pos, W, H):
    return {c: {'x': round((b[0] + b[2]) / 2 / W, 3), 'pieds': round(b[3] / H, 3), 'tete': round(b[1] / H, 3), 'hauteur': round((b[3] - b[1]) / H, 3)} for c, b in pos.items()}
def depuis_app(shot):
    """Mêmes mesures pour un plan de l'application (plans.json)."""
    out = {}
    for a in shot.get('actors', []):
        if a.get('fg') and a.get('silhouette'): continue
        out[a['who']] = {'x': round(a['x'] / 1080, 3), 'pieds': round(a['by'] / 1920, 3), 'tete': round((a['by'] - a['h']) / 1920, 3), 'hauteur': round(a['h'] / 1920, 3)}
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('image'); ap.add_argument('persos'); ap.add_argument('-o', '--out', default='sortie_scene')
    ap.add_argument('--plans', default=None); ap.add_argument('--plan', type=int, default=None); ap.add_argument('--rendu', default=None, help="image du plan de l'application")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    im = Image.open(a.image).convert('RGB'); chars = [c.strip().upper() for c in a.persos.split(',')]
    boxes = personnes(im); print(f'{len(boxes)} personnes trouvées')
    pos, conf = attribuer(im, boxes, chars); m = mesures(pos, im.width, im.height)
    res = {'modele': m, 'confiance_couleurs': conf}
    if a.plans and a.plan is not None: res['application'] = depuis_app(json.load(open(a.plans))[a.plan])
    json.dump(res, open(os.path.join(a.out, 'mesures.json'), 'w'), ensure_ascii=False, indent=1)
    # image de comparaison
    H = 960; L = im.resize((int(im.width * H / im.height), H)); d = ImageDraw.Draw(L); f = ImageFont.load_default()
    for c, b in pos.items():
        sc = H / im.height; bb = [v * sc for v in b]; d.rectangle(bb, outline=(255, 120, 0), width=3); d.text((bb[0] + 4, bb[1] + 4), c, fill=(255, 255, 255), font=f)
    imgs = [L]
    if a.rendu and 'application' in res:
        R = Image.open(a.rendu).convert('RGB').resize((int(1080 * H / 1920), H)); dr = ImageDraw.Draw(R)
        for c, v in res['application'].items():
            x = v['x'] * R.width; y0, y1 = v['tete'] * H, v['pieds'] * H; dr.line([(x, y0), (x, y1)], fill=(0, 200, 255), width=3); dr.text((x + 4, y0 + 4), c, fill=(255, 255, 255), font=f)
        imgs.append(R)
    C = Image.new('RGB', (sum(i.width for i in imgs) + 10 * (len(imgs) - 1), H), 'white'); x = 0
    for i in imgs: C.paste(i, (x, 0)); x += i.width + 10
    C.save(os.path.join(a.out, 'comparaison.jpg'), quality=85)
    print(json.dumps(res, ensure_ascii=False, indent=1))
if __name__ == '__main__': main()
