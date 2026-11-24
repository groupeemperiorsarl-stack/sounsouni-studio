"""IMAGES SANS GEMINI (demande d'Issa, 24/11/2026 : « au lieu de nous faire attendre »).
Pour les scènes à deux (moto, gifle…) et les plans dans le décor de la fiche, l'application les fait elle-même avec un modèle
libre (FLUX.1 Kontext, gratuit, sur Hugging Face, depuis les machines GitHub) : on colle les images des personnages côte à côte,
le modèle les met en scène en gardant visage, habits et style ; l'image va dans demandes/gemini/N/ puis le rangement habituel.
Utilisation : N=26 python .github/scripts/image_libre.py [groupes ex. 3,4 | vide = toutes les scènes de la fiche]"""
import os, sys, json, subprocess, time, shutil
sys.path.insert(0, 'studio'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
N = os.environ['N']; A = 'studio/assets'
# fiche refaite ici à partir du script actuel (celle de la page peut être d'avant : images déjà rangées puis retirées…)
subprocess.run(f'STUDIO_FAUSSES_VOIX=1 python -m studio.gemini demandes/episode_{N}.txt -o /tmp/fiche_libre', shell=True, check=True)
fiche = json.load(open('/tmp/fiche_libre/fiche_gemini.json'))
items = {x['n']: x for x in fiche['items']}
voulu = [int(g) for g in (sys.argv[1] if len(sys.argv) > 1 else '').replace(' ', '').split(',') if g]
import gemini
def planche(x):
    """Les personnages de la scène côte à côte sur fond gris (et le décor à gauche pour un plan dans le décor)."""
    ims = []
    if x['type'] == 'scene_decor':
        d = Image.open(f"{A}/decors/{x['decor']}.jpg").convert('RGB'); d.thumbnail((700, 1000)); ims.append(d.convert('RGBA'))
    for c in x['persos']:
        im = Image.open(f"{A}/poses/{gemini.reference(c)}.webp").convert('RGBA'); ims.append(im.resize((int(im.width * 900 / im.height), 900)))
    W = sum(i.width for i in ims) + 40 * (len(ims) + 1); bg = Image.new('RGB', (max(W, 1024), 1024), (226, 226, 226)); x0 = 40
    for im in ims: bg.paste(im, (x0, 1024 - im.height - 40), im); x0 += im.width + 40
    return bg
def consigne(x):
    noms = ', '.join(f"{gemini.gfx.nom(c)} ({gemini.IDENTITE.get(c, '')[:90]})" for c in x['persos'])
    if x['type'] == 'scene_decor':
        return (f"Use the place shown on the left as the setting and put these exact cartoon characters in it: {noms}. Scene: {x['texte']}. "
                "Keep every face, hairstyle, clothes and the 3D animated movie style exactly the same. Vertical image, characters at the right size for their distance, feet on the ground, no text.")
    return (f"Make these exact cartoon characters do this action together: {x['texte']}. Characters, from left to right: {noms}. "
            "They share the SAME single object (only ONE motorcycle, ONE table, etc. — never one each); the first character named in the action is the one who does it (for example the driver sits in front, the other sits behind as passenger). "
            "Keep every face, hairstyle, clothes and the 3D animated movie style exactly the same. Full bodies visible, side view, plain light grey studio background (even if the scene is at night), no text, nobody else.")
VERIF = """Tu es le contrôleur des images du studio (dessin animé 3D « Les Plans de Bakary »). On te montre : 1) les personnages de référence côte à côte, 2) une image fabriquée.
Vérifie que l'image fabriquée montre EXACTEMENT l'action demandée, sans défaut grossier : chaque objet une seule fois (par exemple UNE seule moto pour deux personnes, jamais deux motos collées),
la bonne personne fait la bonne chose (qui conduit, qui est derrière, qui gifle…), les personnages reconnaissables (visage, coiffure, habits), corps entiers, pas de membre en trop, pas de personnage en plus, pas de texte.
Réponds uniquement en JSON : {"ok": true ou false, "probleme": "une phrase en français simple si ok est false"}"""
def verifier(x, chemin):
    """Règle d'Issa (24/11/2026) : l'application regarde chaque image elle-même avant de la ranger (deux motos collées étaient passées)."""
    import base64, relecture as rl
    b = lambda f: base64.b64encode(open(f, 'rb').read()).decode()
    parts = [{'text': 'Action demandée : ' + x['texte'] + '\nPersonnages : ' + ', '.join(x['persos'])}, {'inline_data': {'mime_type': 'image/png', 'data': b('/tmp/entree.png')}},
             {'inline_data': {'mime_type': 'image/jpeg', 'data': b(chemin)}}]
    try: m, r = rl.gemini(VERIF, parts); return bool(r.get('ok')), r.get('probleme', '')
    except Exception as e: print('  vérification impossible :', str(e)[:120]); return None, 'vérification impossible (Gemini indisponible)'
def kontext(image, consigne_, graine, sortie):
    from gradio_client import Client, handle_file
    r = Client('black-forest-labs/FLUX.1-Kontext-Dev', hf_token=os.environ.get('HF_TOKEN') or None).predict(input_image=handle_file(image), prompt=consigne_, seed=graine,
                                                                     randomize_seed=False, guidance_scale=2.5, steps=28, api_name='/infer')
    p = r[0] if isinstance(r[0], str) else r[0]['path']; Image.open(p).convert('RGB').save(sortie, quality=94)
def faire(x, sortie):
    """Plusieurs essais ; chaque image est vérifiée. Pour deux personnes : si le collage côte à côte donne des objets en double, on fait en deux temps
    (d'abord le premier seul avec l'action, puis on ajoute l'autre à côté de lui)."""
    planche(x).save('/tmp/entree.png'); echecs = []
    for essai in range(4):
        try:
            if essai < 2 or len(x['persos']) < 2: kontext('/tmp/entree.png', consigne(x), 7 + essai, sortie)
            else:   # en deux temps
                y = dict(x, persos=x['persos'][:1]); planche(y).save('/tmp/un.png')
                kontext('/tmp/un.png', f"Make this exact cartoon character do this: {x['texte']}. The other people of the action are not there yet: leave free space for them. Keep face, hair, clothes and 3D style exactly. Full body, side view, plain light grey background.", 11 + essai, '/tmp/etape1.jpg')
                a = Image.open('/tmp/etape1.jpg').convert('RGB'); o = planche(dict(x, persos=x['persos'][1:], type='scene')); a.thumbnail((1024, 1024))
                c = Image.new('RGB', (a.width + o.width, 1024), (226, 226, 226)); c.paste(a, (0, 1024 - a.height)); c.paste(o, (a.width, 0)); c.save('/tmp/deux.png')
                kontext('/tmp/deux.png', f"The character(s) on the right join the scene on the left, so that the final picture shows: {x['texte']}. Use the SAME objects as on the left (never add a second one). Keep every face, hair, clothes and 3D style exactly. One single scene, full bodies, side view, plain light grey background, no text.", 21 + essai, sortie)
        except Exception as e:
            print('  essai', essai + 1, ':', str(e)[:200]); echecs.append(str(e)[:80])
            if 'ZeroGPU' in str(e) or 'quota' in str(e).lower(): return False, 'quota gratuit du modèle épuisé'
            time.sleep(15); continue
        ok, pb = verifier(x, sortie); print('  essai', essai + 1, ': contrôle', ok, pb)
        if ok: return True, ''
        if ok is None: return False, pb
        echecs.append(pb)
    return False, ' ; '.join(echecs[-2:])
os.makedirs(f'demandes/gemini/{N}', exist_ok=True); faits, rates = [], []
for g in fiche['groupes']:
    xs = [items[n] for n in g['items']]
    if (voulu and g['g'] not in voulu) or (not voulu and not (len(xs) == 1 and xs[0]['type'] in ('scene', 'scene_decor'))): continue
    f = f"{g['g']}_libre.jpg"; print('image', g['g'], ':', g.get('titres'))
    ok, pb = faire(xs[0], f'demandes/gemini/{N}/{f}')
    if ok: faits.append(f"{g['g']}={f}")
    else:
        rates.append(f"demande {g['g']} : {pb}")
        if os.path.exists(f'demandes/gemini/{N}/{f}'): os.remove(f'demandes/gemini/{N}/{f}')   # une image ratée n'est jamais rangée
print('FAITS', ' '.join(faits)); open('faits.txt', 'w').write(' '.join(faits)); open('rates.txt', 'w').write('\n'.join(rates))
