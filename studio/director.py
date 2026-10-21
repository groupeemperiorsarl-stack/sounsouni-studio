"""Réalisateur automatique : transforme les événements du script (+ durées des voix) en liste de plans.
Règles apprises sur les épisodes 12-14 :
 - un seul sol par plan d'ensemble, profondeur (arrière-plan plus petit), personne ne flotte ;
 - chaque personnage garde sa place dans la scène ; en gros plan, il est décalé du côté opposé à celui qu'il regarde ;
 - gros plans cadrés tête-buste (la bouche se voit) ;
 - le lieu du plan est toujours le décor de la scène en cours ;
 - réactions sur un mot = plan de coupe pendant que la voix continue ;
 - marche : cycle de pas quand il existe, déplacement en ligne droite."""
import json, os, re, copy
from script import norm
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
CAT = json.load(open(A + '/catalog.json'))
POSES = CAT['poses']; HEIGHT = CAT['height']
def reload():
    POSES.clear(); POSES.update(json.load(open(A + '/catalog.json'))['poses'])
GROUND, BACK = 1900, 1560
EMOS = {'neutre', 'sourire', 'grand_sourire', 'sourire_malin', 'rire', 'rire_retenu', 'colere', 'furieux', 'choc', 'surpris', 'peur', 'panique', 'triste',
        'gene', 'mepris', 'mefiant', 'yeux_plisses', 'amoureux', 'fier', 'moue', 'degout', 'innocent', 'taquin', 'pensif', 'serieux', 'inquiet', 'tendre',
        'moqueur', 'froide', 'hesitante', 'chaleureuse', 'joie', 'content', 'severe', 'emu', 'confus', 'determine', 'fiere', 'sage', 'victoire',
        'emerveille', 'timide', 'reveur'}
SYN = {'grand_sourire': 'sourire content', 'sourire_malin': 'taquin sourire', 'rire_retenu': 'rire', 'furieux': 'colere furieux', 'yeux_plisses': 'mefiant mepris',
       'peur': 'peur panique', 'panique': 'panique peur', 'surpris': 'surpris choc', 'froide': 'mepris colere froide', 'moqueur': 'moqueur taquin rire',
       'hesitante': 'pensif moue', 'innocent': 'sourire', 'emu': 'emu amoureux', 'tendre': 'tendre sourire', 'inquiet': 'inquiet triste', 'pleure': 'pleure triste larmes', 'triste': 'triste',
       'chaleureuse': 'sourire', 'severe': 'severe colere', 'serieux': 'serieux neutre', 'joie': 'joie content rire',
       # mots utilisés par le scénariste, ramenés aux émotions connues
       'confus': 'gene confus', 'determine': 'serieux fier', 'determinee': 'serieux fier', 'fiere': 'fier', 'sage': 'serieux neutre', 'victoire': 'joie victoire',
       'emerveille': 'surpris amoureux', 'emerveillee': 'surpris amoureux', 'timide': 'gene timide', 'reveur': 'amoureux reveur', 'reveuse': 'amoureux reveur',
       'sert': 'verse the', 'contente': 'content', 'surprise': 'surpris', 'inquiete': 'inquiet', 'furieuse': 'furieux', 'amoureuse': 'amoureux'}
BODY = {'recule', 'avance', 'sursaut', 'tremble', 'hoche_tete', 'secoue_tete', 'penche_tete', 'se_penche', 's_affale', 'bombe_torse', 'soupir', 'tourne_vers', 'detourne_regard', 'regarde_bas', 'leve_yeux_ciel', 'cligne', 'clin_oeil', 'ferme_yeux'}
FX = {'coeurs', 'etoiles', 'eclair', 'fumee_tete', 'goutte', 'sueur', 'point_exclamation', 'point_interrogation', 'rougit', 'idee', 'ampoule'}
SFX = {'sonnerie': 'call', 'telephone': 'call', 'bip': 'bip', 'clic': 'click', 'notification': 'ding', 'pieces': 'coin', 'porte': 'door', 'porte qui claque': 'door',
       'pas': 'steps', 'talons': 'heels', 'tonnerre': 'thunder', 'grillon': 'cricket', 'grillons': 'cricket', 'whoosh': 'whoosh', 'pop': 'pop', 'fracas': 'crack',
       'gresillement': 'sizzle', 'rires de foule': 'applause', 'applaudissements': 'applause', 'klaxon': 'klaxon', 'moto': 'motor', 'moteur': 'motor', 'vibreur': 'buzz',
       'vibration': 'buzz', 'canne': 'cane', 'machine a coudre': 'sew', 'ciseaux': 'snip', 'the': 'pourw', 'gorgee': 'sip', 'sifflotement': 'whistlew',
       'scintillement': 'sparkle', 'boum': 'boum', 'bong': 'bong', 'tic-tac': 'tick', 'tic tac': 'tick', 'coeur': 'heart', 'battements de coeur': 'heart', 'bam': 'door', 'cri-cri': 'cricket'}
def sfx_file(name):
    n = norm(name)
    if n in SFX: return SFX[n]
    for k, v in SFX.items():
        if k in n: return v
    return 'pop'
def tagwords(t):
    out = set()
    for w in t:
        out.add(w); out.update(SYN.get(w, '').split())
    return out
POS = {'sourire', 'grand_sourire', 'sourire_malin', 'rire', 'content', 'fier', 'fiere', 'amoureux', 'reveur', 'taquin', 'joie', 'heureux'}
NEG = {'triste', 'pleure', 'peur', 'inquiet', 'panique', 'colere', 'furieux', 'degout', 'choc', 'mepris'}
OBJ = {'telephone', 'brochettes', 'brochette', 'boite', 'cartes', 'carte', 'plateau', 'billet', 'parapluie', 'grill', 'hoverboard', 'robe', 'canne', 'voiture', 'mange', 'verse', 'the', 'verre',
       'bouteilles', 'livre', 'porte', 'gateau', 'rouleau', 'panier', 'beignets', 'louche', 'larmes', 'sale', 'nuit'}
LIGHT = {'verre', 'the', 'porte', 'machine', 'grill', 'nuit'}   # éléments de décor ou de posture : petite pénalité seulement
GESTE = {'pointe', 'mains_tete', 'mains_levees', 'bras_leves', 'supplie', 'non', 'panique', 'bondit', 'doigt', 'salue', 'montre'}
TENUE = {}   # tenue portée en ce moment par chaque personnage ([TENUE AWA: bazin doré]) ; vide = tenue de tous les jours
LASTPICK = {}   # dernier choix de pose : gardé sur l'acteur pour que les planches proposent les autres poses possibles
def pick(char, want=(), frame=None, posture=None, need_mouth=True, avoid_cycle=True, extra_ok=(), must=(), side=False, calm=False):
    t = TENUE.get(char, '')
    r = rank(char, want, frame, posture, need_mouth, avoid_cycle, extra_ok, must, side, calm, t); best = r[0][0] if r else None
    LASTPICK.clear(); LASTPICK.update(key=best, args={'char': char, 'want': list(want), 'frame': frame, 'posture': posture, 'need_mouth': need_mouth, 'avoid_cycle': avoid_cycle, 'extra_ok': list(extra_ok), 'must': list(must), 'side': side, 'calm': calm, 'tenue': t})
    return best
def rank(char, want=(), frame=None, posture=None, need_mouth=True, avoid_cycle=True, extra_ok=(), must=(), side=False, calm=False, tenue=''):
    """must : objets demandés par le PLAN (ex. [Karim, téléphone]) = fortement voulus ; side : préférer une pose de trois-quarts
    (pour se tourner vers l'autre dans les plans à plusieurs). Rend toutes les poses classées : [(clé, note), …], la meilleure d'abord."""
    out = []
    w = tagwords(want)
    for k, p in POSES.items():
        if p['char'] != char or '@' in k: continue   # les têtes tournées sont des variantes, pas des poses à choisir
        tags = set(p['tags'])
        if avoid_cycle and ('cycle_marche' in tags or 'cycle_marche_dos' in tags): continue
        s = 3 * len(w & tags)
        pt = p.get('tenue', '')
        if tenue: s += 14 if pt == tenue else -14   # la tenue du moment d'abord (s'il n'y a aucune image dans cette tenue, la tenue habituelle)
        elif pt: s -= 40   # une tenue spéciale n'apparaît jamais sans [TENUE …] dans le script
        s += 8 * len({x for x in w if x.startswith('pose:')} & tags)   # {POSE: …} demandée par le script
        if frame:
            if p['frame'] == frame: s += 2
            elif frame == 'buste' and p['frame'] == 'pied': s += 1
            elif frame == 'pied' and p['frame'] != 'pied': s -= 6
        if posture:
            if p['posture'] == posture: s += 3
            elif posture in ('assis', 'banc') and p['posture'] in ('assis', 'banc'): s += 2
            elif p['posture'] in ('assis', 'banc', 'dos', 'tombe', 'court', 'marche') and posture != p['posture']: s -= 4
        elif p['posture'] in ('dos', 'tombe', 'court', 'marche') and p['posture'] not in w and not (tags & w & {'tombe', 'glisse', 'court', 'dos', 'marche'}): s -= 5
        props = set(p.get('props', [])) | (tags & OBJ)
        unasked = props - w - set(extra_ok) - set(must)
        s -= 7 * len(unasked - LIGHT) + 1.5 * len(unasked & LIGHT)   # un objet (brochette, téléphone…) ou des larmes jamais montrés sans raison
        s += 6 * len(set(must) & (tags | props))
        if side and face_dir(k) != 0: s += 2.5
        if calm and side and face_dir(k) != 0 and not ((tags & (GESTE | POS | NEG | {'gene', 'rire', 'surpris', 'fatigue', 'sale'})) - w): s += 5   # validé par Issa (pose D) : de trois-quarts, même dessin que la suite de la scène
        if calm:   # personne ne parle encore : attitude tranquille, ni geste ni grande émotion
            if (tags & GESTE) - w: s -= 6
            s -= 2.5 * len((tags & (POS | NEG | {'gene', 'rire', 'surpris', 'fatigue', 'sale'})) - w)
            if tags & {'neutre', 'ecoute', 'serieux'}: s += 3
        # pas de visage à contre-sens : un sourire demandé ne doit jamais donner une pose triste, et l'inverse
        if w & POS and tags & NEG and not (w & NEG): s -= 6
        if w & NEG and tags & POS and not (w & POS): s -= 4
        if need_mouth and p['mouth']: s += 1.5
        if 'neutre' in tags and not w: s += 1
        if not w and tags & NEG: s -= 3   # sans émotion demandée : jamais un visage fâché ou triste
        out.append((k, s))
    return sorted(out, key=lambda x: -x[1])   # à égalité, la première du catalogue (comme avant)
def pick_args(k):
    return dict(LASTPICK['args']) if LASTPICK.get('key') == k and k else None
def group_pick(chars, want):
    w = tagwords(want); cs = set(chars)
    for k, p in POSES.items():
        if '+' in p['char'] and set(p['char'].split('+')) == cs and (w & set(p['tags'])): return k
    return None
def posture_of(pose_text):
    t = norm(pose_text or '')
    if 'banc' in t: return 'banc'
    if 'assis' in t or 'machine' in t or 'chaise' in t or 'coud' in t: return 'assis'
    if 'marche' in t and 'dos' in t: return 'dos_marche'
    if 'marche' in t: return 'marche'
    if 'court' in t: return 'court'
    if 'dos' in t: return 'dos'
    if 'grill' in t: return 'grill'
    return 'debout'
class Stage:
    def __init__(self): self.order = []; self.posture = {}; self.props = {}; self.arrivals = set(); self.entering = set(); self.seq = []   # seq : arrivées déjà faites, dans l'ordre
    def set(self, who_list):
        for w in who_list:
            if w['who'] not in self.order: self.order.append(w['who'])
            if w.get('pose'):
                self.posture[w['who']] = posture_of(w['pose'])
                pw = norm(w['pose']); self.props[w['who']] = [x for x in sorted(OBJ | {'machine'}) if x in pw]
    def add(self, who):
        if who and who not in self.order and who in HEIGHT: self.order.append(who)
    def post(self, who):
        p = self.posture.get(who) or 'debout'; return 'debout' if p in ('grill', 'marche', 'dos_marche') else p
    def pan(self, who):
        if who not in self.order or len(self.order) < 2: return 0.0
        return round((self.order.index(who) / (len(self.order) - 1)) * 2 - 1, 2)
    def side(self, who, target):
        if who in self.order and target in self.order: return 1 if self.order.index(target) > self.order.index(who) else -1
        return 0
def depth_staging(acts, speaker=None, arrivals=()):
    """Groupe de 4 et plus avec des gens assis : on ne les aligne plus. Les assis au milieu, un peu en retrait ;
    ceux qui sont debout sur les côtés, devant, tournés vers le centre : un cercle de discussion avec de la profondeur."""
    if len(acts) < 4 or any(a.get('walk') or a.get('leave') for a in acts): return acts
    sit = [a for a in acts if POSES[a['key']]['posture'] in ('assis', 'banc')]; std = [a for a in acts if a not in sit]
    if not sit or not std: return acts
    for a in sit:
        a['h'] = int(1050 * 0.86 * HEIGHT.get(a['who'], 1)); a['w'] = POSES[a['key']]['size'][0] * a['h'] / POSES[a['key']]['size'][1]; a['by'] = GROUND - 150
    tot = sum(a['w'] for a in sit); f = max(0.82, min(1.0, 900 / max(1, tot)))   # les bancs peuvent se toucher, mais les gens gardent leur taille
    step = 0.72   # chevauchement des bancs
    span = sum(a['w'] * f for a in sit) * step + (sit[-1]['w'] * f) * (1 - step) if sit else 0
    x = 540 - span / 2
    for a in sit:
        a['h'] = int(a['h'] * f); a['w'] *= f; a['x'] = int(x + a['w'] / 2); x += a['w'] * step
    # à gauche le premier (le héros de la scène) ; à droite, en face de lui, celui qui arrive / parle ; les autres derrière les assis
    rest = sorted(std[1:], key=lambda a: (not a.get('enter'), a['who'] not in arrivals, a['who'] != speaker))
    left, right, behind = [std[0]], rest[:1], rest[1:]
    if arrivals and right and right[0]['who'] not in arrivals:   # quelqu'un va arriver : sa place en face reste libre, chacun garde la sienne
        behind = rest; right = []
    for side, grp in ((-1, left), (1, right)):
        for a in grp:
            a['h'] = int(1080 * HEIGHT.get(a['who'], 1)); a['w'] = POSES[a['key']]['size'][0] * a['h'] / POSES[a['key']]['size'][1]
            a['by'] = GROUND + 40; x = 540 + side * 360
            a['x'] = int(min(max(x, a['w'] * 0.42 + 5), 1075 - a['w'] * 0.42))   # jamais coupé par le bord
    for i, a in enumerate(behind):   # debout derrière le banc, plus loin
        a['h'] = int(780 * HEIGHT.get(a['who'], 1)); a['w'] = POSES[a['key']]['size'][0] * a['h'] / POSES[a['key']]['size'][1]
        a['by'] = GROUND - 190; a['x'] = int(540 + (i - (len(behind) - 1) / 2) * 260 + (60 if i % 2 else -60))
    sit = behind + sit
    return sit + [a for a in std if a not in behind]
RANGS = {'devant': {'x': (0.25, 0.73), 'pieds': 0.945, 'h': 1080}, 'derriere': {'x': (0.5, 0.1, 0.9, 0.3, 0.7), 'pieds': 0.745, 'h': 900}}
def deux_rangees(acts, stage, speaker=None, partner=None):
    """Plan d'ensemble à 4 personnes et plus, d'après la scène modèle (Gemini, épisode 16) : devant, les deux qui se parlent,
    grands et face à face ; derrière, les autres, plus petits, placés dans les espaces libres pour que tous les visages se voient."""
    assis = lambda a: POSES[a['key']]['posture'] in ('assis', 'banc')
    rang = lambda c: stage.order.index(c) if c in stage.order else 99
    std = [a['who'] for a in acts]; late = stage.seq[-1] if stage.seq else None   # assis aussi : celle à qui l'on parle vient devant, tabouret au sol
    pair = []
    for c in (speaker, partner, late) + tuple(sorted(std, key=rang)):
        if c and c in std and c not in pair: pair.append(c)
        if len(pair) == 2: break
    pair.sort(key=rang)   # le héros de la scène (premier nommé) à gauche
    D, R = RANGS['devant'], RANGS['derriere']; out_front, out_back = [], []
    def poser(a, x, h, pieds):
        p = POSES[a['key']]; h = int(h * (0.86 if assis(a) else 1.0) * (1.0 if p['frame'] == 'pied' else 0.8))
        a['h'] = h; a['w'] = p['size'][0] * h / p['size'][1]; a['by'] = int(pieds * 1920)
        a['x'] = int(min(max(x * 1080, a['w'] * 0.42 + 5), 1075 - a['w'] * 0.42))   # jamais coupé par le bord
    for a in acts:
        if a['who'] in pair: poser(a, D['x'][pair.index(a['who'])], D['h'] * HEIGHT.get(a['who'], 1), D['pieds']); out_front.append(a)
    reste = sorted([a for a in acts if a['who'] not in pair], key=lambda a: (not assis(a), rang(a['who'])))
    slots = list(R['x'][:len(reste)])
    if reste and assis(reste[0]): poser(reste[0], slots.pop(0), R['h'] * HEIGHT.get(reste[0]['who'], 1), R['pieds']); out_back.append(reste.pop(0))
    for a, x in zip(sorted(reste, key=lambda a: rang(a['who'])), sorted(slots)):   # de gauche à droite dans l'ordre de la scène
        poser(a, x, R['h'] * HEIGHT.get(a['who'], 1), R['pieds']); out_back.append(a)
    return out_back + out_front
def wide_layout(stage, chars, moods, speaker=None, partner=None):
    """Plan d'ensemble : tout le monde sur le même sol, côte à côte sans se chevaucher, arrière-plan plus petit."""
    chars = [c for c in chars if c in HEIGHT]; acts = []
    prio = sorted(chars, key=lambda c: (c != speaker, stage.posture.get(c) != 'marche', chars.index(c)))
    keep = set(prio[:6]); front = [c for c in chars if c in keep]; back = [c for c in chars if c not in keep]
    # celui qui arrive et s'adresse au groupe : au premier plan, DE DOS, face au groupe (validé par Issa)
    has_back = lambda c: any(p['char'] == c and p['posture'] == 'dos' and 'cycle' not in ' '.join(p['tags']) for p in POSES.values())
    rangs = len(front) >= 4 and not any(stage.posture.get(c) in ('marche', 'dos_marche') for c in front)   # groupe : deux rangées (scène modèle validée par Issa)
    fgc = [c for c in front if c in stage.arrivals and stage.posture.get(c) not in ('marche', 'dos_marche') and has_back(c)]
    late = stage.seq[-1] if stage.seq else None   # celui qui arrive, c'est le dernier arrivé (pas un ancien arrivant de la scène)
    fgc = [c for c in fgc if c == speaker or (speaker is None and c == late)][:1] if len(front) >= 3 and not rangs else []
    front = [c for c in front if c not in fgc]
    for c in front:
        post = stage.posture.get(c, 'debout'); pst = 'debout' if post == 'grill' else post
        want = list(moods.get(c, [])) + (['grill'] if post == 'grill' else []) + stage.props.get(c, [])
        walk = post in ('marche', 'dos_marche') and c == 'AWA' and not TENUE.get(c)   # pas d'images de marche dans une tenue spéciale : elle entre simplement
        k = ('awa_dos_pas1' if post == 'dos_marche' else 'awa_pas1') if walk else (pick(c, want, 'pied', pst, need_mouth=(c == speaker), must=stage.props.get(c, []), side=len(chars) > 1, calm=speaker is None or (c == speaker and not moods.get(c))) or pick(c, want, None, None))
        sit = POSES[k]['posture'] in ('assis', 'banc')
        base = {1: 1450, 2: 1320, 3: 1150, 4: 1060, 5: 980}.get(len(front), 920)   # moins il y a de monde, plus on est près
        h = int(base * (0.8 if sit else 1.0) * HEIGHT.get(c, 1)) if POSES[k]['frame'] == 'pied' else int(base * 0.83)
        w = POSES[k]['size'][0] * h / POSES[k]['size'][1]
        act = {'key': k, 'who': c, 'h': h, 'w': w, 'by': GROUND + (0 if sit else 15), 'walk': ('AWA_dos' if post == 'dos_marche' else 'AWA') if walk else None}
        if not walk and pick_args(k): act['pick'] = pick_args(k)
        if c in stage.entering and not walk and not sit: act['enter'] = True; stage.entering.discard(c)   # il arrive : on le voit entrer
        if walk and post == 'dos_marche': act['leave'] = True   # elle s'en va : de dos, elle sort du cadre
        elif walk:   # elle entre en marchant puis s'arrête à sa place, avec une pose qui parle
            act['stop_key'] = pick(c, list(moods.get(c, [])), 'pied', 'debout', need_mouth=True) or pick(c, [], 'pied', None)
            stage.posture[c] = 'debout'
        acts.append(act)
    tot = sum(a['w'] for a in acts) + 30 * max(0, len(acts) - 1); avail = 1040
    if tot > avail:
        f = max(0.58, avail / tot)
        for a in acts: a['h'] = int(a['h'] * f); a['w'] *= f
        tot = sum(a['w'] for a in acts) + 30 * max(0, len(acts) - 1)
    gap = 30 if len(acts) < 2 else 30 + max(0, (avail - tot)) / (len(acts) - 1) * 0.6
    tot2 = sum(a['w'] for a in acts) + gap * max(0, len(acts) - 1); x = 540 - tot2 / 2
    if tot2 > 1080: gap -= (tot2 - 1060) / max(1, len(acts) - 1); tot2 = 1060; x = 10
    for a in acts:
        a['x'] = int(x + a['w'] / 2); x += a['w'] + gap
        if a.get('leave'):
            a['vx'] = 230 if a['x'] > 540 else -230; a['flip'] = a['vx'] < 0; a['walk_t'] = 1e9
        elif a.get('walk'):
            # les images de marche regardent vers la droite : venir de la gauche = image normale, venir de la droite = image retournée
            from_right = a['x'] > 540
            a['vx'] = -260 if from_right else 260; a['flip'] = from_right; a['walk_t'] = 1.8
    acts = deux_rangees(acts, stage, speaker, partner) if rangs else depth_staging(acts, speaker, stage.arrivals)
    for i, c in enumerate(back):
        k = pick(c, moods.get(c, []), 'pied', stage.posture.get(c)); acts.insert(0, {'key': k, 'who': c, 'x': int(160 + i * 260), 'by': BACK, 'h': int(600 * HEIGHT.get(c, 1)), 'back': True})
    for c in fgc:
        backs = sorted([k for k, p in POSES.items() if p['char'] == c and p['posture'] == 'dos' and 'cycle' not in ' '.join(p['tags'])], key=lambda k: len(POSES[k].get('props', [])))
        k = backs[0] if backs else pick(c, [], 'pied', 'debout', need_mouth=False)
        h = int(1500 * HEIGHT.get(c, 1)); a = {'key': k, 'who': c, 'h': h, 'by': GROUND + 330, 'x': 820, 'fgwide': True, 'speaker': False}
        if not backs: a['silhouette'] = True; a['fg'] = True   # pas d'image de dos : silhouette sombre
        acts.append(a)
    return acts
def close_actor(char, key, x=540, tight=False, scale=1.0, flip=False):
    p = POSES[key]; fr = p['frame']
    if fr == 'pied': h = 3000 if tight else 2650; by = 330 + h
    elif fr == 'buste': h = 1950 if tight else 1700; by = 300 + h
    elif fr == 'groupe': h = 2300; by = 380 + h
    else: h = 1500; by = 250 + h
    if scale != 1.0: h = int(h * scale); by = int(330 + h) if fr == 'pied' else int(250 + h)
    hx = p.get('head_x', 0.5); hx = 1 - hx if flip else hx
    w = p['size'][0] * h / p['size'][1]; cx = x + (0.5 - hx) * w   # le visage est placé à x
    if fr == 'groupe': cx = x
    d = {'key': key, 'who': char, 'x': int(cx), 'by': by, 'h': h, 'face_x': x, 'tight': tight, 'scale': scale, 'flip': flip}
    if pick_args(key): d['pick'] = pick_args(key)
    return d
def face_dir(key):
    """+1 : le visage regarde vers la droite de l'image, -1 : vers la gauche, 0 : de face (mesuré par LivePortrait)."""
    y = POSES.get(key, {}).get('yaw')
    if y is None or abs(y) < 9: return 0
    return -1 if y > 0 else 1
def yaw_variant(key, turn, eyes=0, up=0):
    """Variante LivePortrait : tête tournée (turn), yeux dirigés (eyes) vers la droite (+1) / gauche (-1) de l'image d'origine,
    et regard vers le haut (up=+1) ou le bas (up=-1) quand l'autre est plus grand / plus bas (debout face à assis)."""
    sg = lambda v: '+' if v > 0 else ('-' if v < 0 else '0')
    v = f'{key}@{sg(turn)}{sg(eyes)}{sg(up)}'
    if v not in POSES: POSES[v] = dict(POSES[key], yaw=(-24.0 * turn) if turn else POSES[key].get('yaw', 0), variant_of=key, turn=turn, eyes=eyes, up=up)
    return v
def parse_variant(v):
    base, t = v.split('@'); m = {'+': 1, '-': -1, '0': 0}
    return base, m[t[0]], (m[t[1]] if len(t) > 1 else 0), (m[t[2]] if len(t) > 2 else 0)
def face_y(a):
    fr = {'pied': 0.08, 'buste': 0.2}.get(POSES[a['key'].split('@')[0]]['frame'], 0.15)
    return a['by'] - a['h'] + a['h'] * fr
def orient(a, d, up=0, variant=True):
    """Tourne l'acteur vers l'autre : image retournée si besoin, tête tournée, yeux dirigés vers l'autre
    (à gauche/droite ET en haut/bas selon la hauteur du visage de l'autre)."""
    if not d or a.get('back'): return a
    if a.get('walk'):   # après la marche, la pose d'arrêt regarde aussi le bon côté
        sk = a.get('stop_key')
        if sk:
            sk = sk.split('@')[0]; f = face_dir(sk); fl = f == -d; sd = d if fl else -d
            a['stop_flip'] = fl; a['stop_key'] = yaw_variant(sk, sd, sd, up)
        return a
    base = a['key'].split('@')[0]
    if POSES[base]['char'] == 'OBJET' or '+' in POSES[base]['char'] or POSES[base]['posture'] == 'dos': return a
    a['look_dir'] = d; f = face_dir(base); flip = f == -d
    sd = d if flip else -d   # sens validé à l'œil par Issa (image B du test de regard)
    a['key'] = yaw_variant(base, sd, sd, up) if variant else base
    if 'face_x' in a:
        b = close_actor(a['who'], a['key'], x=a['face_x'], tight=a.get('tight', False), scale=a.get('scale', 1.0), flip=flip)
        a['x'] = b['x']
    a['flip'] = flip
    return a
def orient_shot(sh):
    acts = [a for a in sh.get('actors', []) if not a.get('back') and '+' not in a['who']]
    if sh.get('ots'):   # par-dessus l'épaule : la hauteur du regard vient des postures (assis / debout), pas de l'image
        # validé par Issa (questions 1 et 2 : réponse E) : en champ / contre-champ, image d'origine, seulement retournée vers l'autre
        for a in acts: orient(a, a.get('look_dir') or (1 if a['x'] < 540 else -1), 0, variant=False)
        return
    if len(acts) >= 2:   # plan à plusieurs : on se regarde (celui qui écoute regarde celui qui parle)
        spk = next((a for a in acts if a.get('speaker')), None)
        for a in acts:
            others = [b for b in acts if b is not a]
            tgt = spk if spk is not None and spk is not a else min(others, key=lambda b: abs(b['x'] - a['x']))
            dy = face_y(tgt) - face_y(a); up = 1 if dy < -0.06 * 1920 else (-1 if dy > 0.06 * 1920 else 0)
            orient(a, 1 if tgt['x'] > a['x'] else -1, up)
    elif len(acts) == 1 and acts[0].get('look_dir'):
        orient(acts[0], acts[0]['look_dir'], acts[0].get('look_up', 0))
def updown(stage, who, tgt):
    if not tgt: return 0
    sit = lambda c: stage.post(c) in ('assis', 'banc')
    return 1 if sit(who) and not sit(tgt) else (-1 if sit(tgt) and not sit(who) else 0)
def over_shoulder(who, side, stage):
    """Celui qui écoute, vu de dos ou de trois-quarts, au premier plan sur le bord de l'image (caméra derrière lui)."""
    back = [k for k, p in POSES.items() if p['char'] == who and p['posture'] == 'dos' and 'cycle' not in ' '.join(p['tags']) and not p.get('props')]
    if back: k = back[0]; d = 0
    else: k = pick(who, stage.props.get(who, []), 'buste', stage.post(who), need_mouth=False); d = -side
    a = close_actor(who, k, x=540 + (600 if back else 540) * side, scale=1.4); a['by'] = a['by'] + 420; a['fg'] = True; a['speaker'] = False
    if not back: a['silhouette'] = True   # pas de vue de dos : on montre une silhouette sombre (dos), jamais le visage
    return a
LAUGH = {'rire', 'rire_retenu', 'rit', 'rigole', 'eclate_de_rire', 'moqueur'}
def laughs(actions): return bool(set(actions) & LAUGH)
CHOIX = {}; VARIANTES = False
def cible(e, defaut=None):
    """À qui parle la réplique (« regarde: Bakary »), sinon le dernier qui a parlé."""
    t = e.get('look') and re.sub(r'[^A-Z_]', '', e['look'].upper())
    return t if t in HEIGHT else defaut
def set_pose(a, k):
    """Remplace la pose d'un acteur en gardant sa place (visage au même endroit, pieds au même sol)."""
    a['key'] = k; a['flip'] = False
    if 'face_x' in a:
        b = close_actor(a['who'], k, x=a['face_x'], tight=a.get('tight', False), scale=a.get('scale', 1.0))
        a['by'] = a['by'] - a['h'] + b['h'] if a.get('scale', 1.0) != 1.0 else b['by']; a['h'] = b['h']; a['x'] = b['x']
    else: a['w'] = POSES[k]['size'][0] * a['h'] / POSES[k]['size'][1]
    return a
def apply_pose_choices(shots):
    """Poses choisies par Issa sur les planches : {"12": {"pose": {"who": "BAKARY", "key": "bak_explique"}}}."""
    for idx, ch in CHOIX.items():
        p = ch.get('pose')
        if not p or not str(idx).isdigit() or int(idx) >= len(shots) or p.get('key') not in POSES: continue
        for a in shots[int(idx)].get('actors', []):
            if a['who'] == p['who'] and not (a.get('fg') or a.get('back') or a.get('silhouette') or a.get('walk')): set_pose(a, p['key']); break
def build(meta, events, log=print, choix=None, variantes=False):
    """choix : décisions prises sur les planches (par numéro de plan) ; variantes : garder les autres cadrages possibles (pour les planches)."""
    global VARIANTES
    CHOIX.clear(); CHOIX.update(choix or {}); VARIANTES = variantes; TENUE.clear()
    shots = []; stage = Stage(); scene = {'decor': 'KIOSQUE', 'moment': 'jour', 'ambiance': ''}; plan = None
    present = []; moods = {}; music = 'joyeuse'; ending = False; pending_sfx = []; first_in_scene = True; last_shot = None; last_speaker = None; ots_count = 0
    def add(s):
        nonlocal last_shot
        s.setdefault('decor', scene['decor']); s.setdefault('moment', scene['moment']); s.setdefault('sfx', []); s.setdefault('fx', [])
        s['sfx'] = pending_sfx[:] + s['sfx']; pending_sfx.clear(); s['music'] = music; s['ambiance'] = scene['ambiance']
        shots.append(s); last_shot = s
    first = next((x for x in events if x['type'] == 'scene'), None)
    add({'kind': 'title', 'dur': 2.0, 'title': meta.get('title', ''), 'decor': first['decor'] if first else scene['decor'], 'moment': first.get('moment', 'jour') if first else 'jour'})
    i = 0
    while i < len(events):
        e = events[i]; t = e['type']
        if t == 'scene':
            scene = dict(e); stage = Stage(); plan = None; first_in_scene = True; moods = {}; last_speaker = None
            present = []
            # personnages de la scène : ceux qui parlent avant le prochain décor
            # arrivée annoncée par des pas / talons avant la première réplique : le premier qui parle entre dans le plan
            k2 = i + 1; steps = False
            while k2 < len(events) and events[k2]['type'] not in ('line', 'scene'):
                if events[k2]['type'] == 'sfx' and re.search(r'talons|pas|marche', norm(events[k2]['name'])): steps = True
                k2 += 1
            if steps and k2 < len(events) and events[k2]['type'] == 'line': stage.entering.add(events[k2]['who'])
            j = i + 1; first_plan = True
            while j < len(events) and events[j]['type'] != 'scene':
                if events[j]['type'] == 'plan':
                    if not first_plan: stage.arrivals |= {w['who'] for w in events[j]['who'] if w['who'] not in stage.order}
                    if events[j]['who']: first_plan = False
                    stage.set(events[j]['who'])
                if events[j]['type'] == 'line' and not events[j].get('thought') and 'telephone' not in events[j].get('voice', ''): stage.add(events[j]['who'])
                j += 1
        elif t == 'plan':
            stage.set(e['who']); plan = e
            for w in e['who']:
                if w['who'] in stage.arrivals and w['who'] not in stage.seq: stage.seq.append(w['who'])
            if e['who']: present = [w['who'] for w in e['who']]
            if e.get('dur') or e['kind'] in ('objet', 'ecran'):
                from script import pose_id
                fx = [(0.1, re.sub(r'[{}]', '', x)) for x in re.findall(r'\{[^}]+\}', ' '.join(e.get('extra', [])))]
                fx = [(a, pose_id(b.split(':', 1)[1]) if b.upper().startswith('POSE:') else b) for a, b in fx]
                if e['kind'] in ('objet', 'ecran'):
                    nxt = next((x for x in events[i + 1:] if x['type'] not in ('sfx', 'music')), None)
                    if not (re.search(r't[ée]l[ée]phone|ecran|portable', norm(e.get('object', ''))) and nxt and nxt['type'] == 'screen'):
                        add({'kind': 'insert', 'dur': e.get('dur') or 2.4, 'object': e.get('object', ''), 'fx': fx})
                    plan = None
                elif len(e['who']) > 1 and group_pick([w['who'] for w in e['who']], [x[1] for x in fx]):
                    g = group_pick([w['who'] for w in e['who']], [x[1] for x in fx]); add({'kind': 'close', 'dur': e['dur'], 'actors': [close_actor('+'.join(w['who'] for w in e['who']), g)], 'fx': fx, 'mode': 'close'})
                    plan = {'kind': 'group', 'key': g, 'who': e['who']}; i += 1; continue
                elif e['kind'] == 'large' or len(e['who']) > 1:
                    add({'kind': 'wide', 'dur': e['dur'], 'actors': wide_layout(stage, [w['who'] for w in e['who']] or stage.order, moods), 'fx': fx}); plan = None
                else:
                    c = e['who'][0]['who']; want = [x[1] for x in fx]
                    k = pick(c, want + stage.props.get(c, []), 'buste' if e['kind'] == 'tresgros' else None, stage.post(c))
                    add({'kind': 'close', 'dur': e['dur'], 'actors': [close_actor(c, k, tight=e['kind'] == 'tresgros')], 'fx': fx})
                    plan = None
            elif e['kind'] == 'large':
                add({'kind': 'wide', 'dur': 2.4, 'actors': wide_layout(stage, [w['who'] for w in e['who']] or stage.order, moods), 'establish': True}); first_in_scene = False
        elif t == 'line':
            if first_in_scene and not ending:
                add({'kind': 'wide', 'dur': 2.2, 'actors': wide_layout(stage, stage.order, moods), 'establish': True, 'card': scene['decor']}); first_in_scene = False
            who = e['who']; reacts = []
            j = i + 1
            while j < len(events) and events[j]['type'] in ('reaction', 'sfx'):
                r = events[j]
                reacts.append(r)
                j += 1
            lead = 0.18 if not shots or shots[-1].get('who') == who else 0.35
            dur = lead + e.get('dur', 2) + 0.3
            laugh_line = e.get('emotion') in ('rire', 'rire_retenu') or 'rit' in e.get('voice', '') or any(tg in ('rire', 'rire_retenu') for _, tg in e.get('tags', []))
            if laugh_line: dur += 1.1
            from script import pose_id
            poses_dem = [pose_id(tg.split(':', 1)[1]) for _, tg in e['tags'] if tg.upper().startswith('POSE:')]
            emo = [e.get('emotion', 'neutre')] + [tg for _, tg in e['tags'] if tg in EMOS] + poses_dem
            moods[who] = emo[:1]
            sh = {'kind': 'line', 'who': who, 'line': e, 'lead': lead, 'dur': dur}
            if laugh_line: sh['sfx'] = [(lead + e.get('dur', 2) + 0.05, 'rire:' + who + (':petit' if e.get('emotion') in ('rire_retenu', 'moqueur') else ''), 0.9)]
            if e.get('thought') and last_shot and last_shot['kind'] == 'screen' and who in HEIGHT and not ending:
                # pensée juste après un écran de téléphone : l'écran reste, la tête du personnage pense dans une bulle (demande d'Issa)
                sh['kind'] = 'pensee_ecran'; sh['text'] = last_shot['text']
                sh['tete'] = pick(who, ['pensif'] + emo[:1], 'buste', stage.post(who), need_mouth=False) or pick(who, [], None, None)
            elif who == 'VOIX_OFF' or ending:
                sh['kind'] = 'endline'
            elif 'telephone' in e.get('voice', '') and who not in stage.order:
                sh['kind'] = 'phonecall'
            else:
                mode = plan['kind'] if plan else 'gros'
                if mode == 'group' and who not in [w['who'] for w in plan['who']]: plan = None; mode = 'gros'
                if mode == 'group':
                    a = close_actor('+'.join(w['who'] for w in plan['who']), plan['key']); a['h'] = int(a['h'] * 1.15); a['by'] = 330 + a['h']
                    sh['actors'] = [a]; sh['mode'] = 'close'; sh['group'] = True
                elif mode == 'large':
                    acts = wide_layout(stage, [w['who'] for w in plan['who']] or stage.order, moods, speaker=who, partner=cible(e, last_speaker))
                    for a in acts: a['speaker'] = a['who'] == who
                    sh['actors'] = acts; sh['mode'] = 'wide'; plan = None
                elif mode == 'deux' and plan and len(plan['who']) >= 2 and who not in [w['who'] for w in plan['who']][:2]:
                    pair = [w['who'] for w in plan['who']][:2]; acts = []
                    for c, x in zip(pair, (330, 760)):
                        k = pick(c, moods.get(c, []), None, stage.post(c), need_mouth=c == who, must=stage.props.get(c, []), side=True)
                        a = close_actor(c, k, x=x, scale=0.62); a['by'] = 420 + a['h'] if POSES[k]['frame'] != 'pied' else 600 + a['h']; a['speaker'] = c == who; acts.append(a)
                    sh['actors'] = acts; sh['mode'] = 'two'
                else:
                    post = stage.posture.get(who) or 'debout'; post = 'debout' if post in ('grill', 'marche') else post
                    k = pick(who, emo, 'buste', post, must=stage.props.get(who, []))
                    kargs = pick_args(k)
                    side = stage.side(who, e.get('look') and re.sub(r'[^A-Z_]', '', e['look'].upper()))
                    x = 540 - 110 * side if side else 540
                    tgt = e.get('look') and re.sub(r'[^A-Z_]', '', e['look'].upper())
                    if mode == 'deux' and plan:   # « deux » : l'autre de dos au premier plan, celui qui parle de face
                        pair = [w['who'] for w in plan['who']]; tgt = next((c for c in pair if c != who), tgt)
                    if not (tgt in stage.order and tgt != who): tgt = last_speaker if last_speaker in stage.order and last_speaker != who else None
                    if tgt and not side: side = stage.side(who, tgt)
                    ots = (mode in ('gros', 'deux') and tgt and side and not e.get('thought') and stage.posture.get(tgt) != 'marche')
                    # échange entre deux personnes : toujours la caméra derrière l'épaule de celui qui écoute (demande d'Issa)   # champ / contre-champ, avec de temps en temps un plan seul
                    # cadrages possibles pour cette réplique ; celui choisi par Issa sur une planche (fichier .choix.json) passe avant la règle
                    def seul(k=k, side=side, tgt=tgt, kargs=kargs):
                        a = close_actor(who, k, x=540 - 110 * side if side else 540, tight=(mode == 'tresgros')); a['speaker'] = True; a['look_dir'] = side; a['look_up'] = updown(stage, who, tgt)
                        if kargs: a['pick'] = kargs
                        return {'actors': [a], 'mode': 'close', 'ots': None}
                    def epaule(k=k, side=side, tgt=tgt, kargs=kargs):
                        a = close_actor(who, k, x=540 - 170 * side); a['speaker'] = True; a['look_dir'] = side; a['look_up'] = updown(stage, who, tgt)
                        if kargs: a['pick'] = kargs
                        return {'actors': [a, over_shoulder(tgt, side, stage)], 'mode': 'close', 'ots': tgt}
                    def large():
                        st2 = copy.deepcopy(stage); acts = wide_layout(st2, [c for c in present if c in st2.order] or st2.order, moods, speaker=who, partner=cible(e, last_speaker))   # seulement ceux déjà arrivés
                        for b in acts: b['speaker'] = b['who'] == who
                        return {'actors': acts, 'mode': 'wide', 'ots': None}
                    alts = {'seul': seul, 'large': large}
                    if tgt and side and not e.get('thought') and tgt in HEIGHT: alts['epaule'] = epaule
                    cur = 'epaule' if ots else 'seul'
                    if CHOIX.get(str(len(shots)), {}).get('cadrage') in alts: cur = CHOIX[str(len(shots))]['cadrage']
                    sh.update(alts[cur]()); sh['pan'] = stage.pan(who); sh['cadrage'] = cur
                    if VARIANTES: sh['cadrages'] = {n: f() for n, f in alts.items() if n != cur}
                    # changements de pose sur les balises d'émotion
                    sw = []
                    for tt, tg in e.get('tag_times', []):
                        if tg in EMOS or tg in SYN:
                            k2 = pick(who, [tg] + stage.props.get(who, []), 'buste', post)
                            if k2 and k2 != k and (tagwords([tg]) & set(POSES[k2]['tags'])): sw.append((lead + tt, k2))
                    sh['switch'] = [] if sh.get('mode') == 'wide' else sw
            sh['tagfx'] = [(lead + tt, tg) for tt, tg in e.get('tag_times', []) if tg not in EMOS or tg in ('rire',)]
            # réactions et bruitages accrochés aux mots
            cut = []
            for r in reacts:
                if r['type'] == 'sfx':
                    tw = word_time(e, r.get('word')); sh.setdefault('sfx', []).append((lead + (tw if tw is not None else e.get('dur', 1)), sfx_file(r['name'])))
                else:
                    tw = word_time(e, r.get('word'))
                    if tw is not None and sh['kind'] == 'line' and r['who'] != who:
                        cut.append({'t': lead + tw, 'who': r['who'], 'actions': r['actions'], 'look_dir': stage.side(r['who'], who), 'pan': stage.pan(r['who']), 'posture': stage.post(r['who']), 'props': stage.props.get(r['who'], []), 'tenue': TENUE.get(r['who'], '')})
                        cut[-1]['key'] = pick(r['who'], r['actions'] + stage.props.get(r['who'], []), 'buste', stage.post(r['who']), need_mouth=False)   # choisie ici (tenue du moment)
                        if laughs(r['actions']): sh.setdefault('sfx', []).append((lead + tw + 0.05, 'rire:' + r['who'] + ':petit', 0.5))   # on l'entend rire doucement (sous la voix)
                    elif r['who'] != who: sh.setdefault('after', []).append(r)
            sh['cuts'] = cut
            add(sh); last_speaker = who
            for r in sh.get('after', []):
                k = pick(r['who'], r['actions'] + stage.props.get(r['who'], []), 'buste', stage.post(r['who']), need_mouth=False)
                if k:
                    a = close_actor(r['who'], k, x=540 - 110 * stage.side(r['who'], who)); a['look_dir'] = stage.side(r['who'], who)
                    add({'kind': 'close', 'dur': 1.4, 'actors': [a], 'fx': [(0.15, x) for x in r['actions']], 'pan': stage.pan(r['who']),
                         'sfx': [(0.1, 'rire:' + r['who'], 0.9)] if laughs(r['actions']) else []})
            i = j; continue
        elif t == 'reaction':
            k = pick(e['who'], e['actions'] + stage.props.get(e['who'], []), 'buste', stage.post(e['who']), need_mouth=False)
            if k: add({'kind': 'close', 'dur': 1.4, 'actors': [close_actor(e['who'], k)], 'fx': [(0.15, a) for a in e['actions']],
                       'sfx': [(0.1, 'rire:' + e['who'], 0.9)] if laughs(e['actions']) else []})
        elif t == 'sfx':
            pending_sfx.append((0.1, sfx_file(e['name'])))
        elif t == 'screen':
            if e.get('final'): add({'kind': 'endcard', 'dur': e.get('dur') or 3.0, 'step': 2})
            else: add({'kind': 'screen', 'dur': e.get('dur') or 2.6, 'text': e['text']})
        elif t == 'music':
            music = e['name']
        elif t == 'silence':
            base = dict(last_shot) if last_shot and last_shot['kind'] in ('line', 'close', 'wide') else {'kind': 'wide', 'actors': wide_layout(stage, stage.order, moods)}
            s = {'kind': 'close' if base.get('mode') == 'close' or base['kind'] == 'close' else 'wide', 'dur': e['dur'], 'actors': [dict(a, speaker=False) for a in base.get('actors', [])]}
            if e.get('sfx'): s['sfx'] = [(0.2, sfx_file(e['sfx']))]
            add(s)
        elif t == 'tenue':
            if e['tenue']: TENUE[e['who']] = e['tenue']
            else: TENUE.pop(e['who'], None)
        elif t == 'end':
            ending = True
        i += 1
    if not any(s['kind'] == 'endcard' for s in shots): add({'kind': 'endcard', 'dur': 3.0, 'step': 2})
    apply_pose_choices(shots)
    for sh in shots: orient_shot(sh)
    t0 = 0
    for s in shots: s['t0'] = t0; t0 += s['dur']
    log(f'{len(shots)} plans, durée {t0:.1f} s')
    return shots, t0
def word_time(e, word):
    if not word: return None
    from voices import words, say_text
    target = words(word)
    toks = e['text'].split()
    for i, tk in enumerate(toks):
        if words(say_text(tk))[:1] == target[:1]:
            tw = e.get('tok_word', list(range(len(toks) + 1)))[i]
            return e.get('word_times', {}).get(str(tw), e.get('dur', 1) * i / max(1, len(toks)))
    return None
