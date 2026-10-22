"""Mini-vidéos d'un personnage (faites par Issa avec un générateur gratuit, fond gris uni) → nouvelles poses du catalogue.

  tour   : le personnage tourne sur lui-même → 16 vues tout autour (face, trois-quarts, profil, dos…).
  action : un geste de l'épisode → toutes les images différentes du geste (jusqu'à 16).
Demandé par Issa : garder TOUTES les images utiles, chacune décrite (vue, sens du regard, émotion, geste, objets) pour que
la mise en scène retrouve la bonne au bon moment. La description est faite par Gemini (clé GEMINI_API_KEY) qui regarde les images ;
sans clé, l'application met des étiquettes simples (vue d'après l'angle du tour).
Chaque image garde aussi sa place dans la vidéo (« sequence ») : on pourra rejouer les mouvements image par image.

Étape 1 (planche) :  python -m studio.videos_ia video.mp4 --perso BAKARY --sorte tour -o sortie_videos
Étape 2 (rangement) : python -m studio.videos_ia --garder tout -o sortie_videos/<nom>     (ou « garder 1 3 5 »)
Libre et local : ffmpeg + rembg (détourage). Rien n'est retouché à la main.
"""
import os, sys, json, re, argparse, subprocess, glob, shutil, base64, io, time, urllib.request, ssl
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses_ia, director

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
FPS = 8

def log(t): print(t, flush=True)

def images(video, dossier):
    os.makedirs(dossier, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'fps={FPS}', f'{dossier}/f_%04d.png'], check=True)
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

def choisir_tour(fs, n_vues=16):
    """Un tour complet : on cherche quand le personnage revient de face, puis n_vues réparties tout autour."""
    M = [masque(f) for f in fs]; n = len(fs); debut = 0
    for i in range(1, n // 3):   # il ne bouge pas encore : départ = dernière image immobile
        if iou(M[i], M[0]) > 0.97: debut = i
        else: break
    fin = max(range(debut + n // 3, n), key=lambda i: iou(M[i], M[debut]) - 0.002 * (i - debut)) if n > 6 else n - 1
    if iou(M[fin], M[debut]) < 0.85: fin = n - 1
    out = []
    for k in range(n_vues):
        ang = round(360 * k / n_vues); c = debut + round((fin - debut) * k / n_vues)
        c = max(range(max(0, c - 1), min(n, c + 2)), key=lambda i: nettete(fs[i]))
        out.append({'fichier': fs[c], 'vue': f'angle_{ang:03d}', 'angle': ang, 'temps': round(c / FPS, 2), 'ordre': k})
    return out

def choisir_action(fs, k=16, seuil=0.02):
    """Un geste : toutes les images vraiment différentes (le corps a bougé), dans l'ordre de la vidéo."""
    M = [masque(f) for f in fs]; pris = [0]
    while len(pris) < k:
        i = max(range(len(fs)), key=lambda j: min(1 - iou(M[j], M[p]) for p in pris))
        if min(1 - iou(M[i], M[p]) for p in pris) < seuil: break
        pris.append(i)
    pris = sorted(pris)
    return [{'fichier': fs[i], 'vue': f'geste_{n + 1:02d}', 'angle': None, 'temps': round(i / FPS, 2), 'ordre': n} for n, i in enumerate(pris)]

# ---------- description de chaque image (Gemini regarde ; vocabulaire de l'application) ----------
def _gemini(parts, cle):
    ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None) if os.environ.get('SSL_CERT_FILE') else None
    noms = ['models/gemini-3-flash-preview', 'models/gemini-3.8-flash', 'models/gemini-flash-latest', 'models/gemini-3.5-flash']
    for tour in range(6):
        for m in noms:
            q = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/' + m + ':generateContent', method='POST',
                headers={'x-goog-api-key': cle, 'Content-Type': 'application/json'},
                data=json.dumps({'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'temperature': 0.1, 'responseMimeType': 'application/json'}}).encode())
            try:
                r = json.load(urllib.request.urlopen(q, timeout=240, context=ctx))
                t = ''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts'])
                return json.loads(t)
            except Exception as e: log(f'Gemini ({m}) : {str(e)[:80]}')
        time.sleep(20)
    return None

def decrire(cands, perso):
    """Étiquettes de chaque image. Gemini si la clé existe ; sinon d'après l'angle du tour."""
    for c in cands:   # étiquettes simples (toujours) : vue d'après l'angle
        a = c['angle']
        if a is None: c.update(vue_type='face', regard='face', emotion='neutre', gestes=[], objets=[], description='')
        else:
            d = min(a, 360 - a); c['vue_type'] = 'face' if d < 23 else 'trois_quarts' if d < 68 else 'profil' if d < 113 else 'trois_quarts_dos' if d < 158 else 'dos'
            c.update(regard='face' if c['vue_type'] in ('face', 'dos') else ('gauche' if a < 180 else 'droite'), emotion='neutre', gestes=[], objets=[], description='')
    cle = os.environ.get('GEMINI_API_KEY')
    if not cle: log('pas de clé Gemini : étiquettes simples seulement'); return cands
    parts = [{'text': (f"Voici {len(cands)} images numérotées du personnage {perso} (dessin animé 3D, fond uni), tirées d'une vidéo. Pour CHAQUE image, décris ce que tu VOIS, "
              "en choisissant seulement dans ces listes.\nvue : face, trois_quarts, profil, trois_quarts_dos, dos.\n"
              "regard : face, gauche, droite (vers quel côté DE L'IMAGE le visage est tourné ; dos = face).\n"
              f"emotion (une seule) : {', '.join(sorted(director.EMOS))}.\n"
              f"gestes (zéro ou plusieurs) : {', '.join(sorted(director.GESTE | director.BODY | {'main_joue', 'main_bouche', 'lit', 'bras_croises', 'mains_hanches', 'marche', 'court', 'assis'}))}.\n"
              f"objets visibles (zéro ou plusieurs) : {', '.join(sorted(director.OBJ))}.\n"
              "Réponds en JSON : [{\"n\": 1, \"vue\": \"…\", \"regard\": \"…\", \"emotion\": \"…\", \"gestes\": [], \"objets\": [], \"nette\": true, \"description\": \"une courte phrase en français\"}, …]. "
              "« nette » = false si l'image est floue, déformée (mains, visage) ou si le personnage ne ressemble plus à lui-même.")}]
    for i, c in enumerate(cands):
        im = Image.open(c['detoure']).convert('RGBA'); im.thumbnail((360, 640)); b = Image.new('RGB', im.size, (236, 236, 236)); b.paste(im, (0, 0), im)
        buf = io.BytesIO(); b.save(buf, 'JPEG', quality=85); parts += [{'text': f'Image {i + 1} :'}, {'inline_data': {'mime_type': 'image/jpeg', 'data': base64.b64encode(buf.getvalue()).decode()}}]
    r = _gemini(parts, cle)
    if not isinstance(r, list): log('Gemini indisponible : étiquettes simples seulement'); return cands
    for x in r:
        try: c = cands[int(x['n']) - 1]
        except (KeyError, ValueError, IndexError, TypeError): continue
        if x.get('vue') in ('face', 'trois_quarts', 'profil', 'trois_quarts_dos', 'dos'): c['vue_type'] = x['vue']
        if x.get('regard') in ('face', 'gauche', 'droite'): c['regard'] = x['regard']
        if x.get('emotion') in director.EMOS: c['emotion'] = x['emotion']
        c['gestes'] = [g for g in x.get('gestes', []) if isinstance(g, str)][:4]; c['objets'] = [o for o in x.get('objets', []) if o in director.OBJ]
        c['nette'] = bool(x.get('nette', True)); c['description'] = str(x.get('description', ''))[:120]
    log('images décrites par Gemini')
    return cands

def planche(cands, chemin, titre):
    w, h = 300, 600; cols = 4; rows = (len(cands) + cols - 1) // cols
    P = Image.new('RGB', (cols * w, rows * h + 50), 'white'); d = ImageDraw.Draw(P)
    try: fb = ImageFont.truetype(os.path.join(A, 'ui', 'Poppins-Bold.ttf'), 26); fm = ImageFont.truetype(os.path.join(A, 'ui', 'Poppins-Medium.ttf'), 15)
    except OSError: fb = fm = ImageFont.load_default()
    d.text((12, 10), titre, font=fb, fill=(20, 20, 20))
    for i, c in enumerate(cands):
        im = Image.open(c['detoure']).convert('RGBA'); im.thumbnail((w - 30, h - 120))
        x, y = (i % cols) * w, 50 + (i // cols) * h; fond = Image.new('RGBA', (w - 10, h - 10), (236, 240, 236, 255) if c.get('nette', True) else (250, 225, 225, 255))
        fond.alpha_composite(im, ((w - 10 - im.width) // 2, h - 110 - im.height)); P.paste(fond.convert('RGB'), (x + 5, y + 5))
        d.text((x + 14, y + 12), str(i + 1), font=fb, fill=(200, 60, 20))
        lig = [c['vue_type'].replace('_', ' ') + (' · regarde ' + c['regard'] if c['regard'] != 'face' else '') + ' · ' + c['emotion'].replace('_', ' '),
               ', '.join(c['gestes'] + c['objets'])[:40] or ' ', '' if c.get('nette', True) else '(floue ou déformée)']
        for k, l in enumerate(lig): d.text((x + 14, y + h - 95 + k * 22), l, font=fm, fill=(30, 30, 30))
    P.save(chemin)

def preparer(video, perso, sorte, out, tags=''):
    nom = f"{perso.lower()}_{sorte}_{re.sub(r'[^0-9]', '', os.path.basename(video))[-6:] or 'v'}"
    d = os.path.join(out, nom); shutil.rmtree(d, ignore_errors=True); fs = images(video, os.path.join(d, 'images'))
    log(f'{len(fs)} images tirées de la vidéo')
    cands = choisir_tour(fs) if sorte == 'tour' else choisir_action(fs)
    for i, c in enumerate(cands):
        im = poses_ia.detourer(Image.open(c['fichier'])); c['detoure'] = os.path.join(d, f'candidat_{i + 1:02d}.webp'); im.save(c['detoure'], quality=92)
    log(f'{len(cands)} images détourées')
    decrire(cands, perso.upper())
    for c in cands: c['fichier'] = os.path.basename(c['fichier']); c['detoure'] = os.path.basename(c['detoure'])
    json.dump({'perso': perso.upper(), 'sorte': sorte, 'video': nom, 'tags': [t for t in tags.split(',') if t], 'candidats': cands},
              open(os.path.join(d, 'candidats.json'), 'w'), ensure_ascii=False, indent=1)
    for c in cands: c['detoure'] = os.path.join(d, c['detoure'])
    planche(cands, os.path.join(d, 'planche.png'), f"{perso.capitalize()} · {'tour complet' if sorte == 'tour' else 'geste'} · {len(cands)} images — « garder tout » ou « garder 1 3 5 »")
    shutil.rmtree(os.path.join(d, 'images'), ignore_errors=True)
    log(f'planche : {os.path.join(d, "planche.png")}')
    return d

YAW = {'face': 0, 'trois_quarts': 32, 'profil': 75}   # orientation approximative ; autoyaw la mesure ensuite quand le visage est visible

def garder(reponse, d):
    data = json.load(open(os.path.join(d, 'candidats.json'), encoding='utf-8')); cands = data['candidats']
    nums = [i + 1 for i, c in enumerate(cands) if c.get('nette', True)] if re.search(r'tout', reponse, re.I) else [int(x) for x in re.findall(r'\d+', reponse)]
    cat = json.load(open(f'{A}/catalog.json')); c0 = data['perso']; pre = poses_ia.prefixe(c0); faits = []
    for n in nums:
        x = cands[n - 1]; vt = x.get('vue_type', 'face')
        base = f"{pre}_v_{data['sorte']}_{data['video'].split('_')[-1]}_{n:02d}"; k = base; i = 2
        while k in cat['poses']: k = f'{base}_{i}'; i += 1
        im = Image.open(os.path.join(d, x['detoure'])); im.save(f'{A}/poses/{k}.webp', quality=92)
        tags = (['dos'] if vt == 'dos' else ['dos', 'trois_quarts_dos'] if vt == 'trois_quarts_dos' else
                [x.get('emotion', 'neutre')] + x.get('gestes', []) + x.get('objets', []) + list(data.get('tags', [])) + ([vt] if vt != 'face' else []) + (['ecoute'] if x.get('emotion') == 'neutre' and not x.get('gestes') else []))
        tags = list(dict.fromkeys(t for t in tags if t))
        p = {'char': c0, 'frame': 'pied', 'posture': 'dos' if vt == 'dos' else ('assis' if 'assis' in tags else 'debout'), 'tags': tags, 'mouth': False, 'size': list(im.size),
             'head_x': poses_ia.tete_x(im), 'props': [t for t in tags if t in director.OBJ], 'genere': 'video', 'vue': vt,
             'sequence': {'video': data['video'], 'ordre': x.get('ordre', n - 1), 'temps': x.get('temps')}, 'description': x.get('description', '')}
        if vt in YAW: p['yaw'] = YAW[vt] * (1 if x.get('regard') == 'gauche' else -1 if x.get('regard') == 'droite' else 0)   # yaw > 0 : visage vers la gauche de l'image
        cat['poses'][k] = p; faits.append(k); log(f"rangée : {k} ({vt}, {', '.join(tags)})")
    json.dump(cat, open(f'{A}/catalog.json', 'w'), ensure_ascii=False, indent=1); director.reload()
    return faits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video', nargs='?'); ap.add_argument('--perso'); ap.add_argument('--sorte', default='tour', choices=['tour', 'action'])
    ap.add_argument('--tags', default='', help='étiquettes ajoutées à toutes les images d\'un geste, ex. "telephone"'); ap.add_argument('--garder'); ap.add_argument('-o', '--out', default='sortie_videos')
    a = ap.parse_args()
    if a.garder: print('NOUVELLES_POSES=' + ','.join(garder(a.garder, a.out))); return
    preparer(a.video, a.perso, a.sorte, a.out, a.tags)
if __name__ == '__main__': main()
