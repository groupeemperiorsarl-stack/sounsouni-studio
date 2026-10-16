"""Lecteur du script détaillé (format docs/GUIDE_SCENARISTE.md).

Le script est transformé en une liste d'événements, dans l'ordre :
  scene    : changement de décor (lieu, moment, ambiance)
  plan     : indication de plan (large / deux / gros / très gros / objet / écran / durée fixe)
  line     : réplique (personnage, émotion, regard, voix, texte propre, balises accrochées aux mots)
  reaction : réaction d'un personnage (sur un mot précis ou à la fin de la réplique)
  sfx      : bruitage
  screen   : écran (texte, application, « À suivre… », écran de fin)
  music    : changement de musique
  silence  : pause sans parole
  end      : début de la fin d'épisode
"""
import re, unicodedata

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').strip()

CHAR_ALIASES = {'bakary': 'BAKARY', 'awa': 'AWA', 'modibo': 'MODIBO', 'diasabi': 'DIASABI', 'sali': 'SALI', 'fatim': 'FATIM',
                'mimi': 'MIMI', 'seydou': 'SEYDOU', 'vendeuse': 'VENDEUSE', 'voix_off': 'VOIX_OFF', 'voix off': 'VOIX_OFF',
                'tantie kadi': 'KADI', 'kadi': 'KADI', 'tantie_kadi': 'KADI', 'moussa': 'MOUSSA', 'karim': 'KARIM'}
def who(name):
    n = norm(name).replace('-', ' ')
    return CHAR_ALIASES.get(n, n.upper().replace(' ', '_'))

RE_LINEHEAD = re.compile(r'^(PENSÉE\s+|PENSEE\s+)?([A-ZÀ-Ÿ_][A-ZÀ-Ÿ_ \-]*?)\s*(?:\((.*)\))?\s*$')
RE_TAG = re.compile(r'\{([^}]*)\}')
RE_BRACKET = re.compile(r'^\[(.*)\]$')

def parse_attrs(s):
    """« taquin · regarde: Bakary · voix: normal » -> dict"""
    out = {'emotion': 'neutre', 'look': None, 'voice': 'normal'}
    if not s: return out
    for part in re.split(r'[·;,]', s):
        p = part.strip()
        if not p: continue
        if ':' in p:
            k, v = [x.strip() for x in p.split(':', 1)]
            k = norm(k)
            if k.startswith('regard'): out['look'] = v
            elif k.startswith('voix'): out['voice'] = norm(v)
            else: out[k] = v
        else:
            out['emotion'] = norm(p).replace(' ', '_')
    return out

def split_tags(text):
    """Texte avec {balises} -> (texte propre, [(index_du_mot, balise)])"""
    tags, words = [], []
    pos = 0
    for m in RE_TAG.finditer(text):
        before = text[pos:m.start()]
        words += before.split()
        tags.append((len(words), m.group(1).strip()))
        pos = m.end()
    words += text[pos:].split()
    clean = ' '.join(words)
    return clean, tags

def parse_plan(s):
    s = s.strip(); p = {'type': 'plan', 'raw': s, 'kind': 'gros', 'who': [], 'dur': None, 'extra': []}
    m = re.match(r'^(\d+(?:[.,]\d+)?)\s*s\s*·\s*(.*)$', s)
    if m: p['dur'] = float(m.group(1).replace(',', '.')); s = m.group(2)
    parts = [x.strip() for x in s.split('·')]
    head = parts[0]; p['extra'] = parts[1:]
    m = re.match(r'^(très gros|tres gros|gros|large|deux|objet|écran|ecran)\s*(.*)$', head, re.I)
    if m:
        k = norm(m.group(1)); p['kind'] = {'tres gros': 'tresgros', 'ecran': 'ecran'}.get(k, k); rest = m.group(2).strip()
        if rest.startswith('['):
            items = [x.strip() for x in rest.strip('[]').split(',') if x.strip()]
            known = set(CHAR_ALIASES.values())
            for it in items:
                w = it.split()[0]; pose = ' '.join(it.split()[1:])
                if who(w) not in known and p['who']:   # « [Awa de dos, marche] », « [Bakary, téléphone] » : précision pour le personnage d'avant
                    p['who'][-1]['pose'] = (p['who'][-1]['pose'] + ' ' + norm(it)).strip(); continue
                p['who'].append({'who': who(w), 'pose': norm(pose)})
        elif rest:
            if p['kind'] in ('objet', 'ecran'): p['object'] = rest
            else: p['who'].append({'who': who(rest.split()[0]), 'pose': norm(' '.join(rest.split()[1:]))})
    return p

def tenue_id(t):
    """« bazin doré » → « bazin_dore » ; « normale » / « habituelle » → '' (tenue de tous les jours)."""
    t = re.sub(r'[^a-z0-9]+', '_', norm(t)).strip('_')
    return '' if t in ('normale', 'normal', 'habituelle', 'habituel', 'quotidienne', 'de_tous_les_jours') else t
def pose_id(t):
    """{POSE: mains sur la tête} → « pose:mains_sur_la_tete »"""
    return 'pose:' + re.sub(r'[^a-z0-9]+', '_', norm(t)).strip('_')
def parse_bracket(b):
    b = b.strip()
    m = re.match(r'^(RÉACTION|REACTION)\s+([^:]+?)(?:\s+sur\s+"([^"]+)")?\s*:\s*(.*)$', b, re.I)
    if m: return {'type': 'reaction', 'who': who(m.group(2)), 'word': m.group(3), 'actions': [norm(x).replace(' ', '_') for x in m.group(4).split(',') if x.strip()]}
    m = re.match(r'^BRUITAGE(?:\s+sur\s+"([^"]+)")?\s*:\s*(.*)$', b, re.I)
    if m: return {'type': 'sfx', 'word': m.group(1), 'name': norm(m.group(2))}
    m = re.match(r'^(ÉCRAN|ECRAN)\s*(FIN)?\s*(\d+(?:[.,]\d+)?)?\s*s?\s*:\s*(.*)$', b, re.I)
    if m: return {'type': 'screen', 'final': bool(m.group(2)), 'dur': float(m.group(3).replace(',', '.')) if m.group(3) else None, 'text': m.group(4).strip()}
    m = re.match(r'^TENUE\s+([^:]+?)\s*:\s*(.*)$', b, re.I)   # [TENUE AWA: bazin doré] … [TENUE AWA: normale]
    if m: return {'type': 'tenue', 'who': who(m.group(1)), 'tenue': tenue_id(m.group(2))}
    m = re.match(r'^MUSIQUE\s*:\s*(.*)$', b, re.I)
    if m: return {'type': 'music', 'name': norm(m.group(1))}
    m = re.match(r'^SILENCE\s*(\d+(?:[.,]\d+)?)?\s*s?\s*(?::\s*(.*))?$', b, re.I)
    if m: return {'type': 'silence', 'dur': float(m.group(1).replace(',', '.')) if m.group(1) else 2.0, 'sfx': norm(m.group(2) or '')}
    return {'type': 'note', 'text': b}

def parse(text):
    ev = []; meta = {'title': '', 'new_chars': [], 'new_decors': [], 'new_outfits': [], 'new_objects': []}
    lines = [l.rstrip() for l in text.splitlines()]
    cur = None   # réplique en cours
    def flush():
        nonlocal cur
        if cur is not None:
            raw = ' '.join(cur['raw']).strip()
            cur['text'], cur['tags'] = split_tags(raw)
            del cur['raw']
            if cur['text'] or cur['tags']: ev.append(cur)
            cur = None
    for l in lines:
        s = l.strip()
        if not s or s.startswith('#') or s.startswith('```'):
            flush(); continue
        up = s.upper()
        if up.startswith('TITRE:') or up.startswith('TITLE:'):
            flush(); meta['title'] = s.split(':', 1)[1].strip(); continue
        if up.startswith('NOUVEAU PERSONNAGE:'): flush(); meta['new_chars'].append(s.split(':', 1)[1].strip()); continue
        if up.startswith('NOUVEAU DÉCOR:') or up.startswith('NOUVEAU DECOR:'): flush(); meta['new_decors'].append(s.split(':', 1)[1].strip()); continue
        if up.startswith('NOUVELLE TENUE:'): flush(); meta['new_outfits'].append(s.split(':', 1)[1].strip()); continue
        if up.startswith('NOUVEL OBJET:'): flush(); meta['new_objects'].append(s.split(':', 1)[1].strip()); continue
        if up.startswith('DÉCOR:') or up.startswith('DECOR:'):
            flush(); parts = [x.strip() for x in s.split(':', 1)[1].split('·')]
            sc = {'type': 'scene', 'decor': norm(parts[0]).upper(), 'moment': norm(parts[1]) if len(parts) > 1 else 'jour', 'ambiance': ''}
            for p in parts[2:]:
                if ':' in p: sc['ambiance'] = norm(p.split(':', 1)[1])
            ev.append(sc); continue
        if up.startswith('PLAN:'):
            flush(); ev.append(parse_plan(s.split(':', 1)[1])); continue
        if up.startswith('FIN:') or up == 'FIN':
            flush(); ev.append({'type': 'end'}); continue
        mb = RE_BRACKET.match(s)
        if mb:
            flush(); ev.append(parse_bracket(mb.group(1))); continue
        mh = RE_LINEHEAD.match(s)
        if mh and mh.group(2).strip() == mh.group(2).strip().upper() and (mh.group(3) is not None or norm(mh.group(2)) in CHAR_ALIASES) and len(mh.group(2).strip()) > 1:
            flush(); a = parse_attrs(mh.group(3))
            cur = {'type': 'line', 'who': who(mh.group(2)), 'thought': bool(mh.group(1)), 'raw': [], **a}
            continue
        if cur is not None: cur['raw'].append(s)
        else: ev.append({'type': 'note', 'text': s})
    flush()
    # numérotation des répliques
    n = 0
    for e in ev:
        if e['type'] == 'line': e['id'] = f'L{n:03d}'; n += 1
    return meta, ev

if __name__ == '__main__':
    import sys, json
    meta, ev = parse(open(sys.argv[1], encoding='utf-8').read())
    print(json.dumps({'meta': meta, 'events': ev}, ensure_ascii=False, indent=1))
