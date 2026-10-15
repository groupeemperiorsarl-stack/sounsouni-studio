"""Sounsouni Studio — du script détaillé à l'épisode fini.
Utilisation :  python -m studio episode.txt  [-o dossier_sortie]  [--plans-seulement]
"""
import sys, os, json, argparse, hashlib, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import script, voices, director, render, audio
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('-o', '--out', default=None)
    ap.add_argument('--plans-seulement', action='store_true', help="s'arrête après la mise en scène (aperçu des plans)")
    ap.add_argument('--workers', type=int, default=2)
    a = ap.parse_args()
    name = os.path.splitext(os.path.basename(a.script))[0]; out = a.out or os.path.join(os.getcwd(), 'sortie_' + name)
    work = os.path.join(out, 'travail'); os.makedirs(work, exist_ok=True)
    logf = open(os.path.join(out, 'journal.txt'), 'a')
    def log(m): s = time.strftime('%H:%M:%S ') + m; print(s, flush=True); logf.write(s + '\n'); logf.flush()
    log(f'== {a.script}')
    meta, ev = script.parse(open(a.script, encoding='utf-8').read())
    log(f"script : {sum(1 for e in ev if e['type'] == 'line')} répliques, {sum(1 for e in ev if e['type'] == 'scene')} scènes")
    lines = voices.run(ev, director.CAT, work, log)
    shots, tot = director.build(meta, ev, log)
    json.dump(shots, open(os.path.join(work, 'plans.json'), 'w'), ensure_ascii=False, indent=0, default=str)
    render.prepare_turns(shots, log)
    render.contact(shots, os.path.join(out, 'apercu_plans.png')); log('aperçu des plans : apercu_plans.png')
    if a.plans_seulement: return
    A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    stamp = [os.path.getmtime(os.path.join(A, 'catalog.json'))] + sorted(os.path.getmtime(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(A, 'poses')) for f in fs if f.endswith('.webp'))[-3:]
    h = hashlib.md5((json.dumps(shots, sort_keys=True, default=str) + str(stamp)).encode()).hexdigest()[:10]   # images changées = on refait le rendu
    if open(os.path.join(work, 'plans.hash')).read() != h if os.path.exists(os.path.join(work, 'plans.hash')) else True:
        for f in os.listdir(work):
            if f.startswith('seg_'): os.remove(os.path.join(work, f))
        open(os.path.join(work, 'plans.hash'), 'w').write(h)
    silent = render.video(shots, tot, work, a.workers, log)
    v, m = audio.build(shots, tot, work, log)
    final = os.path.join(out, name + '.mp4'); audio.mix(silent, v, m, final)
    ok = audio.light(final, os.path.join(out, name + '_leger.mp4'), tot)
    log(f"fini : {final} ({tot:.0f} s) — version légère {'vérifiée' if ok else 'À VÉRIFIER'}")
if __name__ == '__main__': main()
