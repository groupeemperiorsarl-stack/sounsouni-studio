"""Rendu image par image des plans, en parallèle, puis assemblage avec le son."""
import os, math, json, subprocess, re
from functools import lru_cache
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
import gfx, script
from gfx import W, H, FPS, paste, sticker, prog, eo, lerp
from director import POSES, GROUND
A = gfx.A
DECOR_ALIAS = [('KIOSQUE', 'KIOSQUE'), ('ATELIER', 'ATELIER'), ('MARCHE', 'MARCHE'), ('CABINE', 'CABINE'), ('BUREAU', 'BUREAU'), ('VILLA', 'VILLA'),
               ('SHOWROOM', 'SHOWROOM'), ('VOITURE', 'RUE'), ('RUE', 'RUE')]
def decor_file(name):
    n = name.upper()
    if os.path.exists(f'{A}/decors/{n}.jpg'): return n   # décor du même nom (ex. VILLA_FETE rangé depuis Gemini) avant les autres noms (VILLA)
    for k, v in DECOR_ALIAS:
        if k in n: return v
    return 'KIOSQUE'
@lru_cache(16)
def decor(name, moment, blur):
    im = Image.open(f'{A}/decors/{decor_file(name)}.jpg').convert('RGB'); s = max(2050 / im.height, (W + 120) / im.width)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS); im = gfx.tint(im, moment)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return im
DECOR_LARGE = {'KIOSQUE': (0.32, 0.12)}
try: DECOR_LARGE.update({k: tuple(v) for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reglages.json'), encoding='utf-8')).get('decor_large', {}).items()})
except Exception: pass
DECOR_REGLE = set(DECOR_LARGE)   # cadrage réglé à la main (validé par Issa) : gardé ; les autres décors suivent leur sol libre   # plan large : zoom et hauteur du cadrage (la théière au premier plan du kiosque sort de l'image, personne n'a les pieds dessus)
def background(s, lt, blur=0, zoom=0.0, pan=0.0, haut=0.45):
    """pan (-1 à 1) : en gros plan, la caméra regarde la partie du décor où se trouve le personnage."""
    im = decor(s['decor'], s['moment'], blur); x = int((im.width - W) / 2 + 16 * math.sin(lt * 0.25)); y = int((im.height - H) * 0.6)
    fr = im.crop((x, y, x + W, y + H))
    if zoom:
        zw, zh = int(W * (1 + zoom)), int(H * (1 + zoom)); fr = fr.resize((zw, zh), Image.BILINEAR)
        ox = int((zw - W) / 2 * (1 + max(-1, min(1, pan)))); oy = int((zh - H) * haut)
        fr = fr.crop((ox, oy, ox + W, oy + H))
    return fr
SOL = {}
try: SOL = json.load(open(f'{A}/catalog.json', encoding='utf-8')).get('sol', {})
except Exception: pass
def background_sol(s, lt, pieds):
    """Plan large cadré sur le SOL LIBRE du décor (studio/sol.py) : le bas de la bande de sol tombe en bas de l'image et sa partie haute
    derrière les pieds les plus hauts (rangée du fond). Personne ne flotte, personne n'est debout sur une voiture ou une table.
    Rend (image, genoux) : genoux = True si le sol est trop étroit même en zoomant (on cadre alors aux genoux, les pieds hors de l'image)."""
    v = SOL.get(decor_file(s['decor']))
    if not v or not v.get('fiable') or decor_file(s['decor']) in DECOR_REGLE: return None, False
    im = decor(s['decor'], s['moment'], 0); a, b = v['haut'] * im.height, v['bas'] * im.height
    k = max(1.0, (H + 20) / max(1, b), (H + 80 - pieds) / max(1, b - a)); genoux = k > 2.3; k = min(k, 2.3)
    T = max(0, min(b - (H + 20) / k, im.height - H / k)); cw, ch = W / k, H / k
    x0 = (im.width - cw) / 2 + 16 * math.sin(lt * 0.25) / k; x0 = max(0, min(im.width - cw, x0))
    return im.crop((int(x0), int(T), int(x0 + cw), int(T + ch))).resize((W, H), Image.BILINEAR), genoux
@lru_cache(96)
def pose_img(key, h, opened=False, flip=False):
    if '@' in key:   # tête tournée (variante LivePortrait), sinon pose d'origine
        p = f'{A}/poses/tourne/{key}{"_o" if opened else ""}.webp'
        if not os.path.exists(p): p = f'{A}/poses/tourne/{key}.webp'
        if not os.path.exists(p): key = key.split('@')[0]
    if '@' not in key:
        p = f'{A}/poses/{key}{"_o" if opened else ""}.webp'
        if not os.path.exists(p): p = f'{A}/poses/{key}.webp'
    im = sans_frange(Image.open(p).convert('RGBA')); im = im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
def sans_frange(im, px=2):
    """Règle d'Issa (22/10/2026) : jamais de contour blanc autour d'un personnage. Le bord du détourage garde souvent une fine ligne
    du fond clair d'origine : on rentre le bord de 2 pixels, on recolore la bordure avec les couleurs du personnage juste à côté,
    et on adoucit le bord (pas de marches)."""
    if os.environ.get('STUDIO_SANS_DEFRANGE'): return im
    import cv2   # chargé seulement ici : les machines « voix » n'ont pas cet outil
    a = np.array(im); al = a[..., 3]; plein = (al > 40).astype(np.uint8)
    if plein.mean() > 0.97: return im   # objet ou image sans détourage
    coeur = cv2.erode(plein, np.ones((3, 3), np.uint8), iterations=px)
    bord = ((plein > 0) & (coeur == 0)).astype(np.uint8)
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), cv2.dilate(bord, np.ones((3, 3), np.uint8)) & plein, 3, cv2.INPAINT_TELEA)
    doux = cv2.GaussianBlur(coeur.astype(np.float32), (0, 0), 0.9) * 255
    a2 = np.dstack([rgb, np.minimum(al.astype(np.float32), doux).clip(0, 255).astype(np.uint8)])
    return Image.fromarray(a2, 'RGBA')
@lru_cache(64)
def envelope(wav):
    y, sr = sf.read(wav); y = y if y.ndim == 1 else y.mean(1); hop = sr // FPS
    e = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(y) else 0 for i in range(len(y) // hop + 2)])
    e = np.convolve(e, [0.25, 0.5, 0.25], 'same'); return e / (np.percentile(e, 95) + 1e-6)
def mouth_open(line, t):
    if line is None or line.get('thought') or 'wav' not in line: return False
    e = envelope(line['wav']); k = int(t * FPS)
    return 0 <= k < len(e) and e[k] > 0.3 and not (e[k] < 0.75 and (k // 3) % 2)
WALK = {'AWA': ['awa_pas1', 'awa_pas3', 'awa_pas2', 'awa_pas3'], 'AWA_dos': ['awa_dos_pas1', 'awa_dos_pas3', 'awa_dos_pas2', 'awa_dos_pas3']}
def body_motion(tags, lt):
    """Petits mouvements du corps déclenchés par les balises : (dx, dy, échelle, rotation)."""
    dx = dy = rot = 0.0; sc = 1.0
    for t0, tg in tags:
        k = lt - t0
        if k < 0: continue
        if tg == 'sursaut' and k < 0.4: dy -= 70 * math.sin(math.pi * k / 0.4)
        elif tg == 'recule': sc *= 1 - 0.05 * eo(k / 0.3); dy += 20 * eo(k / 0.3)
        elif tg == 'avance': sc *= 1 + 0.05 * eo(k / 0.3)
        elif tg == 'tremble' and k < 1.5: dx += 6 * math.sin(lt * 60)
        elif tg == 'hoche_tete' and k < 1.0: rot += 2.5 * math.sin(k * 18)
        elif tg == 'secoue_tete' and k < 1.0: dx += 10 * math.sin(k * 22)
        elif tg in ('penche_tete', 'tourne_vers'): rot += 4 * eo(k / 0.3)
        elif tg == 'se_penche': rot += 3 * eo(k / 0.3); dy += 30 * eo(k / 0.3)
        elif tg in ('s_affale', 'soupir'): dy += 35 * eo(k / 0.5); sc *= 1 - 0.02 * eo(k / 0.5)
        elif tg == 'bombe_torse': sc *= 1 + 0.03 * eo(k / 0.3)
    return dx, dy, sc, rot
def draw_actor(fr, a, lt, line=None, tags=(), speaking_t=None):
    key = a['key']; h = a['h']; flip = a.get('flip', False)
    for kk in (key, a.get('stop_key')):
        if kk and '@' in kk and kk not in POSES:
            import director; director.yaw_variant(*director.parse_variant(kk))
    opened = a.get('speaker') and speaking_t is not None and POSES[key]['mouth'] and mouth_open(line, speaking_t)
    breath = 1 + 0.006 * math.sin(lt * 2 * math.pi / 3.4 + a['x'] * 0.01)
    dx, dy, sc, rot = body_motion(tags, lt) if a.get('speaker') else (0, 0, 1, 0)
    walk_dx = 0
    if a.get('walk'):
        wt = a.get('walk_t', 1e9); cyc = WALK.get(a['walk'])
        if lt < wt:
            if cyc: key = cyc[int(lt * 3.4) % 4]
            opened = False; walk_dx = -a.get('vx', 0) * (wt - lt) if wt < 1e8 else a.get('vx', 0) * lt
        else:
            key = a.get('stop_key') or key; flip = a.get('stop_flip', False)
            opened = a.get('speaker') and speaking_t is not None and POSES[key]['mouth'] and mouth_open(line, speaking_t)
    if a.get('fg'): opened = False
    im = pose_img(key, int(h * sc * breath / 4) * 4, bool(opened), flip)
    if a.get('fg'):   # épaule de celui qui écoute, au premier plan (caméra derrière lui) : floue et un peu sombre
        al = im.getchannel('A')
        if a.get('silhouette'):
            # vu de dos sans image de dos : la forme du personnage, avec ses couleurs (cheveux / casquette en haut, habits en bas)
            arr = np.array(im.convert('RGB')).astype(np.float32); A_ = np.array(al) > 128; hh = arr.shape[0]
            out = np.zeros_like(arr); band = max(1, hh // 24)
            def mean_rows(y0, y1, fallback):
                px = arr[y0:y1][A_[y0:y1]]; return px.mean(0) if len(px) > 20 else fallback
            hair = mean_rows(0, max(2, int(hh * 0.05)), np.array([40, 30, 25], np.float32))
            for y in range(0, hh, band):
                c = hair if y < hh * 0.16 else mean_rows(y, y + band, hair)
                out[y:y + band] = c * (0.55 if y < hh * 0.16 else 0.6)
            rgb = Image.fromarray(out.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
        else: rgb = im.convert('RGB').filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.72))
        im = rgb.convert('RGBA'); im.putalpha(al.filter(ImageFilter.GaussianBlur(10 if a.get('silhouette') else 6)))
    if a.get('enter'):   # entrée dans le plan : arrive du bord le plus proche, avec le pas qui balance
        pe = prog(lt, 0, 1.5); sd = 1 if a['x'] > 540 else -1
        walk_dx += sd * 650 * (1 - eo(pe)); dy -= abs(math.sin(lt * 9)) * 16 * (1 - pe)
    cx = a['x'] + dx + walk_dx; by = a['by'] + dy
    if not (a.get('fg') or a.get('silhouette')) and POSES.get(key.split('@')[0], {}).get('frame') == 'pied' and by < H + 10 and not a.get('walk'):
        ombre(fr, cx, by, im.width)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC, center=(im.width / 2, im.height))
    paste(fr, im, cx, by - im.height / 2, 1.0, 1.0, sh=not a.get('back'))
    return cx, by - h  # sommet de la tête
def ombre(fr, cx, by, w):
    """Ombre douce et plate sous les pieds (largeur ≈ 70 % du personnage)."""
    ow, oh = int(w * 0.7), max(10, int(w * 0.09)); sh = Image.new('L', (ow + 40, oh + 40), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse((20, 20, 20 + ow, 20 + oh), fill=95); sh = sh.filter(ImageFilter.GaussianBlur(9))
    noir = Image.new('RGBA', sh.size, (0, 0, 0, 255)); noir.putalpha(sh); fr.paste(noir, (int(cx - sh.width / 2), int(by - sh.height / 2 - 4)), noir)
def fx_draw(fr, fx, lt, head):
    hx, hy = head; hy = max(hy, 340); hx = min(max(hx, 260), 820)   # jamais sous la bulle ni hors cadre
    for t0, tg in fx:
        k = lt - t0
        if k < 0 or k > 2.2: continue
        if tg in ('coeurs', 'amoureux'): gfx.hearts(fr, hx, hy + 300, k)
        elif tg in ('sueur', 'goutte', 'panique'): gfx.sweat(fr, hx + 140, hy + 140, k)
        elif tg in ('fumee_tete', 'furieux'): gfx.smoke(fr, hx - 150, hy + 120, k, 1.0, 4, (90, 90, 90)); gfx.smoke(fr, hx + 150, hy + 120, k, 1.0, 4, (90, 90, 90))
        elif tg == 'etoiles': gfx.stars(fr, hx, hy + 80, k)
        elif tg in ('point_exclamation', 'choc'): sticker(fr, '!', hx + 260, hy + 160, k, 0, 110, (200, 30, 30))
        elif tg == 'point_interrogation': sticker(fr, '?', hx + 260, hy + 160, k, 0, 110, (40, 40, 40))
        elif tg == 'eclair': sticker(fr, '!!', hx + 260, hy + 160, k, 0, 100, (240, 180, 0))
        elif tg == 'rougit': gfx.redface(fr, hx, hy + 260, k)
        elif tg in ('idee', 'ampoule'): gfx.bulb(fr, hx + 250, hy + 60, k)
        elif tg == 'rire' : sticker(fr, 'Ha ha ha !', hx + 180, hy + 80, k, 0, 70, (240, 150, 20))
        elif tg == 'clin_oeil': sticker(fr, ';)', hx + 240, hy + 120, k, 0, 80, (200, 40, 120))
        elif tg.startswith('autocollant'):
            m = re.search(r'"([^"]+)"', tg); sticker(fr, m.group(1) if m else '!', 540, 1480, k, 0, 100, (150, 40, 40))
def norm_txt(t):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()
def photo_for(desc):
    """Image pour « Photo : … » : l'image de groupe des personnages cités, sinon le premier personnage cité, sinon un décor cité."""
    from script import CHAR_ALIASES
    n = norm_txt(desc); chars = []
    for a, c in sorted(CHAR_ALIASES.items(), key=lambda x: -len(x[0])):
        if re.search(r'\b' + re.escape(a) + r'\b', n) and c not in chars: chars.append(c)
    if len(chars) >= 2:
        for k, p in POSES.items():
            if '+' in p['char'] and set(p['char'].split('+')) == set(chars[:2]): return Image.open(f'{A}/poses/{k}.webp').convert('RGBA')
    if chars:
        from director import pick
        k = pick(chars[0], [], 'pied', None)
        if k: return Image.open(f'{A}/poses/{k}.webp').convert('RGBA')
    for d in ('atelier', 'kiosque', 'marche', 'rue', 'bureau', 'villa', 'showroom', 'cabine'):
        if d in n or (d == 'atelier' and ('couture' in n or 'vitrine' in n)):
            im = Image.open(f'{A}/decors/{d.upper()}.jpg').convert('RGBA'); return im.crop((0, im.height // 4, im.width, im.height * 3 // 4))
    return None
def frame_of(shots, T):
    for s in shots:
        if s['t0'] <= T < s['t0'] + s['dur']: return s, T - s['t0']
    return shots[-1], shots[-1]['dur'] - 1 / FPS
def draw(s, lt):
    k = s['kind']; d = s['dur']
    if k == 'title':
        fr = background(s, lt, blur=6); paste(fr, gfx.ICON().resize((220, 220), Image.LANCZOS), 540, 640, eo(prog(lt, 0, 0.4)), sh=False)
        p = gfx.sticker_img('Les Plans de Bakary', 76, gfx.FONCE); paste(fr, p, 540, 900, eo(prog(lt, 0.2, 0.4)))
        t = s.get('title', '').split('–')[-1].split(':')[-1].strip() or s.get('title', '')
        if t: paste(fr, gfx.sticker_img(t, 46, gfx.ORANGE), 540, 1050, eo(prog(lt, 0.5, 0.4)), sh=False)
        return fr
    if k in ('endline', 'endcard'):
        step = s.get('step', 1); return gfx.end_screen(lt, step, s.get('slogan', ''))
    if k == 'screen':
        txt = s['text']
        lines = [x.strip() for x in re.split(r' – | - | · ', txt) if x.strip()]
        if re.match(r'^(nouveau |nouvelle )?(statut|publication|post)', norm_txt(txt)):
            fr = background(s, lt, blur=8); photo = None; rest = []
            for l in lines:
                m = re.match(r'^photo\s*:\s*(.*)$', l, re.I)
                if m: photo = photo_for(m.group(1)); continue
                if re.match(r'^(nouveau |nouvelle )?(statut|publication|post)$', norm_txt(l)): continue
                rest.append(l)
            paste(fr, gfx.phone_with(gfx.status_screen(rest, photo)), 540, lerp(1300, 1100, eo(prog(lt, 0, 0.35))), 1.0, 1.15)
            return fr
        if any(c in txt for c in '–✔✖★[·') or 'sounsouni' in txt.lower() or len(txt) > 40:
            fr = background(s, lt, blur=8)
            title = 'Sounsouni'
            if lines and lines[0].lower().startswith('sounsouni'): title = lines[0]; lines = lines[1:]
            paste(fr, gfx.phone_with(gfx.app_screen(lines, title[:22])), 540, lerp(1300, 1100, eo(prog(lt, 0, 0.35))), 1.0, 1.15)
            return fr
        fr = gfx.tint(background(s, lt, blur=10), 'nuit'); f = gfx.font(gfx.FB, 120)
        for i, l in enumerate(gfx.wrap(txt, f, 950)): ImageDraw.Draw(fr).text((540, 920 + i * 140), l, font=f, fill='white', anchor='mm')
        return fr
    if k == 'insert':
        fr = background(s, lt, blur=4, zoom=0.1); obj = gfx.norm if False else s.get('object', '').lower()
        cands = [(sum(w in obj for w in p['tags']), key) for key, p in POSES.items() if p['frame'] == 'objet']   # l'objet dont le plus de mots correspondent
        mots = [w for w in re.sub(r"[^a-z0-9àâçéèêëîïôûùüœ' ]", ' ', obj).replace("'", ' ').split() if len(w) > 2 and w not in ('les', 'des', 'une', 'avec', 'pour', 'sur')]
        nom = script.norm(mots[0]) if mots else ''   # le mot principal (« bouquet » dans « bouquet de fleurs de la mariée ») doit correspondre : jamais une robe pour un bouquet
        cands = [c for c in cands if c[0] > 0 and (not nom or nom in POSES[c[1]]['tags'] or any(t.startswith(nom[:5]) for t in POSES[c[1]]['tags']))]; hit = max(cands)[1] if cands else None
        if hit:   # l'objet entier dans l'image (un objet large, comme un bouquet ou une voiture, n'est jamais coupé)
            sz = POSES[hit]['size']; hh = int(min(1450, 980 * sz[1] / max(1, sz[0])) / 4) * 4
            paste(fr, pose_img(hit, hh), 540, 1100, 1.0, 1.0 + 0.04 * eo(prog(lt, 0, d)))
        elif 'telephone' in obj or 'téléphone' in obj: paste(fr, gfx.phone_with(gfx.app_screen([s.get('object', '')])), 540, 1100, 1.0, 1.1)
        else:
            o = gfx.draw_object(obj)
            if o is not None: paste(fr, o, 540, 1050, eo(prog(lt, 0, 0.3)), 1.0 + 0.05 * eo(prog(lt, 0, d)))
            sticker(fr, s.get('object', ''), 540, 1700 if o is not None else 900, lt, 0.15, 70 if o is not None else 90, (30, 30, 30))
        fx_draw(fr, s.get('fx', []), lt, (540, 600)); return fr
    if k == 'pensee_ecran':   # l'écran du téléphone + la tête du personnage qui pense, dans une bulle, + sa pensée écrite
        fr = draw(dict(s, kind='screen', dur=99), 9.0).convert('RGBA'); p = POSES[s['tete']]
        H0 = 1500; im = pose_img(s['tete'], H0); w = im.width
        hs = int(H0 * (0.22 if p['posture'] in ('assis', 'banc') else {'pied': 0.15, 'buste': 0.32}.get(p['frame'], 0.45)))   # assis : la tête prend plus de place dans l'image
        top = (im.getchannel('A').getbbox() or (0, 0, w, H0))[1]   # haut de la tête (chignon compris) ; le visage est un peu plus bas
        cx = int(w * p.get('head_x', 0.5)); cy = top + int(hs * (0.82 if p['posture'] in ('assis', 'banc') else 0.78))
        tete = im.crop((cx - hs // 2, cy - hs // 2, cx + hs // 2, cy + hs // 2)).resize((330, 330), Image.LANCZOS)
        ro = 1.5 * math.sin(lt * 1.6); tete = tete.rotate(ro, resample=Image.BICUBIC)   # la tête bouge doucement, l'air de réfléchir
        bx, by = 250, 1590 + int(8 * math.sin(lt * 1.3)); d = ImageDraw.Draw(fr)
        for i, (rx, ry, rr) in enumerate([(420, 1400, 22), (470, 1330, 15), (510, 1275, 10)]):   # petites bulles vers le téléphone
            if lt > 0.15 * i: d.ellipse((rx - rr, ry - rr, rx + rr, ry + rr), fill=(255, 255, 255, 235), outline=(60, 60, 60, 255), width=3)
        d.ellipse((bx - 190, by - 190, bx + 190, by + 190), fill=(255, 255, 255, 240), outline=(60, 60, 60, 255), width=5)
        m = Image.new('L', (330, 330), 0); ImageDraw.Draw(m).ellipse((0, 0, 329, 329), fill=255)
        fond = Image.new('RGBA', (330, 330), (235, 228, 215, 255)); fond.alpha_composite(tete); fond.putalpha(m); fr.alpha_composite(fond, (bx - 165, by - 165))
        line = s['line']; gfx.subtitle(fr, s['who'], line['text'], lt - s.get('lead', 0) + 0.1, True)
        return fr
    if k == 'phonecall':
        fr = background(s, lt, blur=8); paste(fr, gfx.phone_with(gfx.call_screen(gfx.nom(s['who']))), 540, 1100, 1.0, 1.1)
        line = s['line']; gfx.subtitle(fr, s['who'], line['text'], lt - s['lead'] + 0.1); return fr
    # plans avec personnages
    acts = s.get('actors', []); line = s.get('line'); lead = s.get('lead', 0)
    st = lt - lead if line else None
    mode = s.get('mode', 'wide' if k == 'wide' else 'close')
    # plan de coupe (réaction sur un mot) pendant la réplique
    for c in s.get('cuts', []):
        if c['t'] <= lt < c['t'] + 1.3:
            from director import pick, close_actor
            kk = c.get('key') or pick(c['who'], c['actions'] + c.get('props', []), 'buste', c.get('posture'), need_mouth=False)
            if kk:
                from director import orient
                fr = background(s, lt, blur=5, zoom=0.4, pan=c.get('pan', 0)); a = orient(close_actor(c['who'], kk, x=540 - 110 * c.get('look_dir', 0)), c.get('look_dir', 0)); head = draw_actor(fr, a, lt)
                fx_draw(fr, [(c['t'] + 0.05, x) for x in c['actions']], lt, head)
                if line: gfx.subtitle(fr, s['who'], line['text'], lt - lead + 0.3, line.get('thought'))
                return gfx.shake(fr, lt, c['t'], 0.4, 10) if 'choc' in c['actions'] or 'sursaut' in c['actions'] else fr
    # pieds visibles (personnages en pied) : le décor est cadré sur son sol libre, même pendant une réplique, pour que personne ne flotte
    debout = [a['by'] for a in acts if not (a.get('fg') or a.get('fgwide') or a.get('silhouette')) and POSES.get(a['key'].split('@')[0], {}).get('frame') == 'pied' and a['by'] < H + 40]
    fr, genoux = background_sol(s, lt, min(debout)) if debout else (None, False)
    if fr is not None:
        if mode in ('close', 'two'): fr = fr.filter(ImageFilter.GaussianBlur(4))
        if genoux: acts = [dict(a, by=a['by'] + int(0.2 * a['h'])) if not a.get('fg') else a for a in acts]   # sol trop étroit : cadré aux genoux, jamais de pieds en l'air
    elif mode in ('close', 'two') or (k == 'close' and len(acts) == 1): fr = background(s, lt, blur=5, zoom=0.4 + 0.03 * prog(lt, 0, d), pan=s.get('pan', 0))
    else: z, hy = DECOR_LARGE.get(decor_file(s['decor']), (0.1, 0.45)); fr = background(s, lt, zoom=z, haut=hy)
    head = (540, 400)
    for a in acts:
        a2 = a
        if a.get('speaker') and s.get('switch'):
            for tt, k2 in s['switch']:
                if lt >= tt:
                    from director import orient
                    a2 = dict(a, key=k2, flip=False); a2.update({kk: vv for kk, vv in close_like(a, k2).items()}); a2 = orient(a2, a.get('look_dir', 0))
        hh = draw_actor(fr, a2, lt, line, s.get('tagfx', []), st)
        if a.get('speaker') or len(acts) == 1: head = hh
    fx_draw(fr, s.get('fx', []) + [(t, g) for t, g in s.get('tagfx', [])], lt, head)
    if line and k == 'line': gfx.subtitle(fr, s['who'], line['text'], lt - lead + 0.1, line.get('thought'))
    if s.get('card') and lt < 1.6: sticker(fr, s['card'].title(), 540, 420, lt, 0.2, 60, gfx.FONCE)
    return fr
def close_like(a, k2):
    from director import close_actor
    b = close_actor(a['who'], k2, x=a.get('face_x', 540), tight=a.get('tight', False), scale=a.get('scale', 1.0))
    r = {'h': b['h'], 'by': b['by'], 'x': b['x']}
    if a.get('scale', 1.0) != 1.0: r['by'] = a['by'] - a['h'] + b['h']
    return r
# ---------------- rendu parallèle ----------------
def render_segment(args):
    shots, a, b, out = args
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-tune', 'animation', out], stdin=subprocess.PIPE)
    for n in range(a, b):
        s, lt = frame_of(shots, n / FPS)
        A_ = min(1, lt / 0.15, (s['dur'] - lt) / 0.15) if s['kind'] not in ('line',) else 1
        fr = draw(s, lt).convert('RGB')
        if A_ < 1 and s['kind'] in ('title', 'screen', 'endcard', 'insert'): fr = Image.blend(Image.new('RGB', fr.size), fr, max(0, A_))
        ff.stdin.write(fr.tobytes())
        if n % 300 == 299: pose_img.cache_clear(); decor.cache_clear()
    ff.stdin.close(); ff.wait(); return out
def seg_hash(shots, a, b):
    """Empreinte d'un morceau (a → b images) : les plans qui le touchent (+ taille des voix). Inchangée = morceau gardé."""
    import hashlib
    t0, t1 = a / FPS, b / FPS; part = [s for s in shots if s['t0'] < t1 and s['t0'] + s['dur'] > t0]
    wav = [os.path.getsize(s['line']['wav']) if s.get('line', {}).get('wav') and os.path.exists(s['line']['wav']) else 0 for s in part]
    return hashlib.md5(json.dumps([part, wav, a, b], sort_keys=True, default=str).encode()).hexdigest()[:12]
def seg_ok(j):
    f = j[3] + '.ok'
    return os.path.exists(f) and open(f).read().strip() == j[4]
def video(shots, tot, work, workers=2, log=print, seg=360, part=None):
    """Rendu par morceaux de 12 s. Seuls les morceaux dont les plans ont changé sont refaits, puis tout est recollé (ffmpeg)."""
    n = int(tot * FPS); jobs = []
    for a in range(0, n, seg): jobs.append((shots, a, min(n, a + seg), f'{work}/seg_{a:06d}.mp4', seg_hash(shots, a, min(n, a + seg))))
    todo = [j for j in jobs if not seg_ok(j)]
    if part: todo = [j for k, j in enumerate(jobs) if k % part[1] == part[0] and not seg_ok(j)]
    zones = ', '.join(f'{int(j[1] / FPS // 60)}:{int(j[1] / FPS % 60):02d}–{int(j[2] / FPS // 60)}:{int(j[2] / FPS % 60):02d}' for j in todo[:8]) + (' …' if len(todo) > 8 else '')
    log(f'rendu : {n} images, {len(todo)} morceau(x) sur {len(jobs)} à calculer' + (f' ({zones})' if todo and len(todo) < len(jobs) else ''))
    from multiprocessing import Pool
    with Pool(workers) as p:
        for out in p.imap_unordered(render_segment, [j[:4] for j in todo]):
            open(out + '.ok', 'w').write(next(j[4] for j in todo if j[3] == out)); log('  morceau fini ' + os.path.basename(out))
    if part: return None
    missing = [j[3] for j in jobs if not seg_ok(j)]
    if missing: raise RuntimeError(f'morceaux manquants : {len(missing)}')
    with open(f'{work}/list.txt', 'w') as f:
        for j in jobs: f.write(f"file '{os.path.basename(j[3])}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/silent.mp4'], check=True)
    return f'{work}/silent.mp4'
def moment(s, avant_changement=False):
    """Instant montré en image fixe : vers 60 % du plan, jamais pendant une réaction coupée (on verrait quelqu'un d'autre) ;
    avant_changement : avant le premier changement de pose sur un mot (pour juger la pose de départ)."""
    d = s['dur']; want = min(d - 0.05, max(0.6, d * 0.6)); cuts = [c['t'] for c in s.get('cuts', [])]
    end = min([t for t, _ in s.get('switch', [])] + [d]) - 0.05 if avant_changement else d - 0.05
    ok = [i / 10 for i in range(3, int(d * 10)) if i / 10 <= end and not any(c - 0.05 <= i / 10 < c + 1.35 for c in cuts)]
    return min(ok, key=lambda t: abs(t - want)) if ok else want
def contact(shots, path, cols=8):
    """Planche d'aperçu : une image par plan, pour vérifier la mise en scène avant le rendu complet."""
    ims = []
    for i, s in enumerate(shots):
        lt = moment(s); fr = draw(s, lt).convert('RGB').resize((216, 384)); ims.append((i, s, fr))
    rows = (len(ims) + cols - 1) // cols; c = Image.new('RGB', (cols * 216, rows * 410), 'white'); d = ImageDraw.Draw(c)
    for i, s, fr in ims:
        x, y = (i % cols) * 216, (i // cols) * 410; c.paste(fr, (x, y)); d.text((x + 4, y + 390), f"{i} {s['kind']} {s.get('who', '')} {s['dur']:.1f}s", fill='black')
    c.save(path); return path

# ---------------- têtes tournées (LivePortrait) ----------------
def key_color(im):
    """Couleur de fond la plus éloignée des couleurs du personnage (pour le détourage)."""
    a = np.array(im.convert('RGBA')).astype(np.float32); px = a[a[..., 3] > 128][:, :3]
    if len(px) > 20000: px = px[np.random.default_rng(0).choice(len(px), 20000, replace=False)]
    best, bd = (0, 255, 0), -1
    for c in [(0, 255, 0), (255, 0, 255), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)]:
        d = np.sqrt(((px - np.array(c, np.float32)) ** 2).sum(1)); score = (d < 110).mean()
        if bd < 0 or score < bd: best, bd = c, score
    return best
def prepare_turns(shots, log=print):
    """Crée les variantes « tête tournée » dont la mise en scène a besoin (une seule fois, gardées dans assets/poses/tourne)."""
    need = set()
    for s in shots:
        for a in s.get('actors', []):
            for k in (a.get('key'), a.get('stop_key')):
                if k and '@' in k: need.add(k)
        for sw in s.get('switch', []): pass
    out = f'{A}/poses/tourne'; os.makedirs(out, exist_ok=True)
    todo = [k for k in sorted(need) if not os.path.exists(f'{out}/{k}.webp')]
    lp = os.environ.get('STUDIO_LIVEPORTRAIT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp', 'lpgen.py'))
    if not todo: return
    if not os.path.exists(lp): log('têtes tournées : outil LivePortrait absent, poses d\'origine utilisées'); return
    tmp = f'{out}/_tmp'; os.makedirs(tmp, exist_ok=True); jobs = []; boxes = {}; bgs = {}
    for k in todo:
        from director import parse_variant
        base, turn, eyes, up = parse_variant(k); p = POSES[base]
        im = Image.open(f'{A}/poses/{base}.webp').convert('RGBA'); w, h = im.size
        frac = {'pied': 0.42, 'buste': 0.75, 'visage': 1.0}.get(p['frame'], 0.5); box = (0, 0, w, int(h * frac)); boxes[k] = box
        bgc = key_color(im.crop(box)); bgs[k] = bgc; b = Image.new('RGBA', box[2:], bgc + (255,)); b.alpha_composite(im.crop(box)); b.convert('RGB').save(f'{tmp}/{base}.png')   # fond uni absent du personnage : détourage facile
        y = 24 * turn; ex = -26 * eyes; pt = -9 * up; ey = 15 * up   # signes vérifiés à l'œil sur LivePortrait
        jobs.append(f'{tmp}/{k}.png|{tmp}/{base}.png|x|x|{pt}|{y}|0|0|0|0|0|0|0|{ex}|{ey}')
    jobs2 = []
    for k in todo:
        base = k.split('@')[0]; p = POSES[base]
        sm = 0 if set(p['tags']) & {'sourire', 'rire', 'content', 'grand_sourire'} else -0.2
        # bouche ouverte fabriquée à partir de l'image tournée elle-même : les yeux ne bougent pas
        if p['mouth']: jobs2.append(f'{tmp}/{k}_o.png|{tmp}/{k}.png|x|0.38|0|0|0|{sm}|0|0|0|0|0|0|0')
    open(f'{tmp}/jobs.txt', 'w').write('\n'.join(jobs) + '\n'); open(f'{tmp}/jobs2.txt', 'w').write('\n'.join(jobs2) + '\n')
    log(f'têtes tournées : {len(todo)} poses à préparer')
    subprocess.run(['python3', lp, f'{tmp}/jobs.txt'], cwd=os.path.dirname(lp), capture_output=True)
    subprocess.run(['python3', lp, f'{tmp}/jobs2.txt'], cwd=os.path.dirname(lp), capture_output=True)
    for k in todo:   # on ne garde de l'image « bouche ouverte » que la bouche : le reste du visage est identique
        c, o = f'{tmp}/{k}.png', f'{tmp}/{k}_o.png'
        if os.path.exists(c) and os.path.exists(o): mouth_only(c, o)
    n = 0
    for k, box in boxes.items():
        base = Image.open(f'{A}/poses/{k.split("@")[0]}.webp').convert('RGBA'); alpha = None; band = None
        for suf in ('', '_o'):
            f = f'{tmp}/{k}{suf}.png'
            if not os.path.exists(f): continue
            g = Image.open(f).convert('RGBA').resize(box[2:])
            if alpha is None:   # la tête a bougé : nouveau détourage par le fond uni (sinon on voit le fond autour des cheveux)
                import cv2
                ba = np.array(base.crop(box).getchannel('A')).astype(np.float32)
                ar = np.array(g.convert('RGB')).astype(np.float32); dist = np.sqrt(((ar - np.array(bgs[k], np.float32)) ** 2).sum(2))
                na = np.clip((dist - 60) / 50, 0, 1) * 255; na = cv2.GaussianBlur(na, (0, 0), 1.0)
                hgt = ba.shape[0]; w8 = np.clip((np.arange(hgt) - hgt * 0.8) / (hgt * 0.15), 0, 1)[:, None]
                ba = na * (1 - w8) + ba * w8
                hard = (ba > 128).astype(np.uint8); core = cv2.erode(hard, np.ones((5, 5), np.uint8))
                ba = cv2.GaussianBlur(core.astype(np.float32) * 255, (0, 0), 1.2) * (1 - w8) + ba * w8   # bord resserré
                tint = (dist < 150).astype(np.uint8) * (w8[:, 0] < 0.5)[:, None].astype(np.uint8)   # pixels encore teintés par le fond (entre les mèches)
                ba = ba * (1 - tint)
                band = (((cv2.dilate(hard, np.ones((9, 9), np.uint8)) - cv2.erode(hard, np.ones((9, 9), np.uint8))) > 0) | (cv2.dilate(tint, np.ones((5, 5), np.uint8)) > 0)).astype(np.uint8)
                alpha = Image.fromarray(ba.clip(0, 255).astype(np.uint8))
            if band is not None:   # couleurs du bord reprises de l'intérieur : plus de liseré de la couleur du fond
                rgb = cv2.inpaint(np.array(g.convert('RGB')), band, 4, cv2.INPAINT_TELEA); g = Image.fromarray(rgb).convert('RGBA')
            # bas du cadre (corps, objets) : on garde les pixels d'origine, seule la tête vient de LivePortrait
            orig = np.array(base.crop(box).convert('RGB')).astype(np.float32); lpx = np.array(g.convert('RGB')).astype(np.float32)
            hh = orig.shape[0]; wb = np.clip((np.arange(hh) - hh * 0.62) / (hh * 0.2), 0, 1)[:, None, None]
            g = Image.fromarray((lpx * (1 - wb) + orig * wb).clip(0, 255).astype(np.uint8)).convert('RGBA')
            g.putalpha(alpha)
            im = base.copy(); im.paste(g, box[:2]); im.save(f'{out}/{k}{suf}.webp', 'WEBP', quality=88); n += suf == ''
    log(f'têtes tournées : {n} prêtes')

def mouth_only(closed_path, open_path):
    """Remplace l'image « bouche ouverte » par l'image fermée + seulement la zone de la bouche
    (là où l'image change le plus quand la bouche s'ouvre)."""
    import cv2
    ci = Image.open(closed_path).convert('RGB'); c = np.array(ci).astype(np.float32); o = np.array(Image.open(open_path).convert('RGB').resize(ci.size)).astype(np.float32)
    D = cv2.GaussianBlur(np.abs(c - o).mean(2), (0, 0), 4)
    py, px = np.unravel_index(np.argmax(D), D.shape); peak = D[py, px]
    if peak < 15: return
    m = (D > peak * 0.25).astype(np.uint8); n, lab = cv2.connectedComponents(m); m = (lab == lab[py, px]).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((11, 11), np.uint8)); m = cv2.GaussianBlur(m, (0, 0), 5)[..., None] / 255.0
    out = (c * (1 - m) + o * m).clip(0, 255).astype(np.uint8); Image.fromarray(out).save(open_path)
