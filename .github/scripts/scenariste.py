"""ESSAI DU SCÉNARISTE (même consignes que l'onglet ✍️ de la page Studio mobile) : une idée → script complet, puis vérifié par le lecteur du studio.
GitHub : workflow « Essai du scénariste » (idée en entrée). Local : GEMINI_API_KEY=… python .github/scripts/scenariste.py "idée" [numéro]"""
import os, sys, re, json, time, urllib.error
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, 'studio')
import relecture as rl
import script as sc

def ecrire(demande):
    lu = lambda f: open(f, encoding='utf-8').read()
    sys_txt = lu('docs/SCENARISTE.md') + '\n\n## GUIDE DU SCÉNARISTE (format du studio)\n' + lu('docs/GUIDE_SCENARISTE.md') + "\n\n## L'HISTOIRE JUSQU'ICI ET LES IDÉES DE LA SAISON\n" + lu('docs/SAISON.md') + \
              '\n\n## RÈGLES DE MISE AU FORMAT DU STUDIO\n' + lu('docs/ASSISTANT.md') + '\n\n## CE QUE LE RELECTEUR VÉRIFIE\n' + lu('docs/RELECTEUR.md') + "\n\n## CE QUE L'APPLICATION SAIT MONTRER\n" + lu('docs/CAPACITES.md') + \
              '\n\n## CARNET DU STUDIO\n' + lu('technicien/carnet.md') + '\n\n## TOUS LES ÉPISODES DÉJÀ FAITS\n' + lu('docs/EPISODES.md')
    for tour in range(6):
        for m in rl.modeles():
            try:
                d = rl.req(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', {'systemInstruction': {'parts': [{'text': sys_txt}]},
                           'contents': [{'role': 'user', 'parts': [{'text': demande}]}], 'generationConfig': {'temperature': 0.9}}, headers={'x-goog-api-key': rl.K}, timeout=600)
                t = ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
                t = re.sub(r'^```\w*\n?|\n?```\s*$', '', t.strip()).strip(); k = t.find('TITRE:')
                if k >= 0: return m, t[k:]
            except urllib.error.HTTPError as e: print(m, ':', e.code, e.read().decode()[:120])
            except Exception as e: print(m, ':', str(e)[:160])
        time.sleep(60)
    raise RuntimeError('Gemini ne répond pas')

if __name__ == '__main__':
    idee, num = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'suivant')
    m, t = ecrire(f"Écris l'épisode {num} complet à partir de cette idée d'Issa :\n{idee}")
    open('scenario.txt', 'w', encoding='utf-8').write(t)
    meta, ev = sc.parse(t); lignes = [e for e in ev if e.get('type') == 'line']
    mots = sum(len(e.get('text', '').split()) for e in lignes)
    print(f'écrit par {m} · {len(lignes)} répliques · {mots} mots · {sum(1 for e in ev if e.get("type") == "scene")} scènes')
