"""Mini-vidéos d'un personnage (faites par Issa avec un générateur gratuit, fond gris uni) → nouvelles poses du catalogue.

  tour   : le personnage tourne sur lui-même → 8 vues (face, trois-quarts, profil, dos…), la vue de dos remplace la silhouette floue.
  action : un geste de l'épisode → quelques images clés (début, milieu, fin du geste).

Étape 1 (planche à valider) :
    python -m studio.videos_ia video.mp4 --perso BAKARY --sorte tour -o sortie_videos
    → sortie_videos/<nom>/planche.png (images numérotées) + candidats.json
Étape 2 (réponse d'Issa, ex. « garder 1 3 5 » ou « tout ») :
    python -m studio.videos_ia --garder "1 3 5" -o sortie_videos/<nom>
    → poses détourées rangées dans assets/poses + catalogue (les bouches et l'orientation se calculent ensuite : automouth, autoyaw).
Tout est libre et local : ffmpeg + rembg (détourage). Rien n'est retouché à la main.
"""
import os, sys, json, re, argparse, subprocess, glob, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses_ia, director

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
VUES = [('face', 0), ('trois_quarts_1', 45), ('profil_1', 90), ('trois_quarts_dos_1', 135), ('dos', 180), ('trois_quarts_dos_2', 225), ('profil_2', 270), ('trois_quarts_2', 315)]
LIB = {'face': 'de face', 'trois_quarts_1': 'trois-quarts', 'profil_1': 'profil', 'trois_quarts_dos_1': 'trois-quarts de dos', 'dos': 'de dos',
       'trois_quarts_dos_2': 'trois-quarts de dos (autre côté)', 'profil_2': 'profil (autre côté)', 'trois_quarts_2': 'trois-quarts (autre côté)'}

def log(t): print(t, flush=True)

def images(video, dossier, fps=8):
    os.makedirs(dossier, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'fps={fps}', f'{dossier}/f_%04d.png'], check=True)
    return sorted(glob.glob(f'{dossier}/f_*.png'))

def masque(f, h=320):
    """Silhouette rapide (fond gris uni) : pixels qui s'écartent du gris du bord."""
    im = Image.open(f).convert('RGB'); im = im.resize((int(im.width * h / im.height), h))
    a = np.asarray(im).astype(int); bord = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]); fond = np.median(bord, 0)
    return (np.abs(a - fond).sum(2) > 40)

def iou(a, b): return (a & b).sum() / max(1, (a | b).sum())

def nettete(f):
    g = np.asarray(Image.open(f).convert('L')).astype(float)
    return float(np.var(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]))

def choisir_tour(fs):
    """Un tour complet : on cherche quand le personnage revient de face (silhouette la plus proche de la première image), puis 8 vues réparties."""
    M = [masque(f) for f in fs]; n = len(fs)
    debut = 0
    for i in range(1, n // 3):   # le personnage ne bouge pas encore : on prend la dernière image immobile comme départ
        if iou(M[i], M[0]) > 0.97: debut = i
        else: break
    fin = max(range(debut + n // 3, n), key=lambda i: iou(M[i], M[debut]) - 0.002 * (i - debut)) if n > 6 else n - 1
    if iou(M[fin], M[debut]) < 0.85: fin = n - 1   # pas de retour de face clair : on suppose un tour sur toute la vidéo
    out = []
    for nom, ang in VUES:
        c = debut + round((fin - debut) * ang / 360)
        c = max(range(max(0, c - 1), min(n, c + 2)), key=lambda i: nettete(fs[i]))   # la plus nette des images voisines
        out.append({'fichier': fs[c], 'vue': nom, 'angle': ang, 'temps': round(c / 8, 2)})
    return out

def choisir_action(fs, k=6):
    """Un geste : début, puis les images où le corps a le plus changé (sans doublons)."""
    M = [masque(f) for f in fs]; pris = [0]
    while len(pris) < k:
        i = max(range(len(fs)), key=lambda j: min(1 - iou(M[j], M[p]) for p in pris))
        if min(1 - iou(M[i], M[p]) for p in pris) < 0.04: break
        pris.append(i)
    return [{'fichier': fs[i], 'vue': f'geste_{n + 1}', 'angle': None, 'temps': round(i / 8, 2)} for n, i in enumerate(sorted(pris))]

def planche(cands, chemin, titre):
    w, h = 300, 560; cols = 4; rows = (len(cands) + cols - 1) // cols
    P = Image.new('RGB', (cols * w, rows * h + 50), 'white'); d = ImageDraw.Draw(P)
    try: fb = ImageFont.truetype(os.path.join(A, 'ui', 'Poppins-Bold.ttf'), 26); fm = ImageFont.truetype(os.path.join(A, 'ui', 'Poppins-Medium.ttf'), 18)
    except OSError: fb = fm = ImageFont.load_default()
    d.text((12, 10), titre, font=fb, fill=(20, 20, 20))
    for i, c in enumerate(cands):
        im = Image.open(c['detoure']).convert('RGBA'); im.thumbnail((w - 30, h - 80))
        x, y = (i % cols) * w, 50 + (i // cols) * h; fond = Image.new('RGBA', (w - 10, h - 10), (236, 240, 236, 255))
        fond.alpha_composite(im, ((w - 10 - im.width) // 2, h - 70 - im.height)); P.paste(fond.convert('RGB'), (x + 5, y + 5))
        d.text((x + 14, y + 12), str(i + 1), font=fb, fill=(200, 60, 20)); d.text((x + 14, y + h - 55), LIB.get(c['vue'], c['vue'].replace('_', ' ')), font=fm, fill=(30, 30, 30))
    P.save(chemin)

def preparer(video, perso, sorte, out, tags=''):
    nom = f"{perso.lower()}_{sorte}_{re.sub(r'[^0-9]', '', os.path.basename(video))[-6:] or 'v'}"
    d = os.path.join(out, nom); shutil.rmtree(d, ignore_errors=True); fs = images(video, os.path.join(d, 'images'))
    log(f'{len(fs)} images tirées de la vidéo')
    cands = choisir_tour(fs) if sorte == 'tour' else choisir_action(fs)
    for i, c in enumerate(cands):
        im = poses_ia.detourer(Image.open(c['fichier'])); c['detoure'] = os.path.join(d, f'candidat_{i + 1}.webp'); im.save(c['detoure'], quality=92)
        log(f"candidat {i + 1} : {LIB.get(c['vue'], c['vue'])} ({c['temps']} s)")
    json.dump({'perso': perso.upper(), 'sorte': sorte, 'tags': [t for t in tags.split(',') if t], 'candidats': cands}, open(os.path.join(d, 'candidats.json'), 'w'), ensure_ascii=False, indent=1)
    planche(cands, os.path.join(d, 'planche.png'), f"{perso.capitalize()} · {'tour complet' if sorte == 'tour' else 'geste'} — répondez « garder 1 3 5 » ou « tout »")
    log(f'planche : {os.path.join(d, "planche.png")}')
    return d

def garder(reponse, d):
    data = json.load(open(os.path.join(d, 'candidats.json'), encoding='utf-8')); cands = data['candidats']
    nums = range(1, len(cands) + 1) if re.search(r'tout', reponse, re.I) else [int(x) for x in re.findall(r'\d+', reponse)]
    cat = json.load(open(f'{A}/catalog.json')); c = data['perso']; pre = poses_ia.prefixe(c); faits = []
    for n in nums:
        x = cands[n - 1]; dos = x['vue'] in ('dos', 'trois_quarts_dos_1', 'trois_quarts_dos_2')
        base = f"{pre}_{'vue_' + x['vue'] if data['sorte'] == 'tour' else (data['tags'][0] if data['tags'] else 'geste') + '_' + str(n)}"
        k = base; i = 2
        while k in cat['poses']: k = f'{base}{i}'; i += 1
        im = Image.open(x['detoure']); im.save(f'{A}/poses/{k}.webp', quality=92)
        tags = (['dos'] if x['vue'] == 'dos' else ['dos', 'trois_quarts_dos'] if dos else ['neutre', 'ecoute', x['vue'].split('_')[0]]) if data['sorte'] == 'tour' else list(data['tags']) or ['geste']
        cat['poses'][k] = {'char': c, 'frame': 'pied', 'posture': 'dos' if x['vue'] == 'dos' else 'debout', 'tags': tags, 'mouth': False, 'size': list(im.size),
                           'head_x': poses_ia.tete_x(im), 'props': [t for t in tags if t in director.OBJ], 'genere': 'video', 'vue': x['vue']}
        if x['vue'] == 'dos' or dos: cat['poses'][k]['yaw_fixe'] = x['angle']
        faits.append(k); log(f'rangée : {k}')
    json.dump(cat, open(f'{A}/catalog.json', 'w'), ensure_ascii=False, indent=1); director.reload()
    return faits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video', nargs='?'); ap.add_argument('--perso'); ap.add_argument('--sorte', default='tour', choices=['tour', 'action'])
    ap.add_argument('--tags', default='', help='étiquettes des poses d\'un geste, ex. "telephone,lit,emerveille"'); ap.add_argument('--garder'); ap.add_argument('-o', '--out', default='sortie_videos')
    a = ap.parse_args()
    if a.garder: garder(a.garder, a.out); return
    preparer(a.video, a.perso, a.sorte, a.out, a.tags)
if __name__ == '__main__': main()
