"""RELECTEUR automatique (après chaque aperçu) : une IA (Gemini, clé dans les secrets GitHub) relit le script comme un spectateur et regarde
chaque plan de l'aperçu, puis liste les problèmes avec les corrections du studio (mêmes actions que « 💬 Discuter »).
Résultat : relecture.json dans la branche « fichiers » (lu par la page Studio mobile, bouton « Appliquer ») + un commentaire sur la demande.
Utilisation (GitHub) : ISSUE=N GEMINI_API_KEY=… GH_TOKEN=… python .github/scripts/relecture.py   ·   essai local : --local dossier_apercu script.txt"""
import os, sys, json, base64, io, time, re, urllib.request, subprocess
from PIL import Image

R = os.environ.get('GITHUB_REPOSITORY', 'groupeemperiorsarl-stack/sounsouni-studio'); N = os.environ.get('ISSUE', '')
K = os.environ.get('GEMINI_API_KEY', '')
def req(url, data=None, headers=None, raw=False, timeout=300):
    h = {'User-Agent': 'sounsouni-studio-relecteur/1.0', **(headers or {})}
    if data is not None and not isinstance(data, bytes): data = json.dumps(data).encode(); h.setdefault('Content-Type', 'application/json')
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout); b = r.read()
    return b if raw else json.loads(b or b'null')
def gh(path, **kw):
    return req('https://api.github.com/repos/' + R + path, headers={'Authorization': 'Bearer ' + os.environ.get('GH_TOKEN', ''), 'Accept': kw.pop('accept', 'application/vnd.github+json')}, **kw)
def fichier(nom):   # fichier rangé pour la demande (branche fichiers)
    try: return gh(f'/contents/{N}/{nom}?ref=fichiers', accept='application/vnd.github.raw', raw=True)
    except Exception: return None

def lire():
    if '--local' in sys.argv:
        d, scr = sys.argv[sys.argv.index('--local') + 1:][:2]
        g = lambda n: open(os.path.join(d, n), 'rb').read() if os.path.exists(os.path.join(d, n)) else None
        return open(scr, encoding='utf-8').read(), g('apercu_plans.png'), g('plans_resume.json'), g('manques.json'), os.path.splitext(scr)[0] + '.choix.json'
    return open(f'demandes/episode_{N}.txt', encoding='utf-8').read(), fichier('apercu_plans.png'), fichier('plans_resume.json'), fichier('manques.json'), f'demandes/episode_{N}.choix.json'

def bandes(png, par=16):   # l'aperçu coupé en bandes de 2 rangées (8 vignettes par rangée), lisibles par l'IA
    im = Image.open(io.BytesIO(png)).convert('RGB'); w, h = im.size
    cols = 8; vw = w // cols; vh = int(vw * 16 / 9) + 24; rows = max(1, round(h / vh)); vh = h / rows; out = []
    for r in range(0, rows, 2):
        b = im.crop((0, int(r * vh), w, int(min(h, (r + 2) * vh)))); b = b.resize((1536, int(b.height * 1536 / w)))
        f = io.BytesIO(); b.save(f, 'JPEG', quality=82); out.append(base64.b64encode(f.getvalue()).decode())
    return out

def modeles():
    v = []
    try:
        j = req('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000', headers={'x-goog-api-key': K}, timeout=30)
        v = [m['name'].replace('models/', '') for m in j.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m['name'] and not re.search(r'lite|image|tts|live|audio|embed|exp|vision|thinking', m['name'])]
    except Exception as e: print('liste des modèles :', e)
    num = lambda m: (float(re.search(r'gemini-(\d+(?:\.\d+)?)', m).group(1)) - (0.01 if 'preview' in m else 0)) if re.search(r'gemini-(\d+(?:\.\d+)?)', m) else (2.95 if 'latest' in m else 0)
    return sorted(v, key=num, reverse=True)[:6] or ['gemini-flash-latest', 'gemini-3-flash-preview']

def gemini(sys_txt, parts):
    for tour in range(10):
        for m in modeles():
            try:
                d = req(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', {'systemInstruction': {'parts': [{'text': sys_txt}]}, 'contents': [{'role': 'user', 'parts': parts}],
                        'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json'}}, headers={'x-goog-api-key': K}, timeout=600)
                t = ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
                if t: print('relecture par', m); return m, json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception as e: print(m, ':', str(e)[:160])
        print('Gemini occupé, nouvel essai dans 60 s'); time.sleep(60)
    raise RuntimeError('Gemini ne répond pas')

def groq(sys_txt, user):   # passe « histoire » (texte seul) : Groq d'abord quand la clé existe (Gemini gratuit est souvent saturé)
    k = os.environ.get('GROQ_API_KEY')
    if not k: raise RuntimeError('pas de clé Groq')
    for essai in range(6):
        try:
            d = req('https://api.groq.com/openai/v1/chat/completions', {'model': 'openai/gpt-oss-120b', 'temperature': 0.2, 'reasoning_effort': 'medium', 'response_format': {'type': 'json_object'},
                    'messages': [{'role': 'system', 'content': sys_txt}, {'role': 'user', 'content': user}]}, headers={'Authorization': 'Bearer ' + k}, timeout=300)
            t = d['choices'][0]['message']['content']; print('histoire relue par Groq'); return 'Groq gpt-oss-120b', json.loads(t[t.find('{'):t.rfind('}') + 1])
        except urllib.error.HTTPError as e:
            b = e.read().decode()[:300]; print('Groq :', e.code, b[:160])
            if e.code == 429 and 'per day' not in b: time.sleep(65); continue
            raise
    raise RuntimeError('Groq saturé')
import urllib.error

def main():
    scr, png, pr, mq, cpath = lire()
    if not png or not pr: print('pas d\'aperçu à relire'); return 1
    cat = json.load(open('studio/assets/catalog.json', encoding='utf-8'))['poses']
    plans = json.loads(pr); lignes = []
    for p in plans:   # le plan en texte, avec les étiquettes des poses visibles (objets, gestes)
        a = ' ; '.join(f"{x['qui']} {x['pose'].split('@')[0]} [{', '.join(cat.get(x['pose'].split('@')[0], {}).get('tags', []))}]" for x in p.get('acteurs', []))
        lignes.append(f"plan {p['plan']} · {p['debut']} · {p['duree']} s · {p['type']} · {p['decor']}" + (f" · {p['parle']} : « {p['texte']} »" if p.get('parle') else (f" · « {p['texte']} »" if p.get('texte') else '')) + (f" · cadrage {p['cadrage']}" if p.get('cadrage') else '') + (f" · visibles : {a}" if a else ''))
    poses = {}
    for k, p in cat.items():
        if '@' not in k and p['char'] not in ('OBJET',) and '+' not in p['char']: poses.setdefault(p['char'], []).append(f"{k} ({p['posture']} : {' '.join(p.get('tags', []))})")
    lu = lambda f: open(f, encoding='utf-8').read() if os.path.exists(f) else ''
    sys_txt = lu('docs/RELECTEUR.md') + '\n\n## CONSIGNES DE L\'ASSISTANT (les actions possibles)\n' + lu('docs/ASSISTANT_ACTIONS.md') + '\n\n## CARNET DU STUDIO\n' + lu('technicien/carnet.md')
    ctx = ('## SCRIPT\n' + scr + '\n\n## PLANS MINUTÉS\n' + '\n'.join(lignes) + '\n\n## CHOIX DÉJÀ FAITS\n' + (lu(cpath) or '{}') + '\n\n## ÉMOTIONS SANS IMAGE (visage calme mis à la place)\n' + (mq.decode() if mq else '[]') +
           '\n\n## POSES DISPONIBLES PAR PERSONNAGE (clé (posture : étiquettes))\n' + '\n'.join(c + ' : ' + ' | '.join(v) for c, v in poses.items()) + '\n\n## IMAGES DE L\'APERÇU : les bandes suivent, dans l\'ordre des plans (numéro sous chaque vignette).')
    # deux passes, comme un vrai relecteur : d'abord l'histoire seule (le script, lu comme un spectateur), puis les images plan par plan
    A_sys = lu('docs/RELECTEUR.md') + "\n\n## CETTE PASSE : SEULEMENT LA PARTIE A (L'HISTOIRE)\nLis le script ligne par ligne comme un spectateur qui découvre l'épisode. Cherche surtout : contradictions, personnes présentes qui ne devraient pas l'être (ou absentes), phrases adressées à quelqu'un écrites en PENSÉE ou mélangées à un monologue, entrées sans salutation, décor illogique pour l'histoire, objets importants jamais montrés, émotions qui ne vont pas avec la situation. Corrections par actions « script » uniquement ({\"type\": \"script\", \"ancien\": \"texte exact\", \"nouveau\": \"texte corrigé\", \"pourquoi\": \"…\"}), et « note » pour une leçon. Pas de problème d'image dans cette passe."
    A_user = '## SCRIPT\n' + scr
    try: mA, resA = groq(A_sys, A_user)
    except Exception as e:
        print('passe histoire par Gemini (' + str(e)[:80] + ')')
        try: mA, resA = gemini(A_sys + '\n\n## CONSIGNES DE L\'ASSISTANT\n' + lu('docs/ASSISTANT_ACTIONS.md'), [{'text': A_user + '\n\n## PLANS MINUTÉS\n' + '\n'.join(lignes)}])
        except Exception as e2: mA, resA = '', {'resume': '', 'problemes': [], 'erreur': str(e2)}
    parts = [{'text': ctx}] + [{'inline_data': {'mime_type': 'image/jpeg', 'data': b}} for b in bandes(png)]
    try: mB, resB = gemini(sys_txt + "\n\n## CETTE PASSE : SEULEMENT LA PARTIE B (LES IMAGES)\nL'histoire a déjà été relue. Regarde chaque vignette et les étiquettes des poses : décor, pieds au sol, personnes en trop, gestes, objets en trop, visage contraire à l'émotion, images manquantes. Corrections par actions de plan (pose, acteur, plan, fiche).", parts)
    except Exception as e: mB, resB = '', {'resume': 'Les images n\'ont pas pu être regardées (Gemini saturé) : relancez « relecture » plus tard.', 'problemes': []}
    if not mA and not mB: raise RuntimeError('aucune IA disponible pour la relecture')
    m = mA if mA == mB else ' + '.join(x for x in (mA, mB) if x)
    res = {'resume': (resA.get('resume', '') + ' ' + resB.get('resume', '')).strip(), 'problemes': (resA.get('problemes', []) + resB.get('problemes', []))[:20]}
    # contrôle des actions : poses existantes et du bon personnage, numéros de plan possibles, jamais de pose « gifle »
    nplans = len(plans)
    for pb in res.get('problemes', []):
        ok = []
        for a in pb.get('actions', []):
            if a.get('type') == 'pose':
                p = cat.get(a.get('pose', ''));
                if not p or p['char'] != str(a.get('qui', '')).upper() or 'gifle' in p.get('tags', []): continue
            if a.get('type') in ('plan', 'pose', 'acteur', 'duree') and not (isinstance(a.get('plan'), int) and 0 <= a['plan'] < nplans): continue
            if a.get('type') == 'code': continue   # le relecteur ne touche pas au code
            ok.append(a)
        pb['actions'] = ok
    res['modele'] = m; res['date'] = time.strftime('%Y-%m-%d %H:%M')
    json.dump(res, open('relecture.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    P = res.get('problemes', [])
    msg = f"🔎 **Relecture automatique** : {len(P)} problème(s) trouvé(s). {res.get('resume', '')}\n\n" + '\n'.join(f"- {'🔴' if p.get('gravite') == 'fort' else '🟠' if p.get('gravite') == 'moyen' else '🟡'} {(p.get('moment') or '') + ' · ' if p.get('moment') else ''}{p.get('quoi', '')}" for p in P[:20]) + \
          ("\n\nDans la page : « 🔎 Relecture » → cochez les corrections → « ✅ Appliquer », puis relancez l'aperçu." if P else '')
    print(msg)
    if N and '--local' not in sys.argv:
        subprocess.run(['bash', '.github/scripts/fichiers.sh', N, 'relecture.json'])
        gh(f'/issues/{N}/comments', data={'body': msg})
    return 0

if __name__ == '__main__': sys.exit(main())
