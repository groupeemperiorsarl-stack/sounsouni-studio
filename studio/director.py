"""Réalisateur automatique : transforme les événements du script (+ durées des voix) en liste de plans.
Règles apprises sur les épisodes 12-14 :
 - un seul sol par plan d'ensemble, profondeur (arrière-plan plus petit), personne ne flotte ;
 - chaque personnage garde sa place dans la scène ; en gros plan, il est décalé du côté opposé à celui qu'il regarde ;
 - gros plans cadrés tête-buste (la bouche se voit) ;
 - le lieu du plan est toujours le décor de la scène en cours ;
 - réactions sur un mot = plan de coupe pendant que la voix continue ;
 - marche : cycle de pas quand il existe, déplacement en ligne droite."""
import json, os, re
from script import norm
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
CAT = json.load(open(A + '/catalog.json'))
POSES = CAT['poses']; HEIGHT = CAT['height']
GROUND, BACK = 1900, 1560
EMOS = {'neutre', 'sourire', 'grand_sourire', 'sourire_malin', 'rire', 'rire_retenu', 'colere', 'furieux', 'choc', 'surpris', 'peur', 'panique', 'triste',
        'gene', 'mepris', 'mefiant', 'yeux_plisses', 'amoureux', 'fier', 'moue', 'degout', 'innocent', 'taquin', 'pensif', 'serieux', 'inquiet', 'tendre',
        'moqueur', 'froide', 'hesitante', 'chaleureuse', 'joie', 'content', 'severe', 'emu'}
SYN = {'grand_sourire': 'sourire content', 'sourire_malin': 'taquin sourire', 'rire_retenu': 'rire', 'furieux': 'colere furieux', 'yeux_plisses': 'mefiant mepris',
       'peur': 'peur panique', 'panique': 'panique peur', 'surpris': 'surpris choc', 'froide': 'mepris colere froide', 'moqueur': 'moqueur taquin rire',
       'hesitante': 'pensif moue', 'innocent': 'sourire', 'emu': 'emu amoureux', 'tendre': 'tendre sourire', 'inquiet': 'inquiet triste',
       'chaleureuse': 'sourire', 'severe': 'severe colere', 'serieux': 'serieux neutre', 'joie': 'joie content rire'}
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
def pick(char, want=(), frame=None, posture=None, need_mouth=True, avoid_cycle=True):
    best, bs = None, -1e9
    w = tagwords(want)
    for k, p in POSES.items():
        if p['char'] != char: continue
        tags = set(p['tags'])
        if avoid_cycle and ('cycle_marche' in tags or 'cycle_marche_dos' in tags): continue
        s = 3 * len(w & tags)
        if frame:
            if p['frame'] == frame: s += 2
            elif frame == 'buste' and p['frame'] == 'pied': s += 1
            elif frame == 'pied' and p['frame'] != 'pied': s -= 6
        if posture:
            if p['posture'] == posture: s += 3
            elif posture in ('assis', 'banc') and p['posture'] in ('assis', 'banc'): s += 2
            elif p['posture'] in ('assis', 'banc', 'dos', 'tombe', 'court', 'marche') and posture != p['posture']: s -= 4
        elif p['posture'] in ('dos', 'tombe', 'court', 'marche') and p['posture'] not in w and not (tags & w & {'tombe', 'glisse', 'court', 'dos', 'marche'}): s -= 5
        OBJ = {'telephone', 'brochettes', 'boite', 'cartes', 'plateau', 'billet', 'parapluie', 'grill', 'hoverboard', 'robe', 'canne', 'voiture', 'mange', 'verse'}
        s -= 2.5 * len((tags & OBJ) - w)
        # pas de visage à contre-sens : un sourire demandé ne doit jamais donner une pose triste, et l'inverse
        if w & POS and tags & NEG and not (w & NEG): s -= 6
        if w & NEG and tags & POS and not (w & POS): s -= 4
        if need_mouth and p['mouth']: s += 1.5
        if 'neutre' in tags and not w: s += 1
        if s > bs: best, bs = k, s
    return best
def group_pick(chars, want):
    w = tagwords(want); cs = set(chars)
    for k, p in POSES.items():
        if '+' in p['char'] and set(p['char'].split('+')) == cs and (w & set(p['tags'])): return k
    return None
def posture_of(pose_text):
    t = norm(pose_text or '')
    if 'banc' in t: return 'banc'
    if 'assis' in t: return 'assis'
    if 'marche' in t: return 'marche'
    if 'court' in t: return 'court'
    if 'dos' in t: return 'dos'
    if 'grill' in t: return 'grill'
    return 'debout'
class Stage:
    def __init__(self): self.order = []; self.posture = {}
    def set(self, who_list):
        for w in who_list:
            if w['who'] not in self.order: self.order.append(w['who'])
            if w.get('pose'): self.posture[w['who']] = posture_of(w['pose'])
    def add(self, who):
        if who and who not in self.order and who in HEIGHT: self.order.append(who)
    def side(self, who, target):
        if who in self.order and target in self.order: return 1 if self.order.index(target) > self.order.index(who) else -1
        return 0
def wide_layout(stage, chars, moods, speaker=None):
    """Plan d'ensemble : tout le monde sur le même sol, côte à côte sans se chevaucher, arrière-plan plus petit."""
    chars = [c for c in chars if c in HEIGHT]; acts = []
    front = chars[:4]; back = chars[4:]
    for c in front:
        post = stage.posture.get(c, 'debout'); pst = 'debout' if post == 'grill' else post
        want = list(moods.get(c, [])) + (['grill'] if post == 'grill' else [])
        walk = post == 'marche' and c == 'AWA'
        k = 'awa_pas1' if walk else (pick(c, want, 'pied', pst, need_mouth=(c == speaker)) or pick(c, want, None, None))
        sit = POSES[k]['posture'] in ('assis', 'banc')
        h = int((840 if sit else 1060) * HEIGHT.get(c, 1)) if POSES[k]['frame'] == 'pied' else 880
        w = POSES[k]['size'][0] * h / POSES[k]['size'][1]
        act = {'key': k, 'who': c, 'h': h, 'w': w, 'by': GROUND + (0 if sit else 15), 'walk': 'AWA' if walk else None}
        if walk:   # elle entre en marchant puis s'arrête à sa place, avec une pose qui parle
            act['stop_key'] = pick(c, list(moods.get(c, [])), 'pied', 'debout', need_mouth=True) or pick(c, [], 'pied', None)
            stage.posture[c] = 'debout'
        acts.append(act)
    tot = sum(a['w'] for a in acts) + 30 * max(0, len(acts) - 1); avail = 1040
    if tot > avail:
        f = max(0.7, avail / tot)
        for a in acts: a['h'] = int(a['h'] * f); a['w'] *= f
        tot = sum(a['w'] for a in acts) + 30 * max(0, len(acts) - 1)
    gap = 30 if len(acts) < 2 else 30 + max(0, (avail - tot)) / (len(acts) - 1) * 0.6
    tot2 = sum(a['w'] for a in acts) + gap * max(0, len(acts) - 1); x = 540 - tot2 / 2
    if tot2 > 1080: gap -= (tot2 - 1060) / max(1, len(acts) - 1); tot2 = 1060; x = 10
    for a in acts:
        a['x'] = int(x + a['w'] / 2); x += a['w'] + gap
        if a.get('walk'):
            # les images de marche regardent vers la droite : venir de la gauche = image normale, venir de la droite = image retournée
            from_right = a['x'] > 540
            a['vx'] = -260 if from_right else 260; a['flip'] = from_right; a['walk_t'] = 1.8
    for i, c in enumerate(back):
        k = pick(c, moods.get(c, []), 'pied', stage.posture.get(c)); acts.insert(0, {'key': k, 'who': c, 'x': int(160 + i * 260), 'by': BACK, 'h': int(600 * HEIGHT.get(c, 1)), 'back': True})
    return acts
def close_actor(char, key, x=540, tight=False, scale=1.0):
    p = POSES[key]; fr = p['frame']
    if fr == 'pied': h = 3000 if tight else 2650; by = 330 + h
    elif fr == 'buste': h = 1950 if tight else 1700; by = 300 + h
    elif fr == 'groupe': h = 2300; by = 380 + h
    else: h = 1500; by = 250 + h
    if scale != 1.0: h = int(h * scale); by = int(330 + h) if fr == 'pied' else int(250 + h)
    w = p['size'][0] * h / p['size'][1]; cx = x + (0.5 - p.get('head_x', 0.5)) * w   # le visage est placé à x
    if fr == 'groupe': cx = x
    return {'key': key, 'who': char, 'x': int(cx), 'by': by, 'h': h, 'face_x': x, 'tight': tight, 'scale': scale}
def build(meta, events, log=print):
    shots = []; stage = Stage(); scene = {'decor': 'KIOSQUE', 'moment': 'jour', 'ambiance': ''}; plan = None
    moods = {}; music = 'joyeuse'; ending = False; pending_sfx = []; first_in_scene = True; last_shot = None
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
            scene = dict(e); stage = Stage(); plan = None; first_in_scene = True; moods = {}
            # personnages de la scène : ceux qui parlent avant le prochain décor
            j = i + 1
            while j < len(events) and events[j]['type'] != 'scene':
                if events[j]['type'] == 'plan': stage.set(events[j]['who'])
                if events[j]['type'] == 'line' and not events[j].get('thought') and 'telephone' not in events[j].get('voice', ''): stage.add(events[j]['who'])
                j += 1
        elif t == 'plan':
            stage.set(e['who']); plan = e
            if e.get('dur') or e['kind'] in ('objet', 'ecran'):
                fx = [(0.1, re.sub(r'[{}]', '', x)) for x in re.findall(r'\{[^}]+\}', ' '.join(e.get('extra', [])))]
                if e['kind'] in ('objet', 'ecran'): add({'kind': 'insert', 'dur': e.get('dur') or 2.4, 'object': e.get('object', ''), 'fx': fx}); plan = None
                elif len(e['who']) > 1 and group_pick([w['who'] for w in e['who']], [x[1] for x in fx]):
                    g = group_pick([w['who'] for w in e['who']], [x[1] for x in fx]); add({'kind': 'close', 'dur': e['dur'], 'actors': [close_actor('+'.join(w['who'] for w in e['who']), g)], 'fx': fx, 'mode': 'close'})
                    plan = {'kind': 'group', 'key': g, 'who': e['who']}; i += 1; continue
                elif e['kind'] == 'large' or len(e['who']) > 1:
                    add({'kind': 'wide', 'dur': e['dur'], 'actors': wide_layout(stage, [w['who'] for w in e['who']] or stage.order, moods), 'fx': fx}); plan = None
                else:
                    c = e['who'][0]['who']; want = [x[1] for x in fx]
                    k = pick(c, want, 'buste' if e['kind'] == 'tresgros' else None, None)
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
            emo = [e.get('emotion', 'neutre')] + [tg for _, tg in e['tags'] if tg in EMOS]
            moods[who] = emo[:1]
            sh = {'kind': 'line', 'who': who, 'line': e, 'lead': lead, 'dur': dur}
            if who == 'VOIX_OFF' or ending:
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
                    acts = wide_layout(stage, [w['who'] for w in plan['who']] or stage.order, moods, speaker=who)
                    for a in acts: a['speaker'] = a['who'] == who
                    sh['actors'] = acts; sh['mode'] = 'wide'; plan = None
                elif mode == 'deux' and plan and len(plan['who']) >= 2:
                    pair = [w['who'] for w in plan['who']][:2]; acts = []
                    for c, x in zip(pair, (330, 760)):
                        k = pick(c, moods.get(c, []), None, stage.posture.get(c) if stage.posture.get(c) != 'grill' else None, need_mouth=c == who)
                        a = close_actor(c, k, x=x, scale=0.62); a['by'] = 420 + a['h'] if POSES[k]['frame'] != 'pied' else 600 + a['h']; a['speaker'] = c == who; acts.append(a)
                    sh['actors'] = acts; sh['mode'] = 'two'
                else:
                    post = stage.posture.get(who); post = None if post in ('grill', 'debout', None) else post
                    k = pick(who, emo, 'buste', post)
                    side = stage.side(who, e.get('look') and re.sub(r'[^A-Z_]', '', e['look'].upper()))
                    x = 540 - 110 * side if side else 540
                    a = close_actor(who, k, x=x, tight=(mode == 'tresgros')); a['speaker'] = True
                    sh['actors'] = [a]; sh['mode'] = 'close'
                    # changements de pose sur les balises d'émotion
                    sw = []
                    for tt, tg in e.get('tag_times', []):
                        if tg in EMOS or tg in SYN:
                            k2 = pick(who, [tg], 'buste', post)
                            if k2 and k2 != k and (tagwords([tg]) & set(POSES[k2]['tags'])): sw.append((lead + tt, k2))
                    sh['switch'] = sw
            sh['tagfx'] = [(lead + tt, tg) for tt, tg in e.get('tag_times', []) if tg not in EMOS or tg in ('rire',)]
            # réactions et bruitages accrochés aux mots
            cut = []
            for r in reacts:
                if r['type'] == 'sfx':
                    tw = word_time(e, r.get('word')); sh.setdefault('sfx', []).append((lead + (tw if tw is not None else e.get('dur', 1)), sfx_file(r['name'])))
                else:
                    tw = word_time(e, r.get('word'))
                    if tw is not None and sh['kind'] == 'line' and r['who'] != who: cut.append({'t': lead + tw, 'who': r['who'], 'actions': r['actions']})
                    elif r['who'] != who: sh.setdefault('after', []).append(r)
            sh['cuts'] = cut
            add(sh)
            for r in sh.get('after', []):
                k = pick(r['who'], r['actions'], 'buste', None, need_mouth=False)
                if k: add({'kind': 'close', 'dur': 1.4, 'actors': [close_actor(r['who'], k)], 'fx': [(0.15, a) for a in r['actions']]})
            i = j; continue
        elif t == 'reaction':
            k = pick(e['who'], e['actions'], 'buste', None, need_mouth=False)
            if k: add({'kind': 'close', 'dur': 1.4, 'actors': [close_actor(e['who'], k)], 'fx': [(0.15, a) for a in e['actions']]})
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
        elif t == 'end':
            ending = True
        i += 1
    if not any(s['kind'] == 'endcard' for s in shots): add({'kind': 'endcard', 'dur': 3.0, 'step': 2})
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
