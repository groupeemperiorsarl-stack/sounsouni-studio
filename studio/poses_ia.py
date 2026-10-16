"""Poses manquantes dessinées par l'application elle-même, sur une carte graphique gratuite (Kaggle), à choisir sur planche.
1. python -m studio.poses_ia -o sortie                       → liste des poses manquantes (vues de dos, poses assises), dessin sur Kaggle,
                                                                 planche A / B / C / D : sortie/planches/poses.html (+ planche_poses_N.png)
   options : --perso KARIM,DIASABI  --type dos,assis  --liste (montre seulement ce qui manque)
2. python -m studio.poses_ia -o sortie --choix "1B 2C"        → poses choisies détourées et rangées dans le catalogue
Jeton Kaggle : variable d'environnement KAGGLE_API_TOKEN (jamais écrit dans le dépôt). Aucun crédit Claude n'est utilisé.
Modèle : Qwen-Image-Edit-2509 (Apache 2.0, usage commercial permis), version allégée GGUF + Lightning (studio/kaggle/poses_worker.py)."""
import os, sys, io, re, json, time, base64, argparse, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import director, planches, gfx
A = director.A; HERE = os.path.dirname(os.path.abspath(__file__))
COMPTE = os.environ.get('KAGGLE_USERNAME', 'emperormedia'); NOYAU = os.environ.get('STUDIO_KAGGLE_NOYAU', 'sounsouni-poses')
FEMMES = {'AWA', 'MIMI', 'KADI', 'SALI', 'FATIM', 'VENDEUSE'}
STYLE = 'Keep the identical {face}outfit, colors, body proportions and 3D cartoon style. Plain flat light gray background, nothing else in the picture.'
TYPES = {
    'dos': ('Vue de dos', "Turn this cartoon character around: show the exact same {who} seen from behind, back view, full body from head to feet, "
            "standing upright with arms relaxed at the sides. "),
    'assis': ('Assis', "Show the exact same {who} sitting on a simple low wooden bench, full body from head to feet, three-quarter view, "
              "hands resting on the knees, calm neutral expression, mouth closed. "),
}
GRAINES = (1, 2, 3, 4)

def poses_de(char): return {k: p for k, p in director.POSES.items() if p['char'] == char and '@' not in k}
def prefixe(char):
    ks = [k.split('_')[0] for k in poses_de(char)]
    return max(set(ks), key=ks.count) if ks else char.lower()[:3]
def manquantes(persos=None, types=('dos', 'assis')):
    """Ce qui manque à chaque personnage : vue de dos (sans objet), pose assise en pied."""
    out = []
    for c in sorted({p['char'] for p in director.POSES.values() if p['char'] != 'OBJET' and '+' not in p['char']}):
        if persos and c not in persos: continue
        ps = poses_de(c).values()
        if 'dos' in types and not any(p['posture'] == 'dos' and 'cycle' not in ' '.join(p['tags']) for p in ps): out.append((c, 'dos'))
        if 'assis' in types and not any(p['posture'] in ('assis', 'banc') and p['frame'] == 'pied' for p in ps): out.append((c, 'assis'))
    return out
def reference(char):
    """La pose de départ : debout, en pied, calme, sans objet, bras le long du corps (silhouette étroite)."""
    best, bs = None, -1e9
    for k, p in poses_de(char).items():
        if p['posture'] != 'debout' or p['frame'] != 'pied': continue
        t = set(p['tags']); w, h = p['size']; objets = set(p.get('props', [])) | (t & director.OBJ)
        sc = 3 * len(t & {'neutre', 'ecoute', 'serieux'}) - 2 * len(t & director.GESTE) - len(t & (director.POS | director.NEG)) - 6 * w / h - 20 * len(objets)
        if sc > bs: best, bs = k, sc
    return best or director.pick(char, ['neutre'], 'pied', 'debout', need_mouth=False, calm=True)
def ref_image(k):
    im = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); s = 1024 / im.height; im = im.resize((max(1, int(im.width * s)), 1024), Image.LANCZOS)
    W = max(im.width + 160, 600); bg = Image.new('RGBA', (W, 1124), (222, 222, 222, 255)); bg.alpha_composite(im, ((W - im.width) // 2, 50))
    b = io.BytesIO(); bg.convert('RGB').save(b, 'JPEG', quality=92); return base64.b64encode(b.getvalue()).decode()
def taches(liste, graines=GRAINES):
    out = []
    for c, t in liste:
        k = reference(c)
        if not k: continue
        who = 'woman' if c in FEMMES else 'man'
        out.append({'nom': f'{c}__{t}', 'perso': c, 'type': t, 'ref': k, 'refs': [ref_image(k)], 'seeds': list(graines),
                    'prompt': TYPES[t][1].format(who=who) + STYLE.format(face='' if t == 'dos' else 'face, ')})
    return out

# ---------------- Kaggle ----------------
def kaggle(*args, timeout=600):
    r = subprocess.run(['kaggle', *args], capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()
def lancer(tch, travail, log=print, attente=5400):
    """Envoie le travail à Kaggle, attend la fin (sans rien consommer ici), récupère les images."""
    if not os.environ.get('KAGGLE_API_TOKEN'): raise SystemExit('jeton Kaggle absent : variable KAGGLE_API_TOKEN')
    d = os.path.join(travail, 'kaggle'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    job = {'taches': [{k: t[k] for k in ('nom', 'refs', 'prompt', 'seeds')} for t in tch], 'quants': ['Q4_0', 'Q3_K_M'], 'lightning': True}
    code = open(os.path.join(HERE, 'kaggle', 'poses_worker.py')).read().replace('__JOB__', base64.b64encode(json.dumps(job).encode()).decode())
    open(os.path.join(d, 'poses.py'), 'w').write(code)
    json.dump({'id': f'{COMPTE}/{NOYAU}', 'title': NOYAU, 'code_file': 'poses.py', 'language': 'python', 'kernel_type': 'script', 'is_private': True,
               'enable_gpu': True, 'enable_tpu': False, 'enable_internet': True, 'dataset_sources': [], 'kernel_sources': [], 'competition_sources': [],
               'model_sources': [], 'machine_shape': 'NvidiaTeslaT4'}, open(os.path.join(d, 'kernel-metadata.json'), 'w'))
    log(f'Kaggle : envoi de {len(tch)} pose(s) × {len(tch[0]["seeds"])} propositions'); log('  ' + kaggle('kernels', 'push', '-p', d).splitlines()[-1])
    t0 = time.time(); st = ''
    while time.time() - t0 < attente:
        time.sleep(60); st = kaggle('kernels', 'status', f'{COMPTE}/{NOYAU}')
        if re.search(r'complete|error|cancel', st, re.I): break
    log(f'Kaggle : {st.split(" has status ")[-1]} après {int((time.time() - t0) / 60)} min')
    out = os.path.join(travail, 'resultats'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    kaggle('kernels', 'output', f'{COMPTE}/{NOYAU}', '-p', out, timeout=1200)
    j = os.path.join(out, 'journal.json'); jr = json.load(open(j)) if os.path.exists(j) else {'images': [], 'erreurs': ['pas de journal']}
    for e in jr.get('erreurs', [])[:3]: log('  erreur Kaggle : ' + e.strip().splitlines()[-1][:200])
    return out, jr

# ---------------- planche et rangement ----------------
def carre(im, fond=(222, 222, 222)):
    """Image dessinée posée sur un fond 1080×1920 (format des planches)."""
    c = Image.new('RGB', (1080, 1920), fond); s = min(1080 / im.width, 1920 / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    c.paste(im, ((1080 - im.width) // 2, (1920 - im.height) // 2)); return c
def planche(tch, res, jr, out, log=print):
    ok = {i['fichier'] for i in jr.get('images', []) if not i.get('ratee')}
    qs, imgs, tit = [], {}, {}
    for t in tch:
        opts = [f"{t['nom']}__{g}.png" for g in t['seeds'] if f"{t['nom']}__{g}.png" in ok][:len(planches.LETTRES)]
        if not opts: log(f"  {t['nom']} : aucune image réussie"); continue
        n = len(qs) + 1; q = {'n': n, 'perso': t['perso'], 'type': t['type'], 'ref': t['ref'], 'options': []}
        for f, l in zip(opts, planches.LETTRES):
            q['options'].append({'lettre': l, 'fichier': os.path.join(res, f), 'texte': f'proposition {l}'}); imgs[(n, l)] = carre(Image.open(os.path.join(res, f)).convert('RGB'))
        tit[n] = (f"Question {n} · {gfx.nom(t['perso'])}", f"{TYPES[t['type']][0]} : laquelle garder ?", f"dessinée à partir de la pose « {t['ref']} »")
        qs.append(q)
    d = os.path.join(out, 'planches'); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith('planche_poses_') or f in ('poses.html', 'poses.json'): os.remove(os.path.join(d, f))
    if not qs: return []
    json.dump({'questions': qs}, open(os.path.join(d, 'poses.json'), 'w'), ensure_ascii=False, indent=1)
    planches.pages(qs, tit, imgs, d, prefixe='planche_poses_')
    planches.page_html(qs, tit, imgs, os.path.join(d, 'poses.html'), 'nouvelles poses', "Une question sans réponse = aucune de ces images n'est gardée.")
    log(f'planche : {len(qs)} question(s) → planches/poses.html'); return qs
def detourer(im):
    """Fond enlevé (rembg, modèle libre), on garde le personnage seul, recadré, hauteur 1600 comme les autres poses."""
    from rembg import remove, new_session
    from scipy import ndimage
    m = np.asarray(remove(im.convert('RGB'), session=new_session('isnet-general-use'), only_mask=True, post_process_mask=True))
    lab, n = ndimage.label(m > 60)
    if n > 1:
        sz = ndimage.sum(np.ones_like(m), lab, range(1, n + 1)); m = np.where(ndimage.binary_dilation(lab == np.argmax(sz) + 1, iterations=3), m, 0)
    o = im.convert('RGBA'); o.putalpha(Image.fromarray(m.astype(np.uint8))); o = o.crop(o.getbbox())
    return o.resize((max(1, int(o.width * 1600 / o.height)), 1600), Image.LANCZOS)
def tete_x(im):
    a = np.asarray(im)[:, :, 3]; top = a[: int(a.shape[0] * 0.12)] > 128; xs = np.nonzero(top.any(0))[0]
    return round(float((xs.min() + xs.max()) / 2 / a.shape[1]), 3) if len(xs) else 0.5
def ranger(reponse, out, log=print):
    """« 1B 2C » → la pose B de la question 1, la C de la question 2 rejoignent le catalogue (nouvelle analyse des objets au prochain épisode)."""
    data = json.load(open(os.path.join(out, 'planches', 'poses.json'), encoding='utf-8')); qs = {q['n']: q for q in data['questions']}
    cat = json.load(open(f'{A}/catalog.json')); faits = []
    for n, l in re.findall(r'(\d+)\s*[:=]?\s*([A-Da-d])\b', reponse or ''):
        q = qs.get(int(n)); o = next((o for o in (q or {}).get('options', []) if o['lettre'] == l.upper()), None)
        if not o: log(f'question {n} lettre {l} inconnue, ignorée'); continue
        im = detourer(Image.open(o['fichier']))
        base = f"{prefixe(q['perso'])}_{q['type']}_ia"; k = base; i = 2
        while k in cat['poses']: k = f'{base}{i}'; i += 1
        im.save(f'{A}/poses/{k}.webp', quality=92)
        dos = q['type'] == 'dos'
        cat['poses'][k] = {'char': q['perso'], 'frame': 'pied', 'posture': 'dos' if dos else 'assis', 'tags': ['dos'] if dos else ['neutre', 'ecoute', 'assis'],
                           'mouth': False, 'size': list(im.size), 'head_x': tete_x(im), 'props': [], 'genere': 'qwen-image-edit-2509', 'depart': q['ref']}
        faits.append(k); log(f"rangée : {k} ({gfx.nom(q['perso'])}, {TYPES[q['type']][0].lower()})")
    json.dump(cat, open(f'{A}/catalog.json', 'w'), ensure_ascii=False, indent=1); director.reload()
    return faits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('-o', '--out', default='sortie_poses')
    ap.add_argument('--perso', default=None, help='ex. KARIM,DIASABI'); ap.add_argument('--type', default='dos,assis')
    ap.add_argument('--liste', action='store_true', help='montre seulement ce qui manque'); ap.add_argument('--choix', default=None, help='ex. "1B 2C"')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.choix: ranger(a.choix, a.out); return
    persos = {x.strip().upper() for x in a.perso.split(',')} if a.perso else None
    lst = manquantes(persos, tuple(a.type.split(',')))
    print('poses manquantes : ' + (', '.join(f'{gfx.nom(c)} ({TYPES[t][0].lower()})' for c, t in lst) or 'aucune'))
    if a.liste or not lst: return
    tch = taches(lst); res, jr = lancer(tch, os.path.join(a.out, 'travail_poses')); planche(tch, res, jr, a.out)
if __name__ == '__main__': main()
