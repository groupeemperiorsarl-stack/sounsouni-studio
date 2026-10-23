"""SOL DES DÉCORS (règle d'Issa, 23/10/2026) : personne ne flotte, personne n'est debout sur une voiture ou une table.
Un outil libre (SegFormer ADE20K, MIT/NVIDIA, processeur, sans clé) regarde chaque décor une seule fois et trouve la bande de SOL LIBRE
(cour, rue, terre, carrelage… sans voiture, table, banc ni mur). Résultat gardé dans studio/assets/catalog.json → "sol" :
{"VILLA_FETE": {"haut": 0.47, "bas": 0.71, "fiable": true}} (en part de la hauteur de l'image).
render.background s'en sert pour cadrer les plans larges : le bas de la bande tombe en bas de l'image, sa partie haute derrière les pieds
des personnages du fond. Utilisation : python studio/sol.py [DÉCOR …]  (sans nom : les décors pas encore mesurés)."""
import os, sys, json
import numpy as np
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
SOL = {'floor', 'road', 'ground', 'sidewalk', 'earth', 'grass', 'field', 'sand', 'path', 'dirt track', 'rug', 'carpet', 'land', 'stage', 'runway', 'bridge'}
OBST = {'car', 'truck', 'van', 'bus', 'minibike', 'bicycle', 'table', 'chair', 'bench', 'sofa', 'counter', 'desk', 'swivel chair', 'stool', 'wall', 'building',
        'fence', 'railing', 'pot', 'flowerpot', 'tree', 'plant', 'box', 'bed ', 'cabinet', 'stove', 'person', 'awning', 'booth', 'house', 'column', 'fountain'}
_M = {}
def modele():
    if not _M:
        from transformers import SegformerForSemanticSegmentation
        _M['m'] = SegformerForSemanticSegmentation.from_pretrained('nvidia/segformer-b2-finetuned-ade-512-512').eval()
    return _M['m']
def carte(im):
    import torch
    m = modele(); a = np.asarray(im.convert('RGB').resize((512, 512), Image.BILINEAR), dtype=np.float32) / 255   # préparation de l'image à la main (sans torchvision)
    a = (a - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]; x = torch.tensor(a.transpose(2, 0, 1)[None], dtype=torch.float32)
    with torch.no_grad(): lg = m(pixel_values=x).logits
    lg = torch.nn.functional.interpolate(lg, size=(96, 54), mode='bilinear', align_corners=False)   # carte 54 × 96 (format vertical)
    lab = lg.argmax(1)[0].numpy(); noms = m.config.id2label
    sol = np.isin(lab, [i for i, n in noms.items() if n.split(',')[0].strip() in SOL])
    obst = np.isin(lab, [i for i, n in noms.items() if n.split(',')[0].strip() in OBST])
    return sol, obst, lab
def mesurer(nom):
    im = Image.open(f'{A}/decors/{nom}.jpg').convert('RGB')
    w, h = im.size; r = 1080 / 1920   # partie centrale vue dans un plan large (format vertical)
    if w / h > r: cw = int(h * r); im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h))
    sol, obst, _ = carte(im)
    c = sol[:, 6:-6]; libre = c.mean(1)   # part de sol libre sur chaque rangée (sans les bords)
    ok = libre > 0.45
    # la plus grande bande continue de rangées « sol libre » (en partant du bas : c'est là que les gens marchent)
    best, cur = (0, 0), None
    for y in range(len(ok)):
        if ok[y]: cur = (cur[0], y + 1) if cur else (y, y + 1)
        else: cur = None
        if cur and cur[1] - cur[0] > best[1] - best[0]: best = cur
    H = len(ok); haut, bas = best[0] / H, best[1] / H
    return {'haut': round(haut, 3), 'bas': round(bas, 3), 'fiable': bool(bas - haut >= 0.12)}
def main():
    cat = json.load(open(f'{A}/catalog.json', encoding='utf-8')); S = cat.setdefault('sol', {})
    noms = sys.argv[1:] or [os.path.splitext(f)[0] for f in sorted(os.listdir(f'{A}/decors')) if f.endswith('.jpg') and os.path.splitext(f)[0] not in S]
    for n in noms:
        S[n] = mesurer(n); print(n, S[n])
    json.dump(cat, open(f'{A}/catalog.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if __name__ == '__main__': main()
