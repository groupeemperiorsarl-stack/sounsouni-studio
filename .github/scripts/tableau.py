"""Tableau de bord : minutes GitHub utilisées ce mois-ci par ce dépôt, minutes restantes, durée et coût de chaque fabrication.
Écrit le tableau dans la demande épinglée « 📊 Tableau de bord » (créée si besoin)."""
import json, os, subprocess, math, datetime as dt
REPO = os.environ['GITHUB_REPOSITORY']; QUOTA = int(os.environ.get('QUOTA', '2000'))
def api(path, *args):
    r = subprocess.run(['gh', 'api', path, *args], capture_output=True, text=True); return json.loads(r.stdout or '{}')
now = dt.datetime.now(dt.timezone.utc); debut = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
runs, page = [], 1
while True:
    rs = api(f'repos/{REPO}/actions/runs?per_page=100&page={page}&created=>={debut:%Y-%m-%d}').get('workflow_runs', [])
    runs += rs
    if len(rs) < 100: break
    page += 1
def mins(run):
    m, jp = 0, 1
    while True:
        js = api(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100&page={jp}").get('jobs', [])
        for j in js:
            if j.get('started_at') and j.get('completed_at'):
                a = dt.datetime.fromisoformat(j['started_at'].replace('Z', '+00:00')); b = dt.datetime.fromisoformat(j['completed_at'].replace('Z', '+00:00'))
                m += math.ceil(max(0, (b - a).total_seconds()) / 60)
        if len(js) < 100: return m
        jp += 1
def wall(run):
    a = dt.datetime.fromisoformat(run['run_started_at'].replace('Z', '+00:00')); b = dt.datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
    return round((b - a).total_seconds() / 60)
rows, used = [], 0
for r in runs:
    m = mins(r); used += m
    if r['name'].startswith('Fabriquer') and r['status'] == 'completed':
        ap = 'apercu' in (r.get('display_title') or '') or m < 30
        rows.append((r['created_at'][:16].replace('T', ' '), 'Aperçu' if ap else 'Vidéo', wall(r), m, {'success': '✅', 'cancelled': '⏹️'}.get(r['conclusion'], '❌')))
reste = max(0, QUOTA - used)
vids = [x for x in rows if x[1] == 'Vidéo' and x[4] == '✅']
cout = round(sum(x[3] for x in vids) / len(vids)) if vids else 170
attente = round(sum(x[2] for x in vids) / len(vids)) if vids else 30
fin = (debut.replace(month=debut.month % 12 + 1, year=debut.year + (debut.month == 12)))
txt = f"""## 📊 Tableau de bord — {now:%d/%m/%Y %H:%M} (heure de Bamako)

| | |
|---|---|
| Minutes gratuites par mois | **{QUOTA}** |
| Utilisées ce mois-ci (ce dépôt) | **{used}** |
| **Restantes** | **{reste}** ({reste // 60} h {reste % 60:02d}) |
| Remise à zéro | vers le {fin:%d/%m/%Y} |
| Coût moyen d'un épisode complet | ~{cout} minutes |
| Attente moyenne pour un épisode | ~{attente} minutes |
| **Épisodes encore possibles ce mois-ci** | **~{reste // max(1, cout)}** |

### Dernières fabrications
| Date (UTC) | Type | Attente | Minutes | Résultat |
|---|---|---|---|---|
""" + '\n'.join(f'| {d} | {t} | {w} min | {m} | {r} |' for d, t, w, m, r in rows[:12]) + """

_Mis à jour automatiquement après chaque fabrication et chaque matin. Les minutes utilisées par d'autres dépôts du même compte ne sont pas comptées ici._"""
issues = api(f'repos/{REPO}/issues?labels=tableau&state=open')
if issues: n = issues[0]['number']; api(f'repos/{REPO}/issues/{n}', '-X', 'PATCH', '-f', f'body={txt}')
else:
    n = api(f'repos/{REPO}/issues', '-f', 'title=📊 Tableau de bord (minutes GitHub)', '-f', f'body={txt}', '-f', 'labels[]=tableau').get('number')
print(txt)
