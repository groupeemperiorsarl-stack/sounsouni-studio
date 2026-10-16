"""Fiche Gemini : l'application lit les scripts, trouve les images qui manquent (poses, vues de dos, poses assises, nouveaux
personnages, nouveaux décors) et prépare pour chacune l'image de référence + la demande prête à coller dans Gemini (gratuit).
Issa génère les images dans Gemini et les renvoie ; l'application les détoure et les range elle-même.

1. python -m studio.gemini exemples/episode16.txt exemples/episode17.txt -o sortie_gemini
      → sortie_gemini/fiche_gemini.html (téléphone) + fiche_gemini.json + references/
2. python -m studio.gemini -o sortie_gemini --importer "1=image_a.png 2=image_b.jpg"
      → images rangées (poses dans le catalogue, décors dans assets/decors)"""
import os, sys, io, re, json, base64, html, argparse, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('STUDIO_FAUSSES_VOIX', '1')
from PIL import Image
import script, voices, director, gfx
A = director.A
FEMMES = {'AWA', 'MIMI', 'KADI', 'SALI', 'FATIM', 'VENDEUSE'}
# émotion / geste demandé dans le script → description (masculin, féminin)
DESC = {
    'colere': ('en colère, les sourcils froncés', 'en colère, les sourcils froncés'), 'furieux': ('furieux', 'furieuse'), 'choc': ('choqué, la bouche ouverte', 'choquée, la bouche ouverte'),
    'surpris': ('surpris, les yeux grands ouverts', 'surprise, les yeux grands ouverts'), 'peur': ('apeuré', 'apeurée'), 'panique': ('paniqué', 'paniquée'),
    'triste': ('triste, le regard baissé', 'triste, le regard baissé'), 'pleure': ('en larmes', 'en larmes'), 'gene': ('gêné, un sourire embarrassé', 'gênée, un sourire embarrassé'),
    'mepris': ('méprisant', 'méprisante'), 'mefiant': ('méfiant, les yeux plissés', 'méfiante, les yeux plissés'), 'amoureux': ('amoureux, le regard rêveur', 'amoureuse, le regard rêveur'),
    'fier': ('fier, le torse bombé', 'fière, le menton levé'), 'moue': ('qui fait la moue', 'qui fait la moue'), 'degout': ('dégoûté', 'dégoûtée'), 'taquin': ('taquin, un sourire en coin', 'taquine, un sourire en coin'),
    'pensif': ('pensif, la main au menton', 'pensive, la main au menton'), 'serieux': ('sérieux', 'sérieuse'), 'inquiet': ('inquiet', 'inquiète'), 'tendre': ('tendre', 'tendre'),
    'moqueur': ('moqueur', 'moqueuse'), 'froide': ('froid et distant', 'froide et distante'), 'joie': ('joyeux, grand sourire', 'joyeuse, grand sourire'), 'rire': ('qui éclate de rire', 'qui éclate de rire'),
    'sourire': ('souriant', 'souriante'), 'content': ('content', 'contente'), 'severe': ('sévère', 'sévère'), 'emu': ('ému', 'émue'), 'neutre': ('calme, l\'air neutre', 'calme, l\'air neutre'),
    'mains_tete': ('les deux mains sur la tête', 'les deux mains sur la tête'), 'pointe': ('qui pointe du doigt devant lui', 'qui pointe du doigt devant elle'),
    'mains_levees': ('les mains levées', 'les mains levées'), 'bras_croises': ('les bras croisés', 'les bras croisés'), 'supplie': ('qui supplie, les mains jointes', 'qui supplie, les mains jointes'),
    'salue': ('qui salue de la main', 'qui salue de la main'), 'telephone': ('qui regarde son téléphone', 'qui regarde son téléphone'),
    'emerveille': ('émerveillé, les yeux brillants, bouche entrouverte', 'émerveillée, les yeux brillants, bouche entrouverte'), 'determine': ('déterminé, le regard droit', 'déterminée, le regard droit'),
    'confus': ('perdu, qui se gratte la tête', 'perdue, qui se gratte la tête'), 'timide': ('timide, le regard baissé', 'timide, le regard baissé'),
    'reveur': ('rêveur, un petit sourire amoureux', 'rêveuse, un petit sourire amoureux'), 'sage': ('calme et sage, un léger sourire', 'calme et sage, un léger sourire'),
    'victoire': ('qui lève le poing de joie', 'qui lève le poing de joie'),
}
STYLE = ("Garde exactement le même personnage que sur l'image jointe : même visage, même coiffure, mêmes vêtements, mêmes couleurs, "
         "même style dessin animé 3D. ")
FOND = "Corps entier de la tête aux pieds, sur un fond gris clair uni, sans aucun décor ni autre personnage. Image verticale."

CANON = {'fiere': 'fier', 'determinee': 'determine', 'emerveillee': 'emerveille', 'reveuse': 'reveur', 'contente': 'content', 'surprise': 'surpris',
         'inquiete': 'inquiet', 'furieuse': 'furieux', 'amoureuse': 'amoureux'}   # féminin → même pose
TENUES = {}; OBJETS = {}   # descriptions lues dans l'en-tête des scripts (NOUVELLE TENUE / NOUVEL OBJET)
def desc(mot, femme):
    if mot.startswith('pose:'): return mot[5:].replace('_', ' ')
    d = DESC.get(mot); return d[1 if femme else 0] if d else mot.replace('_', ' ')
def objet_connu(o):
    n = script.norm(o)
    if any(p['frame'] == 'objet' and any(w in n for w in p['tags']) for p in director.POSES.values()): return True
    return gfx.draw_object(n) is not None or 'telephone' in n or 'ecran' in n
def poses_de(c): return {k: p for k, p in director.POSES.items() if p['char'] == c and '@' not in k}
def reference(c, posture='debout'):
    """Image de départ : même posture si elle existe, en pied, calme, sans objet, bras le long du corps."""
    best, bs = None, -1e9
    for k, p in poses_de(c).items():
        if p['frame'] != 'pied' or p['posture'] in ('dos', 'tombe', 'court', 'marche') or p.get('tenue'): continue
        t = set(p['tags']); w, h = p['size']; objets = set(p.get('props', [])) | (t & director.OBJ)
        sc = (30 if (p['posture'] in ('assis', 'banc')) == (posture in ('assis', 'banc')) else 0) + 3 * len(t & {'neutre', 'ecoute', 'serieux'}) \
             - 2 * len(t & director.GESTE) - len(t & (director.POS | director.NEG)) - 6 * w / h - 20 * len(objets)
        if sc > bs: best, bs = k, sc
    return best

def analyse(path, log=print):
    """Plans d'un script (voix d'essai : seules les durées sont approximatives)."""
    meta, ev = script.parse(open(path, encoding='utf-8').read())
    work = os.path.join('/tmp', 'gemini_' + os.path.splitext(os.path.basename(path))[0]); os.makedirs(work, exist_ok=True)
    voices.run(ev, director.CAT, work, lambda m: None)
    shots, _ = director.build(meta, ev, lambda m: None)
    return meta, shots
def besoins(paths, log=print, tout=False, maxi=16):
    """Ce qu'il faut générer pour ces scripts, le plus demandé d'abord."""
    b = {}; ep = lambda p: os.path.splitext(os.path.basename(p))[0]
    def add(key, item, ou):
        x = b.setdefault(key, dict(item, ou=[])); x['ou'].append(ou)
    for p in paths:
        meta, shots = analyse(p, log)
        for nc in meta['new_chars']:
            nom = re.split(r'\s*[—–-]\s*', nc, 1)[0].strip().upper(); d = nc[len(nom):].strip(' —–-')
            if nom not in director.HEIGHT: add(('perso', nom), {'type': 'personnage', 'perso': nom, 'texte': d}, ep(p))
        for nd in meta['new_decors']:
            nom = re.split(r'\s*[—–:-]\s*', nd, 1)[0].strip().upper(); d = nd[len(nom):].strip(' —–:-')
            if not os.path.exists(f'{A}/decors/{nom}.jpg'): add(('decor', nom), {'type': 'decor', 'perso': nom, 'texte': d or nom.lower()}, ep(p))
        for nt in meta.get('new_outfits', []):   # « AWA — bazin doré : grande tenue de cérémonie… »
            m = re.match(r'\s*([^—–:-]+?)\s*[—–-]\s*([^:]+?)\s*(?::\s*(.*))?$', nt)
            if m: TENUES[(script.who(m.group(1)), script.tenue_id(m.group(2)))] = (m.group(2).strip(), (m.group(3) or m.group(2)).strip())
        for nob in meta.get('new_objects', []): OBJETS[script.norm(re.split(r'\s*[—–:]\s*', nob, 1)[0])] = nob
        for i, s in enumerate(shots):
            ou = f'{ep(p)} plan {i}'
            if s['kind'] == 'insert' and (script.norm(s.get('object', '')) in OBJETS or not objet_connu(s.get('object', ''))):   # objet annoncé comme nouveau, ou inconnu
                o = s.get('object', ''); add(('objet', script.norm(o)), {'type': 'objet', 'perso': o, 'texte': OBJETS.get(script.norm(o), o)}, ou)
            for a in s.get('actors', []):
                if a.get('silhouette') and a['who'] in director.HEIGHT: add(('pose', a['who'], 'dos', ''), {'type': 'pose', 'perso': a['who'], 'posture': 'dos', 'emo': ''}, ou)
                pa = a.get('pick')
                if not pa or a.get('fg') or a.get('back'): continue
                verif(pa, add, ou)
            for c in s.get('cuts', []): verif({'char': c['who'], 'want': c['actions'] + c.get('props', []), 'frame': 'buste', 'posture': c.get('posture'), 'need_mouth': False}, add, ou)
    prio = lambda x: {'personnage': 6, 'decor': 5, 'objet': 3}.get(x['type'], 4 if x.get('tenue') or str(x.get('emo', '')).startswith('pose:') else 0)
    out = sorted(b.values(), key=lambda x: (-prio(x), -len(x['ou'])))
    if not tout:   # le nécessaire : nouveautés (personnages, décors, tenues, objets, {POSE}), vues de dos, assis, émotions demandées au moins 2 fois
        out = [x for x in out if prio(x) or x['type'] != 'pose' or not x['emo'] or len(x['ou']) >= 2][:maxi]
    for n, x in enumerate(out, 1): x['n'] = n
    return out
def verif(pa, add, ou):
    """La pose que l'application choisirait montre-t-elle ce que le script demande (émotion / geste, assis) ?"""
    char, want, posture = pa['char'], pa['want'], pa.get('posture')
    if char not in director.HEIGHT: return
    r = director.rank(**pa)
    if not r: return
    best = director.POSES[r[0][0]]; tags = set(best['tags']) | set(best.get('props', []))
    assis = posture in ('assis', 'banc'); post = 'assis' if assis else 'debout'
    t = pa.get('tenue', '')
    for m in want:   # pose précise demandée par le script : {POSE: mains sur la tête}
        if m.startswith('pose:') and m not in tags: add(('pose', char, post, m, t), {'type': 'pose', 'perso': char, 'posture': post, 'emo': m, 'tenue': t}, ou); return
    emo = next((m for m in want if (m in director.EMOS or m in director.GESTE or m in DESC) and m != 'neutre'), '')
    emo = CANON.get(emo, emo)
    if t and best.get('tenue', '') != t:   # le personnage porte une tenue spéciale : il faut des images dans cette tenue
        add(('pose', char, post, '', t), {'type': 'pose', 'perso': char, 'posture': post, 'emo': '', 'tenue': t}, ou)
        if emo: add(('pose', char, post, emo, t), {'type': 'pose', 'perso': char, 'posture': post, 'emo': emo, 'tenue': t}, ou)
        return
    if assis and best['posture'] not in ('assis', 'banc'):   # assis dans le script, mais aucune pose assise qui convient
        add(('pose', char, 'assis', emo), {'type': 'pose', 'perso': char, 'posture': 'assis', 'emo': emo}, ou); return
    for mot in want:
        if (mot in director.EMOS or mot in director.GESTE or mot in DESC) and mot not in ('neutre',) and not (director.tagwords([mot]) & tags):
            add(('pose', char, post, mot), {'type': 'pose', 'perso': char, 'posture': post, 'emo': mot}, ou); break

def demande(x):
    """La phrase à coller dans Gemini (en français)."""
    if x['type'] == 'decor':
        return ("Crée un décor de dessin animé 3D, dans le même style que l'image jointe : " + x['texte'] +
                ". Lieu malien réaliste et coloré, à Bamako, sans aucun personnage. Image verticale.")
    if x['type'] == 'objet':
        return ("Dessine cet objet dans exactement le même style dessin animé 3D que l'image jointe : " + x['texte'] +
                ". L'objet seul, en entier, bien éclairé, sur un fond gris clair uni, sans personnage. Image verticale.")
    if x['type'] == 'personnage':
        return ("Crée un nouveau personnage dans exactement le même style dessin animé 3D que le personnage de l'image jointe : " + x['texte'] +
                ". Debout, de face, bras le long du corps, bouche fermée, expression neutre. " + FOND)
    f = x['perso'] in FEMMES
    if x['posture'] == 'dos': pose = 'vu de dos, debout, les bras le long du corps, on ne voit pas son visage' if not f else 'vue de dos, debout, les bras le long du corps, on ne voit pas son visage'
    elif x['posture'] == 'assis': pose = ('assise' if f else 'assis') + ' sur un petit banc en bois, de trois-quarts, les mains sur les genoux' + (', ' + desc(x['emo'], f) if x['emo'] else ', bouche fermée')
    else: pose = 'debout, de trois-quarts, ' + desc(x['emo'], f) + ', bouche fermée'
    rp = director.POSES.get(x.get('ref') or '', {}); objet = set(rp.get('props', [])) | (set(rp.get('tags', [])) & director.OBJ)
    st = STYLE
    if x.get('suite_de'):   # même tenue qu'une image précédente de la fiche : on joint cette image-là
        st = STYLE
    elif x.get('tenue') and rp.get('tenue') != x['tenue']:   # première image dans la nouvelle tenue : on décrit les habits
        st = ("Garde exactement le même personnage que sur l'image jointe : même visage, même coiffure, même corpulence, même style dessin animé 3D, "
              "mais " + ('habillée' if f else 'habillé') + " de : " + TENUES.get((x['perso'], x['tenue']), (x['tenue'], x['tenue'].replace('_', ' ')))[1] + ". ")
    return st + 'Montre-' + ('la ' if f else 'le ') + pose + '. ' + (('Elle' if f else 'Il') + ' ne tient rien dans les mains. ' if objet else '') + FOND
def ref_pour(x):
    if x['type'] == 'decor':
        d = sorted(f for f in os.listdir(f'{A}/decors') if f.endswith('.jpg')); return ('decor', 'KIOSQUE.jpg' if 'KIOSQUE.jpg' in d else d[0])
    if x['type'] == 'personnage': return ('pose', reference('BAKARY') if x['perso'] not in FEMMES else reference('AWA'))
    if x['type'] == 'objet': return ('pose', next((k for k, p in director.POSES.items() if p['frame'] == 'objet'), reference('BAKARY')))
    if x.get('tenue'):   # une image déjà faite dans cette tenue sert de modèle (mêmes habits partout)
        k = next((k for k, p in poses_de(x['perso']).items() if p.get('tenue') == x['tenue']), None)
        if k: return ('pose', k)
    return ('pose', reference(x['perso'], x['posture']))
def image_ref(kind, k, out):
    """Image à joindre dans Gemini, enregistrée dans references/ (pose détourée posée sur fond gris)."""
    d = os.path.join(out, 'references'); os.makedirs(d, exist_ok=True)
    if kind == 'decor': im = Image.open(f'{A}/decors/{k}').convert('RGB'); im.thumbnail((1080, 1920))
    else:
        p = Image.open(f'{A}/poses/{k}.webp').convert('RGBA'); s = 1500 / p.height; p = p.resize((max(1, int(p.width * s)), 1500), Image.LANCZOS)
        im = Image.new('RGB', (max(900, p.width + 200), 1700), (222, 222, 222)); im.paste(p, ((im.width - p.width) // 2, 100), p)
    im.thumbnail((900, 1600)); f = os.path.join(d, f'ref_{os.path.splitext(k)[0]}.jpg'); im.save(f, quality=85); return f
def titre(x):
    if x['type'] == 'decor': return f"Nouveau décor : {x['perso'].title()}"
    if x['type'] == 'personnage': return f"Nouveau personnage : {x['perso'].title()}"
    if x['type'] == 'objet': return f"Nouvel objet : {x['perso']}"
    q = {'dos': 'vue de dos', 'assis': 'assis'}.get(x['posture'], 'debout') + (f", {desc(x['emo'], x['perso'] in FEMMES).split(',')[0]}" if x['emo'] else '')
    if x.get('tenue'): q += ' — ' + TENUES.get((x['perso'], x['tenue']), (x['tenue'].replace('_', ' '),))[0]
    return f"{gfx.nom(x['perso'])} — {q}"

def fiche(items, out, log=print):
    os.makedirs(out, exist_ok=True); cartes = []; premiere = {}
    for x in items:
        kind, k = ref_pour(x); x['ref'] = k if kind == 'pose' else None
        if x.get('tenue') and not director.POSES.get(k, {}).get('tenue'):   # pas encore d'image dans cette tenue : la 1re de la fiche sert de modèle aux suivantes
            if (x['perso'], x['tenue']) in premiere: x['suite_de'] = premiere[(x['perso'], x['tenue'])]
            else: premiere[(x['perso'], x['tenue'])] = x['n']
        x['demande'] = demande(x); f = image_ref(kind, k, out); x['fichier_ref'] = os.path.basename(f)
        note = f'<p class="note">① Joignez plutôt l\'image que vous avez obtenue au n° {x["suite_de"]} (même tenue).</p>' if x.get('suite_de') else ''
        th = Image.open(f); th.thumbnail((420, 640)); b = io.BytesIO(); th.save(b, 'JPEG', quality=82)
        ou = ', '.join(x['ou'][:4]) + (f' … ({len(x["ou"])} fois)' if len(x['ou']) > 4 else '')
        cartes.append(f'''<section><h2><span class="n">{x["n"]}</span>{html.escape(titre(x))}</h2><p class="ou">Demandé : {html.escape(ou)}</p>
<div class="ligne"><a class="ref" href="data:image/jpeg;base64,{base64.b64encode(open(f, "rb").read()).decode()}" download="{x["n"]}_{html.escape(x["fichier_ref"])}"><img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}" alt="image à joindre"><span>① Image à joindre<br>(envoyée à part : « image_pour_n…»)</span></a>
<div class="dem">{note}<p class="txt" id="d{x["n"]}">{html.escape(x["demande"])}</p><button data-c="d{x["n"]}">② Copier la demande</button></div></div></section>''')
    page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fiche Gemini</title><style>
:root{{--fond:#f6f3ee;--carte:#fff;--texte:#222;--doux:#666;--accent:#e8731a;--bord:#ddd}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}}}
:root[data-theme="dark"]{{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fond);color:var(--texte);font:16px/1.45 system-ui,sans-serif;padding:12px;overflow-x:hidden}}
h1{{font-size:20px;margin:4px 0}}.aide{{color:var(--doux);font-size:14px;margin:0 0 12px}}.aide b{{color:var(--texte)}}
section{{background:var(--carte);border:1px solid var(--bord);border-radius:12px;padding:10px;margin:0 0 14px}}
h2{{font-size:16px;margin:0 0 2px;display:flex;gap:8px;align-items:center}}.n{{flex:none;width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px}}
.ou{{margin:0 0 8px;color:var(--doux);font-size:12px;word-wrap:break-word}}.ligne{{display:flex;gap:10px;align-items:flex-start}}
.ref{{flex:0 0 32%;text-decoration:none;color:var(--doux);font-size:11px;text-align:center}}.ref img{{width:100%;border-radius:8px;display:block;margin-bottom:3px}}
.dem{{flex:1;min-width:0}}.note{{margin:0 0 6px;font-size:13px;font-weight:700;color:var(--accent)}}.txt{{margin:0 0 8px;font-size:13px;background:var(--fond);border-radius:8px;padding:8px;word-wrap:break-word}}
button{{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:9px 10px;font-weight:700;font-size:14px;width:100%}}
</style></head><body><h1>Fiche Gemini — {len(items)} image(s)</h1>
<p class="aide">Pour chaque numéro : <b>①</b> prenez l'image envoyée à part dont le nom contient ce numéro, <b>②</b> copiez la demande, puis dans Gemini joignez l'image et collez la demande.
Ensuite, renvoyez les images en disant leur numéro (exemple : « 1, 2, 4 » dans l'ordre des images envoyées).</p>
{''.join(cartes)}
<script>document.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>{{const t=document.getElementById(b.dataset.c).textContent;
const ok=()=>{{const o=b.textContent;b.textContent='Copié ✓';setTimeout(()=>b.textContent=o,1500)}};try{{navigator.clipboard.writeText(t).then(ok,()=>prompt('Copiez :',t))}}catch(e){{prompt('Copiez :',t)}}}});</script>
</body></html>'''
    open(os.path.join(out, 'fiche_gemini.html'), 'w', encoding='utf-8').write(page)
    # les images à joindre, en fichiers séparés (l'aperçu des pages dans l'application Claude ne permet pas de les enregistrer)
    import collections; g = collections.OrderedDict(); d = os.path.join(out, 'a_joindre'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for x in items:
        if not x.get('suite_de'): g.setdefault(x['fichier_ref'], []).append(x['n'])
    for f, ns in g.items(): shutil.copy(os.path.join(out, 'references', f), os.path.join(d, 'image_pour_n' + '-'.join(map(str, ns)) + '.jpg'))
    json.dump(items, open(os.path.join(out, 'fiche_gemini.json'), 'w'), ensure_ascii=False, indent=1)
    log(f'fiche Gemini : {len(items)} image(s) à générer → fiche_gemini.html'); return items

def importer(pairs, out, log=print):
    """Images renvoyées par Issa : {numéro: fichier}. Poses et personnages détourés → catalogue ; décors → assets/decors."""
    import poses_ia
    items = {x['n']: x for x in json.load(open(os.path.join(out, 'fiche_gemini.json'), encoding='utf-8'))}
    cat = json.load(open(f'{A}/catalog.json')); faits = []
    for n, f in pairs.items():
        x = items.get(int(n))
        if not x: log(f'numéro {n} inconnu dans la fiche, ignoré'); continue
        im = Image.open(f)
        if x['type'] == 'decor':
            im = im.convert('RGB'); s = max(1080 / im.width, 1920 / im.height, 1); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            im.save(f'{A}/decors/{x["perso"]}.jpg', quality=92); faits.append(x['perso']); log(f"décor rangé : {x['perso']}"); continue
        im = poses_ia.detourer(im)
        if x['type'] == 'objet':   # nouvel objet : gros plan « PLAN: objet … »
            mots = [w for w in re.sub(r'[^a-z0-9 ]', ' ', script.norm(x['perso'])).split() if len(w) > 2 and w not in ('les', 'des', 'une', 'pour', 'avec')]
            k = 'obj_' + '_'.join(mots[:3]); i = 2
            while k in cat['poses']: k = f"obj_{'_'.join(mots[:3])}{i}"; i += 1
            im.save(f'{A}/poses/{k}.webp', quality=92)
            cat['poses'][k] = {'char': 'OBJET', 'frame': 'objet', 'posture': 'objet', 'tags': mots, 'mouth': False, 'size': list(im.size), 'props': [], 'genere': 'gemini'}
            faits.append(k); log(f'objet rangé : {k}'); continue
        c = x['perso']; emo = x.get('emo', ''); slug = emo[5:] if emo.startswith('pose:') else emo
        pre = poses_ia.prefixe(c) if c in director.HEIGHT else c.lower()[:4]
        parts = [pre] + ([x['tenue']] if x.get('tenue') else []) + ([x['posture']] if x.get('posture', 'debout') != 'debout' else []) + ([slug] if slug else [])
        base = '_'.join(parts) if len(parts) > 1 else f'{pre}_debout'
        k = base; i = 2
        while k in cat['poses']: k = f'{base}{i}'; i += 1
        im.save(f'{A}/poses/{k}.webp', quality=92)
        post = x.get('posture', 'debout')
        tags = ['dos'] if post == 'dos' else ([emo] + slug.split('_') if emo.startswith('pose:') else [emo] if emo else ['neutre', 'ecoute']) + (['assis'] if post == 'assis' else [])
        cat['poses'][k] = {'char': c, 'frame': 'pied', 'posture': post, 'tags': tags, 'mouth': False, 'size': list(im.size),
                           'head_x': poses_ia.tete_x(im), 'props': [], 'genere': 'gemini', 'depart': x.get('ref')}
        if x.get('tenue'): cat['poses'][k]['tenue'] = x['tenue']
        if c not in cat['height']: cat['height'][c] = 1.0 if c not in FEMMES else 0.92
        faits.append(k); log(f'rangée : {k} ({titre(x)})')
    json.dump(cat, open(f'{A}/catalog.json', 'w'), ensure_ascii=False, indent=1); director.reload()
    return faits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('scripts', nargs='*'); ap.add_argument('-o', '--out', default='sortie_gemini')
    ap.add_argument('--importer', default=None, help='ex. "1=image_a.png 2=image_b.jpg"')
    ap.add_argument('--tout', action='store_true', help='aussi les émotions demandées une seule fois'); a = ap.parse_args()
    if a.importer:
        importer({n: f for n, f in re.findall(r'(\d+)\s*=\s*(\S+)', a.importer)}, a.out); return
    fiche(besoins(a.scripts, tout=a.tout), a.out)
if __name__ == '__main__': main()
