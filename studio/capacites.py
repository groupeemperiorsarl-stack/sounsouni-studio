"""Écrit docs/CAPACITES.md : ce que l'application sait montrer aujourd'hui (personnages, poses, émotions, objets, décors).
Généré à partir du catalogue : à relancer après l'ajout de nouvelles images."""
import json, os, collections
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
cat = json.load(open(A + '/catalog.json')); P = cat['poses']
NOM = {'BAKARY': 'Bakary', 'AWA': 'Awa', 'MODIBO': 'Modibo', 'DIASABI': 'Diasabi', 'FATIM': 'Fatim', 'MIMI': 'Mimi', 'SEYDOU': 'Seydou',
       'KADI': 'Tantie Kadi', 'MOUSSA': 'Moussa', 'KARIM': 'Karim', 'SALI': 'Sali', 'VENDEUSE': 'Vendeuse'}
POST = {'debout': 'debout', 'assis': 'assis', 'banc': 'sur le banc', 'marche': 'marche', 'court': 'court', 'dos': 'de dos', 'tombe': 'tombe'}
SKIP = {'cycle_marche', 'cycle_marche_dos'}
out = ['# Ce que l\'application sait montrer', '',
       '_Fiche générée automatiquement à partir des images disponibles. À donner au scénariste avec le guide._', '',
       'Écrire une émotion ou une action de cette liste = elle sera montrée. Une émotion absente = l\'application prend la plus proche.',
       'Un objet n\'apparaît dans les mains d\'un personnage que si le script le demande (ex. `[Bakary assis, téléphone]`).', '']
by = collections.defaultdict(list)
for k, p in P.items():
    if '@' in k or p['char'] in ('OBJET',) or '+' in p['char']: continue
    by[p['char']].append(p)
for c in NOM:
    if c not in by: continue
    emos, posts, objs = set(), set(), set()
    for p in by[c]:
        posts.add(POST.get(p['posture'], p['posture']))
        props = set(p.get('props', []))
        objs |= props - {'larmes'}
        emos |= set(t for t in p['tags'] if t not in props and t not in SKIP and t not in POST)
    out += [f'## {NOM[c]} (`{c}`)', f'- **Postures** : {", ".join(sorted(posts))}', f'- **Émotions / gestes** : {", ".join(sorted(emos))}',
            f'- **Objets en main possibles** : {", ".join(sorted(objs)) or "aucun"}', '']
grp = [p['char'] for k, p in P.items() if '+' in p['char']]
objp = [', '.join(p['tags']) for k, p in P.items() if p['char'] == 'OBJET']
out += ['## Images de groupe', '- ' + '\n- '.join(g.replace('+', ' + ') for g in grp), '',
        '## Objets en gros plan (`PLAN: objet …`)', '- ' + '\n- '.join(objp),
        '- dessinés par l\'application : boîte (pleine / vide), gâteau(x), billets, carte de recharge, colis / cadeau, lettre / message, téléphone (écran)', '',
        '## Décors', '- ' + ', '.join(f'`{d}`' for d in ['KIOSQUE', 'ATELIER', 'MARCHE', 'RUE', 'CABINE', 'BUREAU', 'VILLA', 'SHOWROOM']), '',
        '## À savoir', '- Seuls les personnages ci-dessus peuvent apparaître. « Des clients », « la foule » : les faire jouer par un personnage connu, ou les montrer sur un écran de téléphone.',
        '- La caméra est choisie par l\'application (plan large, gros plan, caméra derrière l\'épaule). Le scénariste peut l\'imposer avec `PLAN:`.',
        '- Une nouvelle image (pose, objet, décor) ajoutée au catalogue est analysée toute seule par l\'application.', '']
open(os.path.join(os.path.dirname(A), '..', 'docs', 'CAPACITES.md'), 'w').write('\n'.join(out)); print('docs/CAPACITES.md écrit')
