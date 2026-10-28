"""Planches à valider : l'application prépare elle-même les choix A, B, C, D (poses, cadrages) et les montre en images fixes.
Issa coche ses réponses (page planches.html, ou il écrit simplement « 1B 3C ») ; la réponse est gardée dans <script>.choix.json
et la mise en scène la suit ensuite (director.CHOIX). Rien n'est retouché à la main.

Sans plans précisés : seulement les plans où l'application hésite (deux poses presque aussi bonnes l'une que l'autre).
Avec --plans ou --de / --a : toutes les questions (pose et cadrage) sur ces plans-là."""
import os, re, io, json, copy, base64, html
from PIL import Image, ImageDraw
import director, render, gfx
from director import POSES
LETTRES = 'ABCD'
DOUTE = 1.5   # écart de note entre les deux meilleures poses en dessous duquel l'application demande
MAX_AUTO = 12
CADRAGE_NOM = {'epaule': "Derrière l'épaule de celui qui écoute", 'seul': 'Gros plan, seul', 'large': 'Plan large, tout le monde'}
SUJET_TXT = {'pose': 'Quelle pose ?', 'cadrage': 'Quel cadrage ?'}

def temps(t): return f'{int(t // 60)}:{int(t % 60):02d}'
def lire_temps(x):
    """« 1:20 » ou « 80 » → secondes."""
    if x is None: return None
    p = [float(v) for v in str(x).replace(',', '.').split(':')]
    return p[0] * 60 + p[1] if len(p) == 2 else p[0]
def lire_plans(txt):
    """« 12,14-16 » → {12, 14, 15, 16}"""
    out = set()
    for part in re.split(r'[,\s]+', txt or ''):
        if '-' in part: a, b = part.split('-'); out.update(range(int(a), int(b) + 1))
        elif part.isdigit(): out.add(int(part))
    return out
def choisir_plans(shots, plans=None, de=None, a=None):
    sel = set(plans or [])
    if de is not None or a is not None:
        t0, t1 = de or 0, a if a is not None else 1e9
        sel |= {i for i, s in enumerate(shots) if s['t0'] < t1 and s['t0'] + s['dur'] > t0}
    return sel or None

def principaux(s):
    """Les acteurs sur qui porte la question de pose : celui qui parle, ou l'acteur seul du plan."""
    acts = [a for a in s.get('actors', []) if a.get('pick') and not (a.get('fg') or a.get('back') or a.get('silhouette') or a.get('walk'))]
    return [a for a in acts if a.get('speaker')] or (acts if len(acts) == 1 else [])
def options_pose(a):
    cur = a['key'].split('@')[0]; r = director.rank(**a['pick'])
    keys = [cur] + [k for k, _ in r if k != cur][:len(LETTRES) - 1]
    gap = (r[0][1] - r[1][1]) if len(r) > 1 else 99
    return keys, gap
def questions(shots, sel=None, sujets=('pose', 'cadrage'), deja=None):
    """Liste des questions. Une même hésitation (même personnage, mêmes poses proposées) sur plusieurs plans = une seule question."""
    deja = deja or {}; qs = {}; auto = sel is None
    for i, s in enumerate(shots):
        if not auto and i not in sel: continue
        if 'pose' in sujets:
            for a in principaux(s):
                if auto and a['who'] in director.poses_choisies(deja.get(str(i), {})): continue   # déjà choisi pour ce personnage
                keys, gap = options_pose(a)
                if len(keys) < 2 or (auto and gap > DOUTE): continue
                q = qs.setdefault(('pose', a['who'], tuple(keys)), {'sujet': 'pose', 'who': a['who'], 'plans': [], 'gap': gap,
                     'options': [{'valeur': {'who': a['who'], 'key': k}, 'texte': ' · '.join(POSES[k]['tags'][:3])} for k in keys]})
                q['plans'].append(i)
        if 'cadrage' in sujets and not auto and s.get('cadrages'):
            names = [s['cadrage']] + [n for n in ('epaule', 'seul', 'large') if n in s['cadrages']]
            qs[('cadrage', i)] = {'sujet': 'cadrage', 'who': s.get('who', ''), 'plans': [i], 'gap': 0,
                                  'options': [{'valeur': n, 'texte': CADRAGE_NOM[n]} for n in names]}
    out = sorted(qs.values(), key=lambda q: q['plans'][0])
    if auto: out = sorted(sorted(out, key=lambda q: q['gap'])[:MAX_AUTO], key=lambda q: q['plans'][0])
    for n, q in enumerate(out, 1):
        q['n'] = n
        for o, l in zip(q['options'], LETTRES): o['lettre'] = l
        q['options'][0]['texte'] += ' (actuelle)'
    return out

def variante(s, q, o):
    """Le plan tel qu'il serait avec l'option o."""
    s2 = copy.deepcopy(s)
    if q['sujet'] == 'pose':
        for a in s2.get('actors', []):
            if a['who'] == o['valeur']['who'] and a.get('pick') and not (a.get('fg') or a.get('back') or a.get('silhouette')):
                director.set_pose(a, o['valeur']['key']); break
    elif o['valeur'] != s.get('cadrage'):
        s2.update(copy.deepcopy(s['cadrages'][o['valeur']])); s2['cadrage'] = o['valeur']
        if s2.get('mode') == 'wide': s2['switch'] = []
    director.orient_shot(s2); return s2
def zoom(im, s, q, o):
    """Question de pose dans un plan large : on resserre l'image sur la personne (sinon elle est trop petite sur un téléphone)."""
    if q['sujet'] != 'pose' or s.get('mode', 'wide' if s['kind'] == 'wide' else 'close') != 'wide': return im
    a = next((a for a in s.get('actors', []) if a['who'] == o['valeur']['who'] and not a.get('fg')), None)
    if not a: return im
    h = min(1920, max(960, int(a['h'] * 1.25))); w = h * 9 // 16
    x0 = int(min(max(a['x'] - w / 2, 0), 1080 - w)); y1 = int(min(1920, a['by'] + 40)); y0 = max(0, y1 - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)

def make(shots, out, sel=None, sujets=('pose', 'cadrage'), deja=None, log=print, script=''):
    qs = questions(shots, sel, sujets, deja)
    d = os.path.join(out, 'planches'); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith('planche_') or f in ('planches.html', 'planches.json'): os.remove(os.path.join(d, f))
    if not qs:
        log("planches : aucune hésitation, rien à valider" if sel is None else 'planches : aucune question possible sur ces plans'); return []
    var = {}
    for q in qs:
        s = shots[q['plans'][0]]
        for o in q['options']: var[(q['n'], o['lettre'])] = variante(s, q, o)
    render.prepare_turns(list(var.values()), log)   # têtes tournées des nouvelles poses
    imgs = {}
    for q in qs:
        for o in q['options']:
            v = var[(q['n'], o['lettre'])]; imgs[(q['n'], o['lettre'])] = zoom(render.draw(v, render.moment(v, q['sujet'] == 'pose')).convert('RGB'), v, q, o)
    json.dump({'script': script, 'questions': [dict({k: v for k, v in q.items() if k != 'gap'}, sigs={str(p): director.sig(shots, p) for p in q['plans']}) for q in qs]}, open(os.path.join(d, 'planches.json'), 'w'), ensure_ascii=False, indent=1)
    tit = {q['n']: titre(q, shots) for q in qs}
    pngs = pages(qs, tit, imgs, d); page_html(qs, tit, imgs, os.path.join(d, 'planches.html'), os.path.splitext(os.path.basename(script))[0] or 'épisode')
    log(f'planches : {len(qs)} questions → planches/planches.html et {len(pngs)} image(s) planche_N.png')
    return qs

def titre(q, shots):
    s = shots[q['plans'][0]]; pl = ', '.join(str(p) for p in q['plans'][:6]) + ('…' if len(q['plans']) > 6 else '')
    who = gfx.nom(q['who']) if q['who'] else ''
    rep = ''
    if s.get('line'): t = s['line']['text']; rep = '« ' + (t if len(t) <= 60 else t[:58] + '…') + ' »'
    return f"Question {q['n']} · plan{'s' if len(q['plans']) > 1 else ''} {pl} · {temps(s['t0'])}", f"{SUJET_TXT[q['sujet']]}  {who}", rep
def pages(qs, tit, imgs, d, par_page=3, prefixe='planche_'):
    """Images de secours (pour WhatsApp ou GitHub) : 3 questions par image, largeur d'un téléphone."""
    tw, th, gap, head, foot = 258, 459, 8, 120, 64; row = head + th + foot
    fb, fr = gfx.font(gfx.FB, 30), gfx.font(gfx.FB, 22); out = []
    for p in range(0, len(qs), par_page):
        grp = qs[p:p + par_page]; c = Image.new('RGB', (1080, row * len(grp) + 10), 'white'); dr = ImageDraw.Draw(c)
        for r, q in enumerate(grp):
            y = r * row + 10; l1, l2, l3 = tit[q['n']]
            dr.text((12, y), l1, font=fb, fill=gfx.FONCE); dr.text((12, y + 40), l2, font=fb, fill=gfx.ORANGE); dr.text((12, y + 80), l3, font=fr, fill=(90, 90, 90))
            for k, o in enumerate(q['options']):
                x = gap + k * (tw + gap); c.paste(imgs[(q['n'], o['lettre'])].resize((tw, th), Image.LANCZOS), (x, y + head))
                dr.ellipse((x + 8, y + head + 8, x + 76, y + head + 76), fill=gfx.ORANGE, outline='white', width=4)
                dr.text((x + 42, y + head + 42), o['lettre'], font=gfx.font(gfx.FB, 44), fill='white', anchor='mm')
                for i, ln in enumerate(gfx.wrap(o['texte'], fr, tw - 4)[:2]): dr.text((x + 2, y + head + th + 6 + i * 26), ln, font=fr, fill=(40, 40, 40))
        f = os.path.join(d, f'{prefixe}{p // par_page + 1}.png'); c.save(f); out.append(f)
    return out
def b64(im):
    b = io.BytesIO(); im.resize((360, 640), Image.LANCZOS).save(b, 'JPEG', quality=80); return base64.b64encode(b.getvalue()).decode()
def page_html(qs, tit, imgs, path, nom='épisode', aide=None):
    """Page à cocher (téléphone) : on touche une image par question, la réponse « 1B 3C » s'écrit toute seule en bas."""
    cartes = []
    for q in qs:
        l1, l2, l3 = (html.escape(x) for x in tit[q['n']])
        opts = ''.join(f'<button class="opt" data-q="{q["n"]}" data-l="{o["lettre"]}"><img src="data:image/jpeg;base64,{b64(imgs[(q["n"], o["lettre"])])}" alt="Option {o["lettre"]}">'
                       f'<span class="l">{o["lettre"]}</span><span class="t">{html.escape(o["texte"])}</span></button>' for o in q['options'])
        cartes.append(f'<section><h2>{l1}</h2><p class="q">{l2}</p><p class="r">{l3}</p><div class="grid">{opts}</div></section>')
    nom = html.escape(nom); aide = html.escape(aide or "Une question sans réponse = on garde l'image A.")
    page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Planches à valider</title>
<style>
:root{{--fond:#f6f3ee;--carte:#fff;--texte:#222;--doux:#666;--accent:#e8731a;--bord:#ddd}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}}}
:root[data-theme="dark"]{{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fond);color:var(--texte);font:16px/1.4 system-ui,sans-serif;padding:12px 12px 110px;overflow-x:hidden}}
h1{{font-size:20px;margin:4px 0 2px}}.aide{{color:var(--doux);font-size:14px;margin:0 0 12px}}
section{{background:var(--carte);border:1px solid var(--bord);border-radius:12px;padding:10px;margin:0 0 14px}}
h2{{font-size:15px;margin:0}}.q{{margin:2px 0;color:var(--accent);font-weight:700}}.r{{margin:0 0 8px;color:var(--doux);font-size:13px;word-wrap:break-word}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.opt{{position:relative;border:3px solid transparent;border-radius:10px;padding:0;background:none;color:inherit;text-align:left;cursor:pointer;min-width:0}}
.opt img{{width:100%;display:block;border-radius:7px;aspect-ratio:9/16;object-fit:cover}}
.opt .l{{position:absolute;top:6px;left:6px;width:36px;height:36px;border-radius:50%;background:var(--accent);color:#fff;font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center;border:2px solid #fff}}
.opt .t{{display:block;font-size:12px;padding:3px 2px 0;color:var(--doux);word-wrap:break-word}}
.opt.on{{border-color:var(--accent)}}.opt.on .t{{color:var(--texte);font-weight:700}}
.barre{{position:fixed;left:0;right:0;bottom:0;background:var(--carte);border-top:1px solid var(--bord);padding:10px 12px;display:flex;gap:8px;align-items:center}}
.barre code{{flex:1;min-width:0;font-size:17px;font-weight:700;overflow-wrap:anywhere}}
.barre button{{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-weight:700;font-size:15px;flex:none}}
</style></head><body>
<h1>Planches à valider — {nom}</h1>
<p class="aide">Touchez une image par question, puis « Copier » : dans la page Studio mobile, le bouton « Envoyer ma réponse » apparaît (ou collez la réponse en commentaire sur GitHub). {aide}</p>
{''.join(cartes)}
<div class="barre"><code id="rep">Aucun choix</code><button id="copie">Copier</button></div>
<script>
const choix={{}};
document.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{{const q=b.dataset.q;
 document.querySelectorAll('.opt[data-q="'+q+'"]').forEach(x=>x.classList.remove('on'));
 if(choix[q]===b.dataset.l){{delete choix[q]}}else{{choix[q]=b.dataset.l;b.classList.add('on')}}
 const t=Object.keys(choix).sort((a,b)=>a-b).map(k=>k+choix[k]).join(' ');document.getElementById('rep').textContent=t||'Aucun choix'}});
document.getElementById('copie').onclick=()=>{{const t=document.getElementById('rep').textContent;if(t==='Aucun choix')return;
 const ok=()=>{{const b=document.getElementById('copie');b.textContent='Copié ✓';setTimeout(()=>b.textContent='Copier',1500)}};
 try{{navigator.clipboard.writeText(t).then(ok,()=>{{prompt('Copiez :',t)}})}}catch(e){{prompt('Copiez :',t)}}}};
</script></body></html>'''
    open(path, 'w', encoding='utf-8').write(page)

def appliquer(reponse, planches_json, choix_path, log=print):
    """« 1B 3C » → décisions gardées dans le fichier des choix (par numéro de plan)."""
    data = json.load(open(planches_json, encoding='utf-8')); qs = {q['n']: q for q in data['questions']}
    choix = json.load(open(choix_path, encoding='utf-8')) if os.path.exists(choix_path) else {}
    pairs = re.findall(r'(\d+)\s*[:=]?\s*([A-Da-d])\b', reponse or '')
    if not pairs: log(f'choix : réponse illisible « {reponse} » (exemple attendu : 1B 3C)'); return choix
    for n, l in pairs:
        q = qs.get(int(n)); l = l.upper()
        o = next((o for o in (q or {}).get('options', []) if o['lettre'] == l), None)
        if not o: log(f'choix : question {n} lettre {l} inconnue, ignorée'); continue
        for p in q['plans']:
            c = choix.setdefault(str(p), {}); g = (q.get('sigs') or {}).get(str(p))
            if c.get('sig') and g and c['sig'] != g: c.clear()   # ancien choix d'un autre plan (le script a bougé) : remplacé
            if g: c['sig'] = g
            v = o['valeur']
            if q['sujet'] == 'pose' and isinstance(v, dict) and v.get('who'):   # une pose par personnage (sinon un choix sur Sali effaçait celui sur Fatim)
                c.setdefault('poses', {})[v['who'].upper()] = v['key']
                if (c.get('pose') or {}).get('who', '').upper() == v['who'].upper(): c.pop('pose')
            else: c[q['sujet']] = v
        log(f"choix : question {n} → {l} ({o['texte']}) sur le{'s' if len(q['plans']) > 1 else ''} plan{'s' if len(q['plans']) > 1 else ''} {', '.join(map(str, q['plans']))}")
    json.dump(choix, open(choix_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    return choix
