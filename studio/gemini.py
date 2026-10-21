"""Fiche Gemini : l'application lit les scripts, trouve les images qui manquent (poses, vues de dos, poses assises, nouveaux
personnages, nouveaux décors) et prépare pour chacune l'image de référence + la demande prête à coller dans Gemini (gratuit).
Issa génère les images dans Gemini et les renvoie ; l'application les détoure et les range elle-même.

1. python -m studio.gemini exemples/episode16.txt exemples/episode17.txt -o sortie_gemini
      → sortie_gemini/fiche_gemini.html (téléphone) + fiche_gemini.json + references/
2. python -m studio.gemini -o sortie_gemini --importer "1=image_a.png 2=image_b.jpg"
      → images rangées (poses dans le catalogue, décors dans assets/decors)"""
import os, sys, io, re, json, base64, html, argparse, shutil
import numpy as np
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
IDENTITE = {   # fiche d'identité de chaque personnage (tenue habituelle, physique) : écrite entre parenthèses dans chaque demande Gemini
    'BAKARY': "jeune homme mince, grand boubou en bazin bleu roi avec broderie dorée et beige sur la poitrine, pantalon bleu assorti, lunettes de soleil bleues posées sur la tête, petite barbiche, montre noire, sandales marron",
    'AWA': "jeune femme élégante, tresses relevées en chignon avec perles dorées, robe moulante en pagne vert, orange et jaune à grands motifs, créoles dorées, bracelets dorés, escarpins verts",
    'MODIBO': "jeune homme costaud, chemise ouverte en pagne orange et marron sur un débardeur blanc, jean bleu, casquette rouge portée à l'envers, baskets orange et blanc, montre en cuir",
    'DIASABI': "homme très grand et très mince, long cou, cheveux très courts, grosses lèvres, chemise à carreaux verts aux manches retroussées, pantalon gris retroussé aux chevilles, sandales",
    'KARIM': "homme au crâne rasé, barbe courte bien taillée, costume bleu marine avec pochette blanche, chemise blanche col ouvert, montre dorée, chaussures noires",
    'FATIM': "jeune femme, grand foulard rose fuchsia noué sur la tête, longues tresses, robe en pagne rose et blanc à motifs, bracelets de perles, boucles d'oreilles dorées, sandales",
    'MIMI': "jeune apprentie couturière mince, tresses en queue de cheval avec un élastique jaune, robe en pagne jaune-kaki à petits motifs ronds, mètre ruban jaune autour du cou, sandales dorées",
    'MOUSSA': "jeune homme mince, petites dreadlocks courtes, t-shirt blanc ample, casque audio noir autour du cou, jean bleu clair, baskets blanches ; debout sur le sol, sans hoverboard",
    'SEYDOU': "livreur souriant, casquette verte, polo vert, pantalon beige, baskets grises",
    'KADI': "femme âgée, lunettes, foulard bordeaux sur la tête, grand boubou bordeaux brodé d'or, canne en bois",
    'SALI': "jeune femme, foulard jaune noué sur la tête, robe en pagne bleu à motifs orange et bordure dorée, sandales",
}
def ident(c): return f"{gfx.nom(c)} ({IDENTITE[c]})" if c in IDENTITE else gfx.nom(c)
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
    st = st.replace("que sur l'image jointe", "que sur l'image jointe, " + ident(x['perso']), 1)
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

PAR_IMAGE = 4   # Gemini fait jusqu'à 4 personnages par image (au-delà la qualité baisse)
def pose_phrase(x):
    """La pose demandée, en quelques mots (pour la liste « 1) … 2) … » d'une image groupée)."""
    f = x['perso'] in FEMMES
    if x['posture'] == 'dos': return ('vue' if f else 'vu') + ' de dos, debout, bras le long du corps, visage caché'
    if x['posture'] == 'assis': return ('assise' if f else 'assis') + ' sur un petit banc en bois, de trois-quarts, mains sur les genoux' + (', ' + desc(x['emo'], f) if x['emo'] else ', bouche fermée')
    return 'debout, de trois-quarts, ' + (desc(x['emo'], f) if x['emo'] else "calme, l'air neutre") + ', bouche fermée'
def groupes(items):
    """Les images de la fiche regroupées par image à joindre (même personnage, même tenue), 4 au plus par génération."""
    import collections
    g = collections.OrderedDict()
    for x in items:
        key = (x['perso'], x.get('tenue', '')) if x['type'] == 'pose' else ('seul', x['n'])   # une seule image de référence par personnage et par tenue
        g.setdefault(key, []).append(x)
    out = []; premier = {}
    for key, xs in g.items():
        for c in range(0, len(xs), PAR_IMAGE):
            grp = {'g': len(out) + 1, 'items': [x['n'] for x in xs[c:c + PAR_IMAGE]], 'fichier_ref': xs[0]['fichier_ref']}
            x0 = xs[0]
            if x0.get('tenue') and not director.POSES.get(x0.get('ref') or '', {}).get('tenue'):   # nouvelle tenue : la 1re image sert de modèle aux suivantes
                if (x0['perso'], x0['tenue']) in premier: grp['suite_de'] = premier[(x0['perso'], x0['tenue'])]
                else: premier[(x0['perso'], x0['tenue'])] = grp['g']
            out.append(grp)
    return out
def demande_groupe(grp, items):
    xs = [items[n] for n in grp['items']]; x0 = xs[0]
    if len(xs) == 1 and x0['type'] != 'pose': return demande(x0)
    f = x0['perso'] in FEMMES
    if x0.get('tenue') and not grp.get('suite_de') and not director.POSES.get(x0.get('ref') or '', {}).get('tenue'):
        tete = ("Garde exactement le même personnage que sur l'image jointe : même visage, même coiffure, même corpulence, même style dessin animé 3D, mais "
                + ('habillée' if f else 'habillé') + ' de : ' + TENUES.get((x0['perso'], x0['tenue']), (x0['tenue'], x0['tenue'].replace('_', ' ')))[1] + '. ')
    else: tete = STYLE
    if not (x0.get('tenue') and not grp.get('suite_de')): tete = tete.replace("que sur l'image jointe", "que sur l'image jointe, " + ident(x0['perso']), 1)
    rp = director.POSES.get(x0.get('ref') or '', {}); objet = set(rp.get('props', [])) | (set(rp.get('tags', [])) & director.OBJ)
    rien = (('Elle' if f else 'Il') + ' ne tient rien dans les mains. ') if objet else ''
    if len(xs) == 1: return tete + 'Montre-' + ('la ' if f else 'le ') + pose_phrase(x0) + '. ' + rien + FOND
    liste = ' ; '.join(f'{i}) {pose_phrase(x)}' for i, x in enumerate(xs, 1))
    return (tete + rien + f"Fais UNE seule image en format paysage qui montre ce personnage {len(xs)} fois, côte à côte sur une seule rangée, "
            "chacun en corps entier de la tête aux pieds, tous à la même taille, bien séparés les uns des autres (un espace vide entre eux), "
            "sur un fond gris clair uni, sans décor ni autre personnage, sans texte ni numéro. De gauche à droite : " + liste + '.')
CSS = """:root{--fond:#f6f3ee;--carte:#fff;--texte:#222;--doux:#666;--accent:#e8731a;--bord:#ddd}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}}
:root[data-theme="dark"]{--fond:#17150f;--carte:#24211b;--texte:#eee;--doux:#aaa;--bord:#3a352c}
*{box-sizing:border-box}body{margin:0;background:var(--fond);color:var(--texte);font:16px/1.45 system-ui,sans-serif;padding:12px;overflow-x:hidden}
h1{font-size:20px;margin:4px 0}.aide{color:var(--doux);font-size:14px;margin:0 0 12px}.aide b{color:var(--texte)}
section{background:var(--carte);border:1px solid var(--bord);border-radius:12px;padding:10px;margin:0 0 14px}
h2{font-size:16px;margin:0 0 2px;display:flex;gap:8px;align-items:center}.n{flex:none;width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px}
ul{margin:4px 0 8px;padding-left:20px;font-size:13px;color:var(--doux)}.ligne{display:flex;gap:10px;align-items:flex-start}
.ref{flex:0 0 28%}.ref img{width:100%;border-radius:8px;display:block}
.dem{flex:1;min-width:0}.note{margin:0 0 6px;font-size:13px;font-weight:700;color:var(--accent)}.txt{margin:0 0 8px;font-size:13px;background:var(--fond);border-radius:8px;padding:8px;word-wrap:break-word}
button{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:9px 10px;font-weight:700;font-size:14px;width:100%}"""
JS = """document.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>{const t=document.getElementById(b.dataset.c).textContent;
const ok=()=>{const o=b.textContent;b.textContent='Copié ✓';setTimeout(()=>b.textContent=o,1500)};try{navigator.clipboard.writeText(t).then(ok,()=>prompt('Copiez :',t))}catch(e){prompt('Copiez :',t)}});"""
def fiche(items, out, log=print):
    os.makedirs(out, exist_ok=True); cartes = []
    for x in items:
        kind, k = ref_pour(x); x['ref'] = k if kind == 'pose' else None
        f = image_ref(kind, k, out); x['fichier_ref'] = os.path.basename(f)
    par_n = {x['n']: x for x in items}; gs = groupes(items)
    d = os.path.join(out, 'a_joindre'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for grp in gs:
        grp['demande'] = demande_groupe(grp, par_n); xs = [par_n[n] for n in grp['items']]; g = grp['g']
        if not grp.get('suite_de'): shutil.copy(os.path.join(out, 'references', grp['fichier_ref']), os.path.join(d, f'image_{g}.jpg'))
        th = Image.open(os.path.join(out, 'references', grp['fichier_ref'])); th.thumbnail((420, 640)); b = io.BytesIO(); th.save(b, 'JPEG', quality=82)
        quoi = ''.join('<li>' + html.escape(titre(x)) + '</li>' for x in xs)
        ref = ('<p class="note">① Joignez l\'image obtenue au n° %d (même tenue).</p>' % grp['suite_de']) if grp.get('suite_de') else ('<p class="note">① Joignez le fichier « image_%d ».</p>' % g)
        cartes.append('<section><h2><span class="n">%d</span>%d image%s en une seule demande</h2><ul>%s</ul>' % (g, len(xs), 's' if len(xs) > 1 else '', quoi)
                      + '<div class="ligne"><div class="ref"><img src="data:image/jpeg;base64,%s" alt="image à joindre"></div>' % base64.b64encode(b.getvalue()).decode()
                      + '<div class="dem">%s<p class="txt" id="d%d">%s</p><button data-c="d%d">② Copier la demande</button></div></div></section>' % (ref, g, html.escape(grp['demande']), g))
    page = ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fiche Gemini</title><style>'
            + CSS + '</style></head><body><h1>Fiche Gemini — %d demande(s), %d image(s)</h1>' % (len(gs), len(items))
            + '<p class="aide">Pour chaque numéro : <b>①</b> joignez dans Gemini le fichier indiqué (envoyé à part), <b>②</b> copiez la demande et collez-la. '
            'Gemini fait plusieurs personnages sur une seule image : l\'application les découpe elle-même. Renvoyez chaque image en disant son numéro.</p>'
            + ''.join(cartes) + '<script>' + JS + '</script></body></html>')
    open(os.path.join(out, 'fiche_gemini.html'), 'w', encoding='utf-8').write(page)
    json.dump({'items': items, 'groupes': gs}, open(os.path.join(out, 'fiche_gemini.json'), 'w'), ensure_ascii=False, indent=1)
    log(f'fiche Gemini : {len(gs)} demande(s) pour {len(items)} image(s) → fiche_gemini.html'); return items

def decouper(im, k):
    """Image Gemini avec k personnages côte à côte → k images (de gauche à droite), chacune avec une marge de fond."""
    from rembg import remove, new_session
    from scipy import ndimage
    im = im.convert('RGB')
    if k == 1: return [im]
    m = np.asarray(remove(im, session=new_session('isnet-general-use'), only_mask=True, post_process_mask=True)) > 60
    lab, n = ndimage.label(ndimage.binary_closing(m, iterations=6))
    objs = sorted([(int((lab[sl] == i).sum()), sl) for i, sl in enumerate(ndimage.find_objects(lab), 1) if sl is not None], key=lambda t: -t[0])
    big = [sl for a, sl in objs[:k] if a > 0.15 * objs[0][0]] if objs else []
    if len(big) != k:   # personnages qui se touchent : découpe en bandes égales
        w = im.width // k; return [im.crop((i * w, 0, (i + 1) * w, im.height)) for i in range(k)]
    out = []
    for sl in sorted(big, key=lambda s: s[1].start):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop; mx = int((x1 - x0) * 0.08) + 6; my = int((y1 - y0) * 0.04) + 6
        out.append(im.crop((max(0, x0 - mx), max(0, y0 - my), min(im.width, x1 + mx), min(im.height, y1 + my))))
    return out

def importer(pairs, out, log=print):
    """Images renvoyées par Issa : {numéro: fichier}. Poses et personnages détourés → catalogue ; décors → assets/decors."""
    import poses_ia
    data = json.load(open(os.path.join(out, 'fiche_gemini.json'), encoding='utf-8'))
    items = {x['n']: x for x in data['items']}; gs = {g['g']: g for g in data['groupes']}
    cat = json.load(open(f'{A}/catalog.json')); faits = []; travail = []
    for n, f in pairs.items():   # numéro de demande → image Gemini, découpée en autant de personnages que demandés
        g = gs.get(int(n))
        if not g: log(f'numéro {n} inconnu dans la fiche, ignoré'); continue
        morceaux = decouper(Image.open(f), len(g['items']))
        travail += list(zip([items[i] for i in g['items']], morceaux))
    for x, im in travail:
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
