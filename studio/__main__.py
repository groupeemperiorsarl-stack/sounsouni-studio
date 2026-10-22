"""Sounsouni Studio — du script détaillé à l'épisode fini.
Utilisation :  python -m studio episode.txt  [-o dossier_sortie]  [--plans-seulement]
Planches à valider :  --planches  [--plans 12,14-16 | --de 1:20 --a 1:45]  [--sujet pose,cadrage]
Réponse d'Issa :      --choix "1B 3C"   (gardée dans episode.choix.json, puis la mise en scène la suit)
"""
import sys, os, json, argparse, hashlib, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import script, voices, director, render, audio, planches
def versions(final, log):
    """Règle de publication (validée par Issa) : versions YouTube complète, TikTok 3:00, Shorts 2:58, Facebook 1:00 avec bandeau « chaîne YouTube »."""
    if os.environ.get('STUDIO_SANS_VERSIONS'): return
    try:
        import publication
        for f in publication.fabriquer_versions(final): log(f'version de publication : {os.path.basename(f)}')
    except Exception as e: log(f'versions de publication impossibles : {e}')
def resume(shots, out):
    """Liste minutée des plans (plans_resume.json), lue par l'assistant de secours : « à 1:20 » = quel plan, qui, quelle pose."""
    def _qui(s): return [{'qui': x['who'], 'pose': x.get('key'), 'x': round(x.get('x', 0) / 1080, 2), 'taille': round(x.get('h', 0) / 1920, 2), 'retourne': bool(x.get('flip'))} for x in s.get('actors', []) if x.get('who')]
    json.dump([{'plan': i, 'debut': f"{int(s['t0'] // 60)}:{s['t0'] % 60:04.1f}", 'duree': round(s['dur'], 1), 'type': s.get('kind'), 'decor': s.get('decor'),
                'parle': s.get('who'), 'texte': ((s.get('line') or {}).get('text') if isinstance(s.get('line'), dict) else '') or s.get('text') or s.get('title') or '', 'cadrage': s.get('cadrage') or s.get('mode'),
                'acteurs': _qui(s)} for i, s in enumerate(shots)], open(os.path.join(out, 'plans_resume.json'), 'w'), ensure_ascii=False, indent=0)   # liste minutée des plans, lue par l'assistant
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('-o', '--out', default=None)
    ap.add_argument('--plans-seulement', action='store_true', help="s'arrête après la mise en scène (aperçu des plans)")
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--etape', choices=['voix', 'plans', 'rendu', 'final'], default=None, help='une seule étape (pour répartir sur plusieurs ordinateurs)')
    ap.add_argument('--part', default=None, help='i/n : cette machine fait la part i sur n')
    ap.add_argument('--planches', action='store_true', help='fabrique les planches A / B / C / D à valider (images fixes), puis s\'arrête')
    ap.add_argument('--plans', default=None, help='plans concernés, ex. 12,14-16 (sinon : les plans où l\'application hésite)')
    ap.add_argument('--de', default=None, help='début des secondes concernées, ex. 1:20'); ap.add_argument('--a', default=None, help='fin, ex. 1:45')
    ap.add_argument('--sujet', default='pose,cadrage', help='pose, cadrage ou les deux')
    ap.add_argument('--choix', default=None, help='réponse d\'Issa aux planches, ex. "1B 3C"')
    ap.add_argument('--fichier-choix', default=None, help='par défaut : à côté du script, même nom + .choix.json')
    a = ap.parse_args()
    name = os.path.splitext(os.path.basename(a.script))[0]; out = a.out or os.path.join(os.getcwd(), 'sortie_' + name)
    work = os.path.join(out, 'travail'); os.makedirs(work, exist_ok=True)
    logf = open(os.path.join(out, 'journal.txt'), 'a')
    def log(m): s = time.strftime('%H:%M:%S ') + m; print(s, flush=True); logf.write(s + '\n'); logf.flush()
    log(f'== {a.script}')
    meta, ev = script.parse(open(a.script, encoding='utf-8').read())
    try:   # nouvelles poses pas encore analysées : l'application reconnaît elle-même les objets dessus
        import autotag; new = [k for k, p in director.POSES.items() if p['char'] != 'OBJET' and 'props_auto' not in p and '@' not in k]
        if new: log(f'analyse des objets sur {len(new)} nouvelles poses'); autotag.run(new); director.reload()
    except Exception as err: log(f'analyse des objets impossible : {err}')
    log(f"script : {sum(1 for e in ev if e['type'] == 'line')} répliques, {sum(1 for e in ev if e['type'] == 'scene')} scènes")
    if not any(e['type'] == 'line' for e in ev):   # script brut (pas au format) : on s'arrête tout de suite avec un message clair
        log("ERREUR : script pas au format du studio (aucune réplique « NOM (émotion · regarde: …) » trouvée). "
            "Passez d'abord par l'onglet 🤖 Assistant de la page Studio mobile (« Mettre au format »), puis relancez."); sys.exit(2)
    part = tuple(int(x) for x in a.part.split('/')) if a.part else None
    if a.etape == 'voix':
        voices.gen_part(ev, director.CAT, work, part[0], part[1], log) if part else voices.gen(voices.first_jobs(ev, director.CAT, work), work); return
    if a.etape in ('rendu', 'final'):
        shots = json.load(open(os.path.join(work, 'plans.json'))); tot = shots[-1]['t0'] + shots[-1]['dur']
        for sh in shots:
            for ac in sh.get('actors', []):
                for kk in (ac.get('key'), ac.get('stop_key')):
                    if kk and '@' in kk and kk not in director.POSES: director.yaw_variant(*director.parse_variant(kk))
        if a.etape == 'rendu': render.video(shots, tot, work, a.workers, log, part=part); return
        resume(shots, out)
        silent = render.video(shots, tot, work, a.workers, log); v, m = audio.build(shots, tot, work, log)
        final = os.path.join(out, name + '.mp4'); audio.mix(silent, v, m, final); ok = audio.light(final, os.path.join(out, name + '_leger.mp4'), tot); versions(final, log)
        log(f"fini : {final} ({tot:.0f} s) — version légère {'vérifiée' if ok else 'À VÉRIFIER'}"); return
    cpath = a.fichier_choix or os.path.splitext(a.script)[0] + '.choix.json'
    if a.choix:
        pj = os.path.join(out, 'planches', 'planches.json')
        if os.path.exists(pj): planches.appliquer(a.choix, pj, cpath, log)
        else: log('choix : planches.json introuvable (lancer d\'abord --planches)')
    choix = json.load(open(cpath, encoding='utf-8')) if os.path.exists(cpath) else {}
    if choix: log(f'choix d\'Issa appliqués : {len(choix)} plan(s) ({os.path.basename(cpath)})')
    lines = voices.run(ev, director.CAT, work, log)
    shots, tot = director.build(meta, ev, log, choix=choix, variantes=a.planches)
    if director.MANQUES:   # émotions sans image : visage calme à la place ; liste gardée pour le relecteur et la fiche Gemini
        json.dump(sorted(director.MANQUES), open(os.path.join(out, 'manques.json'), 'w'), ensure_ascii=False); log('images manquantes (visage calme à la place) : ' + ', '.join(f'{c} {e} ({p})' for c, e, p in sorted(director.MANQUES)))
    json.dump(shots, open(os.path.join(work, 'plans.json'), 'w'), ensure_ascii=False, indent=0, default=str)
    resume(shots, out)
    render.prepare_turns(shots, log)
    render.contact(shots, os.path.join(out, 'apercu_plans.png')); log('aperçu des plans : apercu_plans.png')
    if a.planches:
        sel = planches.choisir_plans(shots, planches.lire_plans(a.plans), planches.lire_temps(a.de), planches.lire_temps(a.a))
        planches.make(shots, out, sel, tuple(a.sujet.split(',')), choix, log, a.script); return
    if a.plans_seulement or a.etape == 'plans': return
    A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    stamp = [os.path.getmtime(os.path.join(A, 'catalog.json'))] + sorted(os.path.getmtime(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(A, 'poses')) for f in fs if f.endswith('.webp'))[-3:]
    h = hashlib.md5(str(stamp).encode()).hexdigest()[:10]   # images de poses changées = on refait tout ; un plan changé = seulement ses morceaux (render.video)
    if open(os.path.join(work, 'plans.hash')).read() != h if os.path.exists(os.path.join(work, 'plans.hash')) else True:
        for f in os.listdir(work):
            if f.startswith('seg_'): os.remove(os.path.join(work, f))
        open(os.path.join(work, 'plans.hash'), 'w').write(h)
    silent = render.video(shots, tot, work, a.workers, log)
    v, m = audio.build(shots, tot, work, log)
    final = os.path.join(out, name + '.mp4'); audio.mix(silent, v, m, final)
    ok = audio.light(final, os.path.join(out, name + '_leger.mp4'), tot); versions(final, log)
    log(f"fini : {final} ({tot:.0f} s) — version légère {'vérifiée' if ok else 'À VÉRIFIER'}")
if __name__ == '__main__': main()
