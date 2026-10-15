"""Reconnaît tout seul les objets visibles sur chaque pose (OWLv2, modèle libre de Google) et les note dans le catalogue.
Une pose avec un objet (brochette, téléphone…) ne sera choisie que si le script le demande.
Utilisation : python autotag.py            (seulement les poses pas encore analysées)
              python autotag.py --tout     (tout refaire)"""
import json, os, sys
import numpy as np
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
# question posée au modèle -> étiquette dans le catalogue
QUERIES = {
    'a skewer of grilled meat': 'brochette', 'a mobile phone': 'telephone', 'a smartphone in a hand': 'telephone',
    'a serving tray with cups': 'plateau', 'a banknote': 'billet', 'paper money': 'billet', 'a bottle': 'bouteilles',
    'a thermos flask': 'bouteilles', 'an open book': 'livre', 'a notebook': 'livre', 'a metal teapot': 'the', 'a glass of tea': 'verre',
    'a cardboard box': 'boite', 'a box of cupcakes': 'boite', 'a cupcake': 'gateau', 'a woven basket': 'panier', 'a donut': 'beignets',
    'an umbrella': 'parapluie', 'a large roll of fabric': 'rouleau', 'a dress on a hanger': 'robe', 'a wooden spoon': 'louche',
    'a handbag': 'sac', 'a playing card': 'cartes', 'a business card': 'carte', 'a barbecue grill': 'grill', 'a wooden door': 'porte',
    'a car': 'voiture', 'a hoverboard': 'hoverboard', 'a walking cane': 'canne', 'a sewing machine': 'machine',
    'tears on the cheek': 'larmes', 'a teardrop on a face': 'larmes', 'a kebab on a stick': 'brochette', 'food on a stick': 'brochette',
}
THR = {'larmes': 0.33, 'telephone': 0.22, 'parapluie': 0.5, 'brochette': 0.22}
DEF_THR = 0.25
def load():
    from transformers import Owlv2Processor, Owlv2ForObjectDetection
    import torch; torch.set_num_threads(2)
    n = 'google/owlv2-base-patch16-ensemble'
    return Owlv2Processor.from_pretrained(n), Owlv2ForObjectDetection.from_pretrained(n).eval()
def detect(proc, model, im):
    import torch
    W = Image.new('RGB', im.size, 'white'); W.paste(im, (0, 0), im)
    W.thumbnail((960, 960))
    texts = [list(QUERIES)]
    inp = proc(text=texts, images=W, return_tensors='pt')
    with torch.no_grad(): out = model(**inp)
    s = max(W.size); pp = getattr(proc, 'post_process_grounded_object_detection', None) or proc.post_process_object_detection
    res = pp(out, threshold=0.12, target_sizes=torch.tensor([[s, s]]))[0]
    found = {}
    for sc, lab, box in zip(res['scores'].tolist(), res['labels'].tolist(), res['boxes'].tolist()):
        tag = QUERIES[texts[0][lab]]
        if sc >= THR.get(tag, DEF_THR): found[tag] = max(found.get(tag, 0), round(sc, 2))
    return found
def todo_list(tout=False):
    P = json.load(open(A + '/catalog.json'))['poses']
    return [k for k, p in P.items() if p['char'] != 'OBJET' and '@' not in k and (tout or 'props_auto' not in p)]
def shard(n_shards, i, out, tout=False):
    """Une part du travail (pour le faire sur plusieurs ordinateurs en même temps) : résultats dans un fichier."""
    keys = todo_list(tout)[i::n_shards]; proc, model = load(); res = {}
    for k in keys:
        res[k] = detect(proc, model, Image.open(f'{A}/poses/{k}.webp').convert('RGBA')); print(k, res[k], flush=True)
    json.dump(res, open(out, 'w'))
def apply(found_by_key):
    """Écrit les objets trouvés dans le catalogue (remplace les anciennes notes d'objets)."""
    cat = json.load(open(A + '/catalog.json')); P = cat['poses']
    objs = set(QUERIES.values())
    try:
        import catalog_src; src = {e[0]: set(e[4].split()) for e in catalog_src.P}
    except Exception: src = {}
    for k, f in found_by_key.items():
        if k not in P: continue
        p = P[k]; keep = src.get(k, set())
        p['tags'] = [t for t in p['tags'] if t not in objs or t in keep or t in f]
        for t in f:
            if t not in p['tags']: p['tags'].append(t)
        p['props_auto'] = f; p['props'] = sorted(t for t in f if t != 'machine')
    json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1)
def run(only=(), tout=False):
    cat = json.load(open(A + '/catalog.json')); P = cat['poses']
    proc, model = load(); n = 0
    for k, p in P.items():
        if only and k not in only: continue
        if p['char'] == 'OBJET' or (not tout and not only and 'props_auto' in p): continue
        im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA')
        f = detect(proc, model, im)
        # un objet qui fait partie du lieu choisi par le script (machine, grill) reste une étiquette, pas un « objet en trop »
        p['props_auto'] = f; p['props'] = sorted(t for t in f if t not in ('machine',))
        for t in f:
            if t not in p['tags']: p['tags'].append(t)
        n += 1; print(k, f, flush=True)
        if n % 10 == 0: json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(cat, open(A + '/catalog.json', 'w'), ensure_ascii=False, indent=1); print('poses analysées', n)
if __name__ == '__main__':
    if '--part' in sys.argv:   # --part i/n fichier.json
        i, n = map(int, sys.argv[sys.argv.index('--part') + 1].split('/')); shard(n, i, sys.argv[sys.argv.index('--part') + 2], '--tout' in sys.argv)
    elif '--fusion' in sys.argv:
        import glob; allf = {}
        for f in glob.glob(sys.argv[sys.argv.index('--fusion') + 1] + '/**/*.json', recursive=True): allf.update(json.load(open(f)))
        apply(allf); print('poses fusionnées', len(allf))
    else: run([a for a in sys.argv[1:] if not a.startswith('--')], '--tout' in sys.argv)
