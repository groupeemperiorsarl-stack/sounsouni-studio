"""IMAGES SANS GEMINI (demande d'Issa, 24/11/2026 : « au lieu de nous faire attendre »).
Pour les scènes à deux (moto, gifle…) et les plans dans le décor de la fiche, l'application les fait elle-même avec un modèle
libre (FLUX.1 Kontext, gratuit, sur Hugging Face, depuis les machines GitHub) : on colle les images des personnages côte à côte,
le modèle les met en scène en gardant visage, habits et style ; l'image va dans demandes/gemini/N/ puis le rangement habituel.
Utilisation : N=26 python .github/scripts/image_libre.py [groupes ex. 3,4 | vide = toutes les scènes de la fiche]"""
import os, sys, json, subprocess, time, shutil
sys.path.insert(0, 'studio')
from PIL import Image
N = os.environ['N']; A = 'studio/assets'
fiche = json.loads(subprocess.check_output(['git', 'show', f'origin/fichiers:{N}/fiche_gemini.json']))
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
def faire(x, sortie):
    from gradio_client import Client, handle_file
    planche(x).save('/tmp/entree.png')
    for essai in range(3):
        try:
            r = Client('black-forest-labs/FLUX.1-Kontext-Dev', hf_token=os.environ.get('HF_TOKEN') or None).predict(input_image=handle_file('/tmp/entree.png'), prompt=consigne(x), seed=7 + essai, randomize_seed=False,
                                                                     guidance_scale=2.5, steps=28, api_name='/infer')
            p = r[0] if isinstance(r[0], str) else r[0]['path']; Image.open(p).convert('RGB').save(sortie, quality=94); return True
        except Exception as e: print('  essai', essai + 1, ':', str(e)[:200]); time.sleep(20)
    return False
os.makedirs(f'demandes/gemini/{N}', exist_ok=True); faits = []
for g in fiche['groupes']:
    xs = [items[n] for n in g['items']]
    if (voulu and g['g'] not in voulu) or (not voulu and not (len(xs) == 1 and xs[0]['type'] in ('scene', 'scene_decor'))): continue
    f = f"{g['g']}_libre.jpg"; print('image', g['g'], ':', g.get('titres'))
    if faire(xs[0], f'demandes/gemini/{N}/{f}'): faits.append(f"{g['g']}={f}")
print('FAITS', ' '.join(faits)); open('faits.txt', 'w').write(' '.join(faits))
