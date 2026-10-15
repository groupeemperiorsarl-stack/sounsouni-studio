import re
"""Outils de dessin : polices, textes, bulles, autocollants, ombres, effets, écrans de téléphone, écran de fin."""
import os, math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
W, H, FPS = 1080, 1920, 30
FB = A + '/ui/Poppins-Bold.ttf'; FM = A + '/ui/Poppins-Medium.ttf'
VERT = (46, 160, 70); FONCE = (20, 110, 60); ORANGE = (240, 140, 20); ENCRE = (30, 30, 30)
COL = {'BAKARY': (32, 72, 200), 'AWA': (230, 120, 20), 'MODIBO': (200, 40, 40), 'DIASABI': (60, 140, 60), 'FATIM': (200, 40, 120),
       'MIMI': (200, 120, 20), 'SEYDOU': (20, 120, 60), 'KADI': (130, 30, 50), 'MOUSSA': (60, 120, 200), 'KARIM': (40, 60, 120),
       'SALI': (30, 120, 190), 'VENDEUSE': (200, 30, 30), 'VOIX_OFF': FONCE}
NOM = {'BAKARY': 'Bakary', 'AWA': 'Awa', 'MODIBO': 'Modibo', 'DIASABI': 'Diasabi', 'FATIM': 'Fatim', 'MIMI': 'Mimi', 'SEYDOU': 'Seydou',
       'KADI': 'Tantie Kadi', 'MOUSSA': 'Moussa', 'KARIM': 'Karim', 'SALI': 'Sali', 'VENDEUSE': 'La vendeuse', 'VOIX_OFF': ''}
def nom(w): return NOM.get(w, w.replace('_', ' ').title())
def col(w): return COL.get(w, (90, 90, 90))
@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, size)
def eo(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def back(x): x = max(0, min(1, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def prog(t, t0, d): return max(0.0, min(1.0, (t - t0) / max(1e-6, d)))
def lerp(a, b, k): return a + (b - a) * k
@lru_cache(None)
def ICON(): return Image.open(A + '/ui/icon.png').convert('RGBA')
@lru_cache(64)
def shadow(im_id, w, h, alpha_bytes, blur=14, op=0.3):
    a = Image.frombytes('L', (w, h), alpha_bytes).point(lambda p: int(p * op)); s = Image.new('RGBA', (w, h), (0, 0, 0, 0)); s.putalpha(a)
    return s.filter(ImageFilter.GaussianBlur(blur))
def paste(fr, im, cx, cy, a=1.0, s=1.0, rot=0, sh=True):
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda p: int(p * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if sh and im.width * im.height < 4_000_000:
        sd = im.getchannel('A').point(lambda p: int(p * 0.28)).filter(ImageFilter.GaussianBlur(12)); s2 = Image.new('RGBA', im.size, (0, 0, 0, 0)); s2.putalpha(sd)
        fr.paste(s2, (x + 6, y + 14), s2)
    fr.paste(im, (x, y), im)
def wrap(text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if f.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines
@lru_cache(256)
def bubble(who, text, thought=False):
    f = font(FB, 46); lines = wrap(text, f, 860); lh = 60; h = len(lines) * lh + 46; w = 960
    c = col(who); L = Image.new('RGBA', (W, h + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    fill = (255, 255, 255, 240) if not thought else (240, 235, 255, 235)
    d.rounded_rectangle([60, 46, 60 + w, 46 + h], radius=36, fill=fill, outline=c, width=6)
    for i, l in enumerate(lines): d.text((W / 2, 46 + 23 + i * lh + lh / 2), l, font=f, fill=ENCRE, anchor='mm')
    n = nom(who) + (' · pensée' if thought else '')
    if n:
        tw = font(FB, 34).getlength(n) + 44; d.rounded_rectangle([90, 12, 90 + tw, 68], radius=28, fill=c); d.text((112, 40), n, font=font(FB, 34), fill='white', anchor='lm')
    return L
def subtitle(fr, who, text, lt, thought=False, y=240):
    k = eo(prog(lt, 0, 0.25)); b = bubble(who, text, thought)
    if k < 1: b = b.copy(); b.putalpha(b.getchannel('A').point(lambda p: int(p * k)))
    fr.paste(b, (0, int(y - 20 * (1 - k))), b)
@lru_cache(128)
def sticker_img(text, size, bgc, fg=(255, 255, 255)):
    f = font(FB, size); w = int(f.getlength(text) + 64); L = Image.new('RGBA', (w, size + 52), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w - 1, size + 51], radius=34, fill=bgc + (238,)); d.text((w / 2, (size + 52) / 2), text, font=f, fill=fg, anchor='mm')
    return L
def sticker(fr, text, x, y, lt, t0=0, size=86, bgc=(30, 30, 30)):
    k = prog(lt, t0, 0.25)
    if k <= 0: return
    paste(fr, sticker_img(text, size, bgc), x, y, eo(k), 0.5 + 0.5 * back(k), rot=-7, sh=False)
@lru_cache(None)
def heart():
    D = Image.new('RGBA', (90, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(D); c = (235, 60, 90, 240)
    d.ellipse([4, 4, 48, 48], fill=c); d.ellipse([42, 4, 86, 48], fill=c); d.polygon([(8, 34), (82, 34), (45, 76)], fill=c); return D
def hearts(fr, cx, cy, lt, a=1.0):
    for i in range(6):
        k = ((lt * 0.6 + i / 6) % 1); x = cx + 260 * math.sin(i * 2.1 + lt) ; y = cy - k * 500
        paste(fr, heart(), x, y, a * (1 - k), 0.6 + 0.6 * k, sh=False)
def sweat(fr, x, y, lt, a=1.0):
    for i in range(3):
        k = ((lt * 1.3 + i * 0.33) % 1); D = Image.new('RGBA', (40, 60), (0, 0, 0, 0)); dd = ImageDraw.Draw(D)
        dd.ellipse([6, 16, 34, 56], fill=(120, 190, 255, 230)); dd.polygon([(20, 0), (8, 28), (32, 28)], fill=(120, 190, 255, 230))
        paste(fr, D, x + i * 55 - 55, y + k * 120, a * (1 - k), sh=False)
def stars(fr, cx, cy, lt, a=1.0, r=170, n=6):
    for i in range(n):
        ang = i * 6.283 / n + lt * 1.5; x = cx + r * math.cos(ang); y = cy + r * 0.6 * math.sin(ang); s = 10 + 6 * math.sin(lt * 6 + i)
        D = Image.new('RGBA', (60, 60), (0, 0, 0, 0)); ImageDraw.Draw(D).regular_polygon((30, 30, s + 8), 4, rotation=45, fill=(255, 215, 80, 240)); paste(fr, D, x, y, a, sh=False)
def smoke(fr, x, y, lt, a=1.0, n=6, c=(150, 150, 150)):
    for i in range(n):
        k = (lt * 0.5 + i / n) % 1; r = int(30 + k * 90); D = Image.new('RGBA', (r * 2 + 40, r * 2 + 40), (0, 0, 0, 0))
        ImageDraw.Draw(D).ellipse([20, 20, r * 2 + 19, r * 2 + 19], fill=c + (int(170 * (1 - k)),)); paste(fr, D.filter(ImageFilter.GaussianBlur(8)), x + 25 * math.sin(i * 1.7 + lt * 2), y - k * 420, a, sh=False)
def redface(fr, x, y, lt, a=1.0):
    k = prog(lt, 0.1, 0.8); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(L).ellipse([x - 200, y - 200, x + 200, y + 180], fill=(230, 40, 30, int(90 * k * a)))
    L = L.filter(ImageFilter.GaussianBlur(40)); fr.paste(L, (0, 0), L)
def bulb(fr, x, y, lt, a=1.0):
    p = Image.new('RGBA', (160, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(p); d.ellipse([10, 0, 150, 140], fill=(255, 230, 80)); d.rectangle([50, 130, 110, 190], fill=(160, 160, 170))
    paste(fr, p, x, y, a * eo(prog(lt, 0, 0.3)), 1 + 0.05 * math.sin(lt * 8), sh=False)
def speedlines(fr, y0, y1, lt, a=1.0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); r = random.Random(int(lt * 10))
    for i in range(14):
        y = r.randint(y0, y1); x = r.randint(0, W); d.line([(x, y), (x + r.randint(120, 320), y)], fill=(255, 255, 255, int(160 * a)), width=5)
    fr.paste(L, (0, 0), L)
def shake(fr, lt, t0, dur, amp=12):
    if not (t0 <= lt < t0 + dur): return fr
    k = 1 - (lt - t0) / dur; dx = int(amp * k * math.sin(lt * 70)); dy = int(amp * k * math.cos(lt * 53))
    out = Image.new('RGB', fr.size, (0, 0, 0)); out.paste(fr, (dx, dy)); return out
def flash(fr, k):
    return Image.blend(fr.convert('RGB'), Image.new('RGB', fr.size, (255, 255, 255)), max(0, min(1, k)))
def tint(fr, moment):
    if moment in ('soir', 'nuit'):
        a = np.asarray(fr).astype(np.float32); m = (0.62, 0.52, 0.62) if moment == 'soir' else (0.38, 0.40, 0.55)
        a = a * np.array(m) + np.array([18, 6, 28]); return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return fr
# ---------------- téléphone ----------------
SW, SH = 600, 1200
@lru_cache(None)
def phone_frame():
    P = Image.new('RGBA', (SW + 60, SH + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle([0, 0, SW + 59, SH + 79], radius=70, fill=(25, 25, 30)); d.rounded_rectangle([8, 8, SW + 51, SH + 71], radius=64, outline=(70, 70, 80), width=4)
    d.rounded_rectangle([(SW + 60) / 2 - 60, 22, (SW + 60) / 2 + 60, 44], radius=11, fill=(10, 10, 12)); return P
def phone_with(ui):
    P = phone_frame().copy(); m = Image.new('L', (SW, SH), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, SW - 1, SH - 1], radius=48, fill=255)
    P.paste(ui.convert('RGBA'), (30, 40), m); return P
def app_screen(lines, title='Sounsouni'):
    """Écran générique de l'application : lignes de texte ; « ✔ » / « ✖ » / « [Bouton] » / « ★★★★★ » reconnus."""
    S = Image.new('RGBA', (SW, SH), (255, 255, 255, 255)); d = ImageDraw.Draw(S)
    d.rectangle([0, 0, SW, 200], fill=FONCE); ic = ICON().resize((76, 76), Image.LANCZOS); S.paste(ic, (40, 100), ic); d.text((132, 110), title, font=font(FB, 44), fill=(255, 255, 255))
    y = 250
    for l in lines:
        l = l.strip()
        if not l: continue
        if l.startswith('[') and l.endswith(']'):
            d.rounded_rectangle([70, y, 530, y + 90], radius=45, fill=FONCE); d.text((300, y + 45), l.strip('[]'), font=font(FB, 38), fill=(255, 255, 255), anchor='mm'); y += 120; continue
        good = '✔' in l; bad = '✖' in l; star = '★' in l
        l2 = l.replace('✔', '').replace('✖', '').strip()
        if star:
            n = l.count('★'); d.text((300, y + 30), '★' * n if False else '', font=font(FB, 40), fill=ENCRE, anchor='mm')
            for i in range(n):
                cx = 300 + (i - (n - 1) / 2) * 80; pts = [(cx + 34 * math.cos(math.radians(-90 + j * 36)) * (1 if j % 2 == 0 else 0.45), y + 40 + 34 * math.sin(math.radians(-90 + j * 36)) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
                d.polygon(pts, fill=(240, 170, 20))
            l2 = l2.replace('★', '').strip(); y += 90
            if not l2: continue
        if good or bad:
            c = FONCE if good else (220, 50, 40); d.ellipse([240, y, 360, y + 120], fill=c)
            if good: d.line([(270, y + 62), (292, y + 86), (332, y + 38)], fill='white', width=12)
            else: d.line([(272, y + 32), (328, y + 88)], fill='white', width=12); d.line([(328, y + 32), (272, y + 88)], fill='white', width=12)
            y += 140
        f = font(FB if (good or bad or y < 330) else FM, 38 if len(l2) < 26 else 32)
        for ln in wrap(l2, f, 520): d.text((300, y + 24), ln, font=f, fill=ENCRE, anchor='mm'); y += 54
        y += 18
    return S
def call_screen(name):
    S = Image.new('RGBA', (SW, SH), (40, 50, 80, 255)); d = ImageDraw.Draw(S)
    d.text((300, 260), 'Appel entrant', font=font(FM, 40), fill=(220, 230, 255), anchor='mm'); d.ellipse([200, 360, 400, 560], fill=(200, 40, 120))
    d.text((300, 460), name[:1], font=font(FB, 110), fill='white', anchor='mm'); d.text((300, 640), name, font=font(FB, 70), fill='white', anchor='mm')
    d.ellipse([90, 880, 230, 1020], fill=(220, 50, 50)); d.ellipse([370, 880, 510, 1020], fill=(40, 180, 80)); return S
# ---------------- écran de fin ----------------
def badge(kind):
    B = Image.new('RGBA', (470, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(B)
    if kind == 'android':
        d.rounded_rectangle([0, 0, 469, 149], radius=34, fill=(25, 35, 25)); d.text((150, 26), 'Disponible sur', font=font(FM, 30), fill=(220, 230, 215)); d.text((150, 62), 'Android', font=font(FB, 52), fill='white')
        d.ellipse([50, 40, 110, 100], fill=(61, 220, 132))
    else:
        d.rounded_rectangle([0, 0, 469, 149], radius=34, fill='white'); d.rounded_rectangle([52, 28, 108, 122], radius=12, outline=(120, 130, 110), width=6)
        d.text((150, 22), 'iPhone', font=font(FB, 52), fill=(100, 110, 95)); d.text((150, 90), 'Bientôt', font=font(FB, 34), fill=ORANGE)
    return B
def end_screen(lt, step, slogan):
    fr = Image.new('RGB', (W, H), (236, 247, 226)); d = ImageDraw.Draw(fr)
    for i in range(18):
        r = random.Random(i); x, y = r.randint(0, W), r.randint(0, H); d.ellipse([x - 60, y - 60, x + 60, y + 60], fill=(214, 236, 196))
    paste(fr, ICON().resize((260, 260), Image.LANCZOS), 540, 330 + 8 * math.sin(lt * 2.5))
    d.text((540, 580), 'Sounsouni', font=font(FB, 120), fill=FONCE, anchor='mm')
    if slogan: d.text((540, 760), slogan, font=font(FB, 40), fill=FONCE, anchor='mm')
    if step >= 1:
        d.text((540, 870), "Téléchargez l'application sur", font=font(FB, 44), fill=ORANGE, anchor='mm'); d.text((540, 1010), 'sounsouni.pro', font=font(FB, 120), fill=FONCE, anchor='mm')
    if step >= 2:
        d.text((540, 1200), 'Ou achetez directement sur le site', font=font(FB, 42), fill=FONCE, anchor='mm')
        for i, kd in enumerate(['android', 'iphone']): paste(fr, badge(kd), 540, 1420 + i * 200, 1.0, 0.85)
    return fr

# ---- objets dessinés (plans « objet » sans image du catalogue) ----
def _cupcake(d, x, y, s=1.0, c=(240, 120, 160)):
    d.polygon([(x - 60 * s, y), (x + 60 * s, y), (x + 45 * s, y + 80 * s), (x - 45 * s, y + 80 * s)], fill=(200, 140, 70), outline=(120, 70, 30), width=4)
    for i in range(-2, 3): d.line([(x + i * 20 * s, y + 5), (x + i * 16 * s, y + 78 * s)], fill=(150, 95, 40), width=3)
    d.ellipse([x - 70 * s, y - 70 * s, x + 70 * s, y + 20 * s], fill=c, outline=(170, 60, 100), width=4)
    d.ellipse([x - 40 * s, y - 110 * s, x + 40 * s, y - 30 * s], fill=c, outline=(170, 60, 100), width=4)
    d.ellipse([x - 16 * s, y - 140 * s, x + 16 * s, y - 108 * s], fill=(200, 20, 40))
def _box(d, full):
    d.polygon([(150, 520), (850, 520), (800, 980), (200, 980)], fill=(196, 150, 95), outline=(110, 75, 40), width=6)
    d.polygon([(150, 520), (850, 520), (760, 420), (240, 420)], fill=(120, 85, 50) if not full else (230, 200, 160))
    d.polygon([(150, 520), (240, 420), (120, 300), (40, 470)], fill=(210, 168, 110), outline=(110, 75, 40), width=6)
    d.polygon([(850, 520), (760, 420), (880, 300), (960, 470)], fill=(210, 168, 110), outline=(110, 75, 40), width=6)
def draw_object(name):
    """Renvoie une image RGBA 1000x1100 de l'objet, ou None s'il est inconnu."""
    n = name.lower(); im = Image.new('RGBA', (1000, 1100), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if 'boite' in n or 'boîte' in n or 'carton' in n:
        vide = 'vide' in n; _box(d, not vide)
        if vide:
            for x, y in [(380, 470), (520, 455), (610, 480), (450, 490)]: d.ellipse([x, y, x + 18, y + 12], fill=(230, 190, 120))
        else:
            for i, x in enumerate((330, 500, 670)): _cupcake(d, x, 380, 0.9, [(240, 120, 160), (250, 230, 200), (150, 90, 60)][i])
        return im
    if 'gateau' in n or 'gâteau' in n or 'patisserie' in n or 'pâtisserie' in n:
        d.ellipse([120, 700, 880, 900], fill=(245, 245, 245), outline=(180, 180, 180), width=6)
        one = 'dernier' in n or 'un ' in n or 'seul' in n
        for i, x in enumerate([500] if one else [300, 500, 700]): _cupcake(d, x, 700, 1.3, [(240, 120, 160), (250, 230, 200), (150, 90, 60)][i % 3])
        return im
    if 'billet' in n or 'argent' in n or 'franc' in n:
        for i in range(3):
            x, y = 200 + i * 40, 380 + i * 60
            d.rounded_rectangle([x, y, x + 600, y + 300], 20, fill=(90, 170, 120), outline=(30, 90, 50), width=6)
            d.ellipse([x + 220, y + 70, x + 380, y + 230], outline=(30, 90, 50), width=6)
            d.text((x + 520, y + 60), '10 000', font=font(FB, 40), fill=(20, 70, 40), anchor='mm')
        return im
    if 'carte' in n:
        d.rounded_rectangle([170, 330, 830, 750], 30, fill=(250, 160, 30), outline=(150, 80, 0), width=6)
        d.text((500, 470), 'RECHARGE', font=font(FB, 70), fill='white', anchor='mm')
        d.text((500, 600), '1 000 F', font=font(FB, 90), fill='white', anchor='mm')
        return im
    if 'colis' in n or 'paquet' in n or 'cadeau' in n:
        d.rectangle([220, 420, 780, 900], fill=(200, 40, 60), outline=(120, 20, 30), width=6)
        d.rectangle([460, 420, 540, 900], fill=(250, 210, 60)); d.rectangle([220, 620, 780, 690], fill=(250, 210, 60))
        d.ellipse([360, 300, 500, 440], outline=(250, 210, 60), width=26); d.ellipse([500, 300, 640, 440], outline=(250, 210, 60), width=26)
        return im
    if 'lettre' in n or 'message' in n or 'mot' in n:
        d.polygon([(220, 300), (800, 260), (830, 860), (250, 900)], fill=(252, 248, 235), outline=(160, 150, 120), width=5)
        for i in range(7): d.line([(290, 400 + i * 65), (760, 370 + i * 65)], fill=(120, 140, 200), width=5)
        return im
    return None

def status_screen(lines, photo=None, title='Statuts'):
    """Publication de réseau social : compte, photo (image du catalogue), légende, nombre de vues."""
    S = Image.new('RGBA', (SW, SH), (245, 245, 245, 255)); d = ImageDraw.Draw(S)
    d.rectangle([0, 0, SW, 170], fill=(18, 140, 126)); d.text((40, 100), title, font=font(FB, 42), fill='white')
    d.ellipse([30, 195, 110, 275], fill=(150, 150, 150)); d.text((128, 205), 'Compte inconnu', font=font(FB, 34), fill=ENCRE); d.text((128, 245), "à l'instant", font=font(FM, 26), fill=(120, 120, 120))
    y = 300
    if photo is not None:
        ph = photo.copy(); ph.thumbnail((SW - 40, 560))
        bg = Image.new('RGBA', (SW - 40, ph.height + 20), (225, 215, 200, 255)); bg.alpha_composite(ph, ((SW - 40 - ph.width) // 2, 10))
        S.alpha_composite(bg, (20, y)); y += bg.height + 20
    views = [l for l in lines if re.search(r'\bvues?\b', l)]
    for l in [l for l in lines if l not in views]:
        f = font(FB if l.startswith('«') else FM, 34)
        for ln in wrap(l, f, SW - 60): d.text((30, y), ln, font=f, fill=ENCRE); y += 46
        y += 10
    for v in views: d.text((30, SH - 90), '👁 ' + v if False else v, font=font(FM, 30), fill=(110, 110, 110))
    return S
