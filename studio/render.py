"""Rendu image par image des plans, en parallèle, puis assemblage avec le son."""
import os, math, json, subprocess, re
from functools import lru_cache
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
import gfx
from gfx import W, H, FPS, paste, sticker, prog, eo, lerp
from director import POSES, GROUND
A = gfx.A
DECOR_ALIAS = [('KIOSQUE', 'KIOSQUE'), ('ATELIER', 'ATELIER'), ('MARCHE', 'MARCHE'), ('CABINE', 'CABINE'), ('BUREAU', 'BUREAU'), ('VILLA', 'VILLA'),
               ('SHOWROOM', 'SHOWROOM'), ('VOITURE', 'RUE'), ('RUE', 'RUE')]
def decor_file(name):
    n = name.upper()
    for k, v in DECOR_ALIAS:
        if k in n: return v
    return 'KIOSQUE'
@lru_cache(16)
def decor(name, moment, blur):
    im = Image.open(f'{A}/decors/{decor_file(name)}.jpg').convert('RGB'); s = max(2050 / im.height, (W + 120) / im.width)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS); im = gfx.tint(im, moment)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return im
def background(s, lt, blur=0, zoom=0.0):
    im = decor(s['decor'], s['moment'], blur); x = int((im.width - W) / 2 + 16 * math.sin(lt * 0.25)); y = int((im.height - H) * 0.6)
    fr = im.crop((x, y, x + W, y + H))
    if zoom:
        fr = fr.resize((int(W * (1 + zoom)), int(H * (1 + zoom))), Image.BILINEAR); fr = fr.crop((int(W * zoom / 2), int(H * zoom / 2), int(W * zoom / 2) + W, int(H * zoom / 2) + H))
    return fr
@lru_cache(96)
def pose_img(key, h, opened=False, flip=False):
    p = f'{A}/poses/{key}{"_o" if opened else ""}.webp'
    if not os.path.exists(p): p = f'{A}/poses/{key}.webp'
    im = Image.open(p).convert('RGBA'); im = im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
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
    opened = a.get('speaker') and speaking_t is not None and POSES[key]['mouth'] and mouth_open(line, speaking_t)
    breath = 1 + 0.006 * math.sin(lt * 2 * math.pi / 3.4 + a['x'] * 0.01)
    dx, dy, sc, rot = body_motion(tags, lt) if a.get('speaker') else (0, 0, 1, 0)
    if a.get('walk'):
        cyc = WALK.get(a['walk'])
        if cyc: key = cyc[int(lt * 3.4) % 4]
    im = pose_img(key, int(h * sc * breath / 4) * 4, bool(opened), flip)
    cx = a['x'] + dx + a.get('vx', 0) * lt; by = a['by'] + dy
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC, center=(im.width / 2, im.height))
    paste(fr, im, cx, by - im.height / 2, 1.0, 1.0, sh=not a.get('back'))
    return cx, by - h  # sommet de la tête
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
        if any(c in txt for c in '–✔✖★[') or 'sounsouni' in txt.lower():
            fr = background(s, lt, blur=8); lines = [x.strip() for x in re.split(r' – | - ', txt)]
            title = 'Sounsouni'
            if lines and lines[0].lower().startswith('sounsouni'): title = lines[0]; lines = lines[1:]
            paste(fr, gfx.phone_with(gfx.app_screen(lines, title[:22])), 540, lerp(1300, 1100, eo(prog(lt, 0, 0.35))), 1.0, 1.15)
            return fr
        fr = gfx.tint(background(s, lt, blur=10), 'nuit'); f = gfx.font(gfx.FB, 120)
        for i, l in enumerate(gfx.wrap(txt, f, 950)): ImageDraw.Draw(fr).text((540, 920 + i * 140), l, font=f, fill='white', anchor='mm')
        return fr
    if k == 'insert':
        fr = background(s, lt, blur=4, zoom=0.1); obj = gfx.norm if False else s.get('object', '').lower()
        hit = None
        for key, p in POSES.items():
            if p['frame'] == 'objet' and any(w in obj for w in p['tags']): hit = key; break
        if hit: paste(fr, pose_img(hit, 1450), 540, 1100, 1.0, 1.0 + 0.04 * eo(prog(lt, 0, d)))
        elif 'telephone' in obj or 'téléphone' in obj: paste(fr, gfx.phone_with(gfx.app_screen([s.get('object', '')])), 540, 1100, 1.0, 1.1)
        else:
            o = gfx.draw_object(obj)
            if o is not None: paste(fr, o, 540, 1050, eo(prog(lt, 0, 0.3)), 1.0 + 0.05 * eo(prog(lt, 0, d)))
            sticker(fr, s.get('object', ''), 540, 1700 if o is not None else 900, lt, 0.15, 70 if o is not None else 90, (30, 30, 30))
        fx_draw(fr, s.get('fx', []), lt, (540, 600)); return fr
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
            kk = pick(c['who'], c['actions'], 'buste', None, need_mouth=False)
            if kk:
                fr = background(s, lt, blur=3, zoom=0.06); a = close_actor(c['who'], kk); head = draw_actor(fr, a, lt)
                fx_draw(fr, [(c['t'] + 0.05, x) for x in c['actions']], lt, head)
                if line: gfx.subtitle(fr, s['who'], line['text'], lt - lead + 0.3, line.get('thought'))
                return gfx.shake(fr, lt, c['t'], 0.4, 10) if 'choc' in c['actions'] or 'sursaut' in c['actions'] else fr
    if mode in ('close', 'two'): fr = background(s, lt, blur=3, zoom=0.06 + 0.03 * prog(lt, 0, d))
    else: fr = background(s, lt, zoom=0.1)
    head = (540, 400)
    for a in acts:
        a2 = a
        if a.get('speaker') and s.get('switch'):
            for tt, k2 in s['switch']:
                if lt >= tt: a2 = dict(a, key=k2); a2.update({kk: vv for kk, vv in close_like(a, k2).items()})
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
def video(shots, tot, work, workers=2, log=print, seg=360):
    n = int(tot * FPS); jobs = []
    for a in range(0, n, seg): jobs.append((shots, a, min(n, a + seg), f'{work}/seg_{a:06d}.mp4'))
    todo = [j for j in jobs if not os.path.exists(j[3] + '.ok')]
    log(f'rendu : {n} images, {len(todo)} morceaux à calculer')
    from multiprocessing import Pool
    with Pool(workers) as p:
        for out in p.imap_unordered(render_segment, todo): open(out + '.ok', 'w').close(); log('  morceau fini ' + os.path.basename(out))
    with open(f'{work}/list.txt', 'w') as f:
        for j in jobs: f.write(f"file '{os.path.basename(j[3])}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/silent.mp4'], check=True)
    return f'{work}/silent.mp4'
def contact(shots, path, cols=8):
    """Planche d'aperçu : une image par plan (milieu du plan), pour vérifier la mise en scène avant le rendu complet."""
    ims = []
    for i, s in enumerate(shots):
        lt = min(s['dur'] - 0.05, max(0.6, s['dur'] * 0.6)); fr = draw(s, lt).convert('RGB').resize((216, 384)); ims.append((i, s, fr))
    rows = (len(ims) + cols - 1) // cols; c = Image.new('RGB', (cols * 216, rows * 410), 'white'); d = ImageDraw.Draw(c)
    for i, s, fr in ims:
        x, y = (i % cols) * 216, (i // cols) * 410; c.paste(fr, (x, y)); d.text((x + 4, y + 390), f"{i} {s['kind']} {s.get('who', '')} {s['dur']:.1f}s", fill='black')
    c.save(path); return path
