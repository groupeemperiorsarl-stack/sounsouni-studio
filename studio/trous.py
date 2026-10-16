"""Vêtements clairs « troués » au détourage : un débardeur blanc, un col clair… pris pour du fond, on voit le décor à travers
le personnage (ex. torse de Modibo). Règle : un trou entièrement entouré par le personnage, dont la couleur cachée est claire
et un peu colorée (tissu, pas le gris neutre du fond), est rebouché avec sa couleur d'origine.
Les vrais vides (entre les pieds du banc, sous le bras quand on y voit le fond gris) restent transparents.

python studio/trous.py           → répare toutes les poses du catalogue (sauf objets), dit lesquelles ont changé"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

def boucher(im, mini=300):
    """Renvoie (image réparée, nombre de pixels rebouchés)."""
    a = np.array(im.convert('RGBA')); solid = a[:, :, 3] > 200
    lab, n = ndimage.label(ndimage.binary_fill_holes(solid) & ~solid); fait = 0
    aire = solid.sum(); xs = np.nonzero(solid.any(0))[0]; larg = (xs.max() - xs.min() + 1) if len(xs) else 1
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab == i; s = int(m.sum())
        bh, bw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        # un vrai « trou de tissu » est grand et ramassé (torse) ; les anneaux d'oreille et l'espace étroit entre le bras et le corps restent vides
        if s < max(mini, 0.01 * aire) or bw < 0.08 * larg or s / (bh * bw) < 0.4: continue
        rgb = a[m][:, :3].astype(int); mu = rgb.mean(0)
        clair = (rgb.min(1) > 180).mean()
        if clair > 0.5 and mu.max() - mu.min() > 12:   # tissu clair (blanc cassé, crème), pas le gris neutre d'un fond
            a[m, 3] = 255; fait += s
    return Image.fromarray(a), fait

if __name__ == '__main__':
    cat = json.load(open(f'{A}/catalog.json'))
    for k, p in cat['poses'].items():
        if p['char'] == 'OBJET' or '@' in k: continue
        for suf in ('', '_o'):
            f = f'{A}/poses/{k}{suf}.webp'
            if not os.path.exists(f): continue
            im, n = boucher(Image.open(f))
            if n: im.save(f, quality=92, lossless=False); print(f'{k}{suf} : {n} pixels rebouchés')
