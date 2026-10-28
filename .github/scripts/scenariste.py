"""SCÉNARISTE SUR GITHUB (mêmes consignes que l'onglet ✍️ de la page Studio mobile), avec TOUTES les IA gratuites du studio (clés dans les secrets GitHub).
Ordre : Gemini, Mistral, NVIDIA, Zhipu, Cerebras, OpenRouter (mémoire complète : scripts entiers de tous les épisodes)
        puis GitHub Models et Groq (trop petits pour tout lire : résumé de l'histoire seulement).
GitHub : commentaire « scénario … » sur la demande « ✍️ Scénariste » (workflow scenariste.yml) → réponse en commentaire.
Local / essai : python .github/scripts/scenariste.py "idée" [numéro]"""
import os, sys, re, json, time, urllib.request, urllib.error
sys.path.insert(0, 'studio')
E = os.environ
def lu(f): return open(f, encoding='utf-8').read() if os.path.exists(f) else ''
def consignes(complet):
    base = lu('docs/SCENARISTE.md') + '\n\n## GUIDE DU SCÉNARISTE (format du studio)\n' + lu('docs/GUIDE_SCENARISTE.md')
    if not complet:   # petites IA : seulement l'histoire jusqu'ici (sans la liste des idées)
        h = lu('docs/SAISON.md'); return base + "\n\n## L'HISTOIRE JUSQU'ICI\n" + h.split('## Idées')[0]
    return (base + "\n\n## L'HISTOIRE JUSQU'ICI ET LES IDÉES DE LA SAISON\n" + lu('docs/SAISON.md') + "\n\n## RÈGLES DE MISE AU FORMAT DU STUDIO (à respecter dès l'écriture)\n" + lu('docs/ASSISTANT.md') +
            '\n\n## CE QUE LE RELECTEUR VÉRIFIE (évite ces erreurs)\n' + lu('docs/RELECTEUR.md') + "\n\n## CE QUE L'APPLICATION SAIT MONTRER\n" + lu('docs/CAPACITES.md') +
            '\n\n## CARNET DU STUDIO (leçons apprises)\n' + lu('technicien/carnet.md') + '\n\n## TOUS LES ÉPISODES DÉJÀ FAITS (scripts complets : même style, même structure, même longueur, suite logique)\n' + lu('docs/EPISODES.md'))
def post(url, data, headers, timeout=600):
    q = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'sounsouni-studio', **headers})
    for essai in range(3):   # 429 (trop de demandes) / 503 (surchargé) : on attend un peu et on réessaie
        try: return json.loads(urllib.request.urlopen(q, timeout=timeout).read())
        except urllib.error.HTTPError as e:
            b = e.read().decode(errors='ignore')[:300]
            if e.code in (429, 500, 502, 503) and essai < 2 and not re.search(r'per day|daily|quota', b, re.I): print(url.split('/')[2], e.code, '→ nouvel essai dans 30 s'); time.sleep(30); continue
            raise RuntimeError(f'{e.code} {b[:160]}')
def modeles_gemini():
    try:
        q = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000', headers={'x-goog-api-key': E['GEMINI_API_KEY']})
        v = [m['name'][7:] for m in json.loads(urllib.request.urlopen(q, timeout=30).read()).get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])
             and re.search(r'flash|pro', m['name']) and not re.search(r'lite|image|tts|live|audio|embed|exp|vision|thinking', m['name'])]
        num = lambda m: (float((re.search(r'gemini-(\d+(?:\.\d+)?)', m) or [0, 0])[1]) + (0.5 if 'pro' in m else 0) - (0.01 if 'preview' in m else 0))
        return sorted(v, key=num, reverse=True)[:6] or ['gemini-flash-latest']
    except Exception as e: print('liste Gemini :', e); return ['gemini-flash-latest']
def gemini(sys_txt, user):
    if not E.get('GEMINI_API_KEY'): raise RuntimeError('pas de clé')
    err = []
    for m in modeles_gemini():
        try:
            d = post(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', {'systemInstruction': {'parts': [{'text': sys_txt}]},
                     'contents': [{'role': 'user', 'parts': [{'text': user}]}], 'generationConfig': {'temperature': 0.9}}, {'x-goog-api-key': E['GEMINI_API_KEY']})
            t = ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
            if t: return t, m
        except Exception as e: err.append(f'{m} {str(e)[:60]}'); print('Gemini', m, ':', str(e)[:120])
    raise RuntimeError('tous les modèles Gemini sont occupés (' + ' ; '.join(err)[:200] + ')')
def compatible(url, cle, modele, extra=None):
    def f(sys_txt, user):
        k = E.get(cle)
        if not k: raise RuntimeError('pas de clé')
        m = modele() if callable(modele) else modele
        d = post(url, {'model': m, 'temperature': 0.9, 'messages': [{'role': 'system', 'content': sys_txt}, {'role': 'user', 'content': user}], **(extra or {})}, {'Authorization': 'Bearer ' + k})
        t = d['choices'][0]['message'].get('content') or ''
        if not t: raise RuntimeError('réponse vide')
        return t, m
    return f
def openrouter_libre():   # le meilleur modèle gratuit du moment qui sait lire très long (la liste change souvent)
    try:
        L = json.loads(urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/models', headers={'User-Agent': 'sounsouni-studio'}), timeout=30).read())['data']
        L = [x for x in L if x['id'].endswith(':free') and (x.get('context_length') or 0) >= 100000]
        rang = lambda x: next((i for i, k in enumerate(('deepseek', 'qwen3', 'gpt-oss', 'llama-4', 'glm', 'kimi', 'mistral', 'gemma')) if k in x['id']), 99)
        return sorted(L, key=rang)[0]['id']
    except Exception as e: print('liste OpenRouter :', e); return 'openai/gpt-oss-120b:free'
IA = [('Gemini', gemini, True),
      ('Mistral', compatible('https://api.mistral.ai/v1/chat/completions', 'MISTRAL_API_KEY', 'mistral-medium-latest'), True),
      ('NVIDIA', compatible('https://integrate.api.nvidia.com/v1/chat/completions', 'NVIDIA_API_KEY', 'deepseek-ai/deepseek-v3.1', {'max_tokens': 8000}), True),
      ('Zhipu', compatible('https://api.z.ai/api/paas/v4/chat/completions', 'ZHIPU_API_KEY', 'glm-4.5-flash'), True),
      ('Cerebras', compatible('https://api.cerebras.ai/v1/chat/completions', 'CEREBRAS_API_KEY', 'gpt-oss-120b', {'reasoning_effort': 'low'}), True),
      ('OpenRouter', compatible('https://openrouter.ai/api/v1/chat/completions', 'OPENROUTER_API_KEY', openrouter_libre), True),
      ('GitHub Models', compatible('https://models.github.ai/inference/chat/completions', 'GITHUB_MODELS_TOKEN', 'openai/gpt-4.1'), False),
      ('Groq', compatible('https://api.groq.com/openai/v1/chat/completions', 'GROQ_API_KEY', 'openai/gpt-oss-120b', {'reasoning_effort': 'low'}), False)]
def nettoyer(t):
    t = re.sub(r'<think>.*?</think>', '', t or '', flags=re.S).strip(); t = re.sub(r'^```\w*\n?|\n?```\s*$', '', t).strip(); k = t.find('TITRE:')
    return t[k:] if k >= 0 else ''
MINI = 600   # mots de dialogue au minimum (≈ 3 min 10 à 145 mots par minute, mesuré sur l'ép. 23)
def mots(s):
    import script as sc
    return sum(len(e.get('text', '').split()) for e in sc.parse(s)[1] if e.get('type') == 'line')
def ecrire(demande, log=print):
    essais = []
    for nom, f, complet in IA:
        try:
            t, m = f(consignes(complet), demande); s = nettoyer(t)
            if s and re.search(r'DÉCOR\s*:', s):
                import script as sc; sc.parse(s)   # le script doit se lire
                n = mots(s)
                if n < MINI and 'ALLONGE' not in demande:   # trop court pour YouTube (3 min 10) : la même IA l'allonge tout de suite
                    log(f'{nom} : {n} mots seulement, je demande de rallonger')
                    try:
                        t2, _ = f(consignes(complet), f"Voici ton script ({n} mots de dialogue) :\n\n{s}\n\nALLONGE-LE : il faut AU MOINS {MINI} mots de dialogue (3 min 10). Rallonge les conversations (plus de répliques qui se répondent, plus de drame et de piquant), sans rien enlever ni changer l'histoire. Renvoie le script ENTIER.")
                        s2 = nettoyer(t2)
                        if s2 and mots(s2) > n: sc.parse(s2); s = s2
                    except Exception as e: log(f'allongement raté : {e}')
                return s, f"{nom} ({m})" + ('' if complet else " — résumé de l'histoire seulement")
            essais.append(f'{nom} : script pas au format')
        except Exception as e: essais.append(f'{nom} : {str(e)[:90]}')
        log(essais[-1])
    raise RuntimeError(' · '.join(essais))
def gh(path, data=None, method=None):
    q = urllib.request.Request('https://api.github.com/repos/' + E['GITHUB_REPOSITORY'] + path, data=json.dumps(data).encode() if data else None, method=method or ('POST' if data else 'GET'),
                               headers={'Authorization': 'Bearer ' + E['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'sounsouni-studio'})
    return json.loads(urllib.request.urlopen(q, timeout=60).read() or b'{}')
if __name__ == '__main__':
    if E.get('COMMENT_ID'):   # sur GitHub : la demande vient d'un commentaire « scénario … »
        n = E['ISSUE']; c = gh(f"/issues/comments/{E['COMMENT_ID']}")['body']
        demande = re.sub(r'\n+(-{3,}\s*\n+)?_Generated by[\s\S]*$', '', re.sub(r'^\s*sc[ée]nario\s*:?\s*', '', c, flags=re.I)).strip()
        try:
            s, qui = ecrire(demande)
            gh(f'/issues/{n}/comments', {'body': f'📜 **Scénario écrit par {qui}** (réponse au message {E["COMMENT_ID"]})\n\n```text\n{s}\n```'})
        except Exception as e:
            gh(f'/issues/{n}/comments', {'body': f'❌ Le scénariste n\'a pas pu écrire (réponse au message {E["COMMENT_ID"]}) : toutes les IA sont occupées ou sans clé. {str(e)[:600]}'})
    else:
        idee, num = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'suivant')
        s, qui = ecrire(f"Écris l'épisode {num} complet à partir de cette idée d'Issa :\n{idee}")
        open('scenario.txt', 'w', encoding='utf-8').write(s); print('écrit par', qui); print(s)
