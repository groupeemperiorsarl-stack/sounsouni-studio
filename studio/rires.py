"""Rires des personnages : de vrais rires (Chatterbox Turbo, MIT) avec la voix de chaque personnage, différents selon le type
(homme, homme d'âge mûr, femme, demoiselle, enfant / adolescent) et selon la sorte de rire (éclat de rire, petit rire retenu).
Les rires choisis par Issa à l'oreille sont gardés dans assets/rires/ : ils resservent à chaque épisode (pas de nouveau calcul).

1. python -m studio.rires -o sortie_rires [--perso BAKARY,AWA]   → candidats A / B / C / D, page d'écoute sortie_rires/rires.html
2. python -m studio.rires -o sortie_rires --choix "1B 2A …"      → rires choisis rangés dans assets/rires/<PERSO>_<sorte>.wav
Un personnage sans rire choisi (nouveau personnage) reçoit automatiquement le premier rire de son type."""
import os, sys, io, re, json, base64, html, argparse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); R = os.path.join(A, 'rires')
TYPES = {'homme': 'homme', 'homme_mur': "homme d'âge mûr", 'femme': 'femme', 'demoiselle': 'demoiselle', 'enfant': 'enfant / adolescent'}
# type de chaque personnage (le catalogue peut le changer : clé "age")
AGE = {'BAKARY': 'homme', 'MODIBO': 'homme', 'DIASABI': 'homme', 'KARIM': 'homme', 'SEYDOU': 'homme', 'MOUSSA': 'homme',
       'AWA': 'demoiselle', 'SALI': 'demoiselle', 'MIMI': 'demoiselle', 'FATIM': 'femme', 'KADI': 'femme', 'VENDEUSE': 'femme'}
SORTES = {'eclat': 'éclat de rire', 'petit': 'petit rire retenu'}
DUREE = {'eclat': 2.6, 'petit': 1.3}
# (texte donné à Turbo, expressivité) : 4 propositions par type et par sorte
STYLES = {
    'homme': {'eclat': [('Ha ha ha ha! [laugh]', 0.6), ('[laugh] [laugh]', 0.7), ('Ha ha! [laugh] ha ha!', 0.55), ('[happy] Ha ha ha! [laugh]', 0.6)],
              'petit': [('[chuckle]', 0.4), ('Hm hm [chuckle]', 0.4), ('Heh heh [chuckle]', 0.45), ('[sarcastic] [chuckle]', 0.45)]},
    'homme_mur': {'eclat': [('Ho ho ho! [laugh]', 0.5), ('Heh heh heh [laugh]', 0.45), ('[laugh] ho ho ho', 0.5), ('Hoo ho ho ho! [laugh]', 0.55)],
                  'petit': [('Hm hm hm [chuckle]', 0.35), ('[chuckle]', 0.35), ('Heh heh [chuckle]', 0.4), ('Ho ho [chuckle]', 0.4)]},
    'femme': {'eclat': [('Ha ha ha! [laugh]', 0.6), ('[laugh] [laugh]', 0.7), ('Hi hi hi ha ha! [laugh]', 0.6), ('[happy] Ha ha! [laugh]', 0.6)],
              'petit': [('[chuckle]', 0.4), ('Hm hm [chuckle]', 0.4), ('Hi hi [chuckle]', 0.45), ('[sarcastic] [chuckle]', 0.45)]},
    'demoiselle': {'eclat': [('Hi hi hi hi! [laugh]', 0.65), ('[laugh] hi hi!', 0.6), ('Hi hi! [chuckle] hi hi hi!', 0.6), ('[happy] [laugh]', 0.7)],
                   'petit': [('Hi hi [chuckle]', 0.45), ('[chuckle]', 0.4), ('Hi hi hi', 0.45), ('[sarcastic] hi hi', 0.45)]},
    'enfant': {'eclat': [('Hi hi hi hi hi! [laugh]', 0.8), ('Ha ha ha ha ha! [laugh]', 0.8), ('[happy] [laugh] [laugh]', 0.8), ('Hé hé hé hé! [laugh]', 0.75)],
               'petit': [('Hi hi hi [chuckle]', 0.55), ('[chuckle]', 0.5), ('Hé hé [chuckle]', 0.55), ('Hi hi', 0.5)]},
}
def catalogue(): return json.load(open(f'{A}/catalog.json'))
def age(c, cat=None): return (cat or catalogue()).get('age', {}).get(c) or AGE.get(c, 'homme')
def voix(c, cat=None):
    """Voix de référence du personnage ; Turbo en veut plus de 5 s : une voix trop courte est répétée (copie de travail)."""
    f = f"{A}/voix/" + (cat or catalogue())['voices'].get(c, 'ref_bakary.wav')
    y, sr = sf.read(f); y = y if y.ndim == 1 else y.mean(1)
    if len(y) / sr >= 5.5: return f
    out = os.path.join('/tmp', 'rires_ref_' + os.path.basename(f)); pause = np.zeros(int(0.3 * sr))
    while len(y) / sr < 6: y = np.concatenate([y, pause, y[:int(len(y))]]) if len(y) < 3 * sr else np.concatenate([y, pause, y])
    sf.write(out, y, sr); return out
def fichier(c, sorte='eclat'): return os.path.join(R, f'{c}_{sorte}.wav')

def nettoyer(src, dst, sorte):
    """Garde le rire seul : silences coupés, longueur limitée, fin adoucie, volume réglé."""
    import librosa
    y, sr = sf.read(src); y = y if y.ndim == 1 else y.mean(1); y = y.astype(np.float32)
    yt, (a, b) = librosa.effects.trim(y, top_db=35); y = y[max(0, a - int(0.03 * sr)): b + int(0.08 * sr)]
    y = y[:int(DUREE[sorte] * sr)]; f = np.linspace(1, 0, min(len(y), int(0.25 * sr))); y[-len(f):] *= f
    sf.write(dst, y / (np.abs(y).max() + 1e-6) * 0.9, sr, subtype='PCM_16'); return dst
def generer(jobs, work):
    import voices
    voices.gen(jobs, work)

def candidats(persos, out, log=print):
    """4 propositions par personnage et par sorte de rire, puis la page d'écoute."""
    cat = catalogue(); d = os.path.join(out, 'candidats'); os.makedirs(d, exist_ok=True); qs = []; jobs = []
    for c in persos:
        for so in SORTES:
            q = {'n': len(qs) + 1, 'perso': c, 'sorte': so, 'type': age(c, cat), 'options': []}
            for (txt, ex), l in zip(STYLES[q['type']][so], 'ABCD'):
                raw = os.path.join(d, f'{c}_{so}_{l}_brut.wav'); fin = os.path.join(d, f'{c}_{so}_{l}.wav')
                if not os.path.exists(raw): jobs.append({'out': raw, 'ref': voix(c, cat), 'text': txt, 'exag': ex, 'turbo': True})
                q['options'].append({'lettre': l, 'fichier': fin, 'brut': raw, 'texte': txt})
            qs.append(q)
    log(f'rires : {len(jobs)} propositions à fabriquer'); generer(jobs, d)
    for q in qs:
        for o in q['options']:
            if os.path.exists(o['brut']): nettoyer(o['brut'], o['fichier'], q['sorte'])
    json.dump({'questions': qs}, open(os.path.join(out, 'rires.json'), 'w'), ensure_ascii=False, indent=1)
    page(qs, os.path.join(out, 'rires.html')); log(f'page d\'écoute : {len(qs)} questions → rires.html'); return qs
def mp3(f):
    r = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', f, '-ac', '1', '-b:a', '64k', '-f', 'mp3', '-'], capture_output=True)
    return base64.b64encode(r.stdout).decode()
def page(qs, path):
    import gfx
    cartes = []
    for q in qs:
        if not any(os.path.exists(o['fichier']) for o in q['options']): continue
        opts = ''.join(f'<button class="opt" data-q="{q["n"]}" data-l="{o["lettre"]}"><span class="l">{o["lettre"]}</span>'
                       f'<audio controls preload="none" src="data:audio/mpeg;base64,{mp3(o["fichier"])}"></audio></button>' for o in q['options'] if os.path.exists(o['fichier']))
        cartes.append(f'<section><h2>{q["n"]}. {html.escape(gfx.nom(q["perso"]))} — {SORTES[q["sorte"]]}</h2><p class="t">type : {TYPES[q["type"]]}</p>{opts}</section>')
    open(path, 'w', encoding='utf-8').write(f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rires à choisir</title><style>
:root{{--fond:#f6f3ee;--carte:#fff;--texte:#222;--doux:#666;--accent:#e8731a;--bord:#ddd}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}}}
:root[data-theme="dark"]{{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fond);color:var(--texte);font:16px/1.4 system-ui,sans-serif;padding:12px 12px 100px;overflow-x:hidden}}
h1{{font-size:20px;margin:4px 0}}.aide{{color:var(--doux);font-size:14px;margin:0 0 12px}}
section{{background:var(--carte);border:1px solid var(--bord);border-radius:12px;padding:10px;margin:0 0 12px}}h2{{font-size:16px;margin:0}}.t{{margin:0 0 6px;color:var(--doux);font-size:13px}}
.opt{{display:flex;align-items:center;gap:8px;width:100%;border:3px solid transparent;border-radius:10px;background:none;padding:4px;margin:2px 0;color:inherit}}
.opt.on{{border-color:var(--accent)}}.l{{flex:none;width:34px;height:34px;border-radius:50%;background:var(--accent);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center}}
audio{{flex:1;min-width:0;height:36px}}
.barre{{position:fixed;left:0;right:0;bottom:0;background:var(--carte);border-top:1px solid var(--bord);padding:10px 12px;display:flex;gap:8px;align-items:center}}
.barre code{{flex:1;min-width:0;font-size:16px;font-weight:700;overflow-wrap:anywhere}}.barre button{{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-weight:700;flex:none}}
</style></head><body><h1>Rires à choisir</h1>
<p class="aide">Écoutez, puis touchez la lettre (A, B, C ou D) du rire à garder pour chaque ligne. Si le type d'un personnage est faux (ex. Moussa = adolescent), dites-le simplement.</p>
{''.join(cartes)}<div class="barre"><code id="rep">Aucun choix</code><button id="copie">Copier</button></div>
<script>const choix={{}};document.querySelectorAll('.opt .l').forEach(s=>s.onclick=()=>{{const b=s.parentElement,q=b.dataset.q;
document.querySelectorAll('.opt[data-q="'+q+'"]').forEach(x=>x.classList.remove('on'));if(choix[q]===b.dataset.l){{delete choix[q]}}else{{choix[q]=b.dataset.l;b.classList.add('on')}}
document.getElementById('rep').textContent=Object.keys(choix).sort((a,b)=>a-b).map(k=>k+choix[k]).join(' ')||'Aucun choix'}});
document.getElementById('copie').onclick=()=>{{const t=document.getElementById('rep').textContent;if(t==='Aucun choix')return;try{{navigator.clipboard.writeText(t).then(()=>{{document.getElementById('copie').textContent='Copié ✓'}},()=>prompt('Copiez :',t))}}catch(e){{prompt('Copiez :',t)}}}};</script></body></html>''')
def choisir(reponse, out, log=print):
    import shutil
    qs = {q['n']: q for q in json.load(open(os.path.join(out, 'rires.json'), encoding='utf-8'))['questions']}; os.makedirs(R, exist_ok=True)
    for n, l in re.findall(r'(\d+)\s*[:=]?\s*([A-Da-d])\b', reponse or ''):
        q = qs.get(int(n)); o = next((o for o in (q or {}).get('options', []) if o['lettre'] == l.upper()), None)
        if not o or not os.path.exists(o['fichier']): log(f'question {n} lettre {l} inconnue, ignorée'); continue
        shutil.copy(o['fichier'], fichier(q['perso'], q['sorte'])); log(f"rire gardé : {q['perso']} {SORTES[q['sorte']]} ({l})")

def pour_episode(qui, work, log=print):
    """Rires d'un épisode : {(perso, sorte)} → voix/rire_<PERSO>[_petit].wav. Rire choisi par Issa s'il existe, sinon fabriqué (1er style du type)."""
    import shutil
    cat = catalogue(); jobs = []; os.makedirs(f'{work}/voix', exist_ok=True)
    def dst(c, so): return f'{work}/voix/rire_{c}' + ('' if so == 'eclat' else '_' + so) + '.wav'
    for c, so in sorted(qui):
        if os.path.exists(dst(c, so)): continue
        if os.path.exists(fichier(c, so)): shutil.copy(fichier(c, so), dst(c, so)); continue
        txt, ex = STYLES[age(c, cat)][so][0]; jobs.append({'out': dst(c, so) + '.brut.wav', 'ref': voix(c, cat), 'text': txt, 'exag': ex, 'turbo': True, '_c': (c, so)})
    if jobs: log(f'rires : {len(jobs)} à fabriquer (pas encore choisis)'); generer([{k: v for k, v in j.items() if k != '_c'} for j in jobs], work)
    for j in jobs:
        if os.path.exists(j['out']): nettoyer(j['out'], dst(*j['_c']), j['_c'][1])
    return jobs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('-o', '--out', default='sortie_rires'); ap.add_argument('--perso', default=None); ap.add_argument('--choix', default=None)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.choix: choisir(a.choix, a.out); return
    cat = catalogue(); persos = [x.strip().upper() for x in a.perso.split(',')] if a.perso else [c for c in cat['voices'] if c not in ('VOIX_OFF', 'VENDEUSE')]
    candidats(persos, a.out)
if __name__ == '__main__': main()
