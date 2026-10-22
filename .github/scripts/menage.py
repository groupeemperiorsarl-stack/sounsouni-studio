"""Ménage automatique de la place prise sur GitHub (demandé par Issa, 22/10/2026).
Les vidéos fabriquées (releases) ne servent plus une fois publiées : les poses et images restent dans le studio.
Règle : si les releases dépassent 60 % de LIMITE_GO, on supprime les plus anciennes jusqu'à redescendre sous 60 %.
Jamais supprimée : la dernière vidéo de chaque épisode modifié depuis moins de 30 jours (elle sert à ne refaire que les secondes changées
et aux boutons ⬇ de la page). Les aperçus de plus de 14 jours sont toujours supprimés (petits, plus utiles)."""
import json, os, sys, urllib.request, datetime as dt
LIMITE_GO = float(os.environ.get('LIMITE_GO', '5')); SEUIL = 0.60
R = os.environ['GITHUB_REPOSITORY']; TOK = os.environ['GH_TOKEN']; ESSAI = os.environ.get('ESSAI') == '1'
def api(p, m='GET'):
    q = urllib.request.Request('https://api.github.com/repos/' + R + p, method=m, headers={'Authorization': 'Bearer ' + TOK, 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(q) as r: return json.load(r) if r.status != 204 else None
def date(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
rel = []
for page in range(1, 20):
    x = api(f'/releases?per_page=100&page={page}')
    if not x: break
    rel += x
maintenant = dt.datetime.now(dt.timezone.utc)
taille = lambda r: sum(a['size'] for a in r['assets'])
total = sum(map(taille, rel)); log = [f'Releases : {len(rel)}, {total / 1e9:.2f} Go sur {LIMITE_GO:.0f} Go ({100 * total / (LIMITE_GO * 1e9):.0f} %), seuil {int(SEUIL * 100)} %']
issues = {}
for r in rel:
    if r['tag_name'].startswith('episode-'):
        n = r['tag_name'].split('-')[1]
        if n not in issues or date(r['created_at']) > date(issues[n]['created_at']): issues[n] = r
protege = set()
for n, r in issues.items():
    try: i = api(f'/issues/{n}')
    except Exception: continue
    if maintenant - date(i['updated_at']) < dt.timedelta(days=30): protege.add(r['id'])
if rel: protege.add(max(rel, key=lambda r: date(r['created_at']))['id'])   # la toute dernière fabrication reste toujours
def supprimer(r, pourquoi):
    global total
    log.append(f"supprimée : {r['tag_name']} ({taille(r) / 1e6:.0f} Mo) — {pourquoi}")
    if not ESSAI:
        api(f"/releases/{r['id']}", 'DELETE')
        try: api(f"/git/refs/tags/{r['tag_name']}", 'DELETE')
        except Exception: pass
    total -= taille(r)
for r in sorted(rel, key=lambda r: date(r['created_at'])):   # aperçus anciens
    if r['tag_name'].startswith('apercu-') and maintenant - date(r['created_at']) > dt.timedelta(days=14) and r['id'] not in protege: supprimer(r, 'aperçu de plus de 14 jours')
restants = [r for r in sorted(rel, key=lambda r: date(r['created_at'])) if not (r['tag_name'].startswith('apercu-') and maintenant - date(r['created_at']) > dt.timedelta(days=14))]
for r in restants:   # au-dessus de 60 % : les plus anciennes d'abord
    if total <= SEUIL * LIMITE_GO * 1e9: break
    if r['id'] in protege: continue
    supprimer(r, 'place au-dessus de 60 %')
log.append(f'Après le ménage : {total / 1e9:.2f} Go ({100 * total / (LIMITE_GO * 1e9):.0f} %)')
d = api('')['size'] / 1024 / 1024
log.append(f'Dépôt (scripts, poses, historique) : {d:.2f} Go' + (' — au-dessus de 60 % de 5 Go : grand ménage automatique de l\'historique' if d > 3 else ''))
if os.environ.get('GITHUB_OUTPUT'): open(os.environ['GITHUB_OUTPUT'], 'a').write(f"grand={'oui' if d > 3 or os.environ.get('FORCER') == '1' else 'non'}\n")
print('\n'.join(log))
if os.environ.get('GITHUB_STEP_SUMMARY'): open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write('\n'.join('- ' + l for l in log) + '\n')
