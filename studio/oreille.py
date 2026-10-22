"""L'OREILLE du studio : écoute le son d'une vidéo finie avec earshot (outil libre, MIT, github.com/Leonxlnx/earshot, sur processeur, sans clé)
et écrit ecoute.txt, un compte rendu en mots que l'assistant de discussion et le technicien lisent (ils « entendent » ainsi la vidéo).
Alertes automatiques : scène aux aigus perçants (cri d'insecte, sifflement), son qui sature, scène trop forte ou trop faible.
Utilisation : python studio/oreille.py video.mp4 plans.json -o ecoute.txt   (EARSHOT = commande earshot, par défaut « earshot »)"""
import os, sys, json, subprocess, tempfile, argparse, statistics
EAR = os.environ.get('EARSHOT', 'earshot')

def _cmd(args, timeout=900):
    r = subprocess.run([EAR] + args + ['--json'], capture_output=True, text=True, timeout=timeout)
    if r.returncode: raise RuntimeError((r.stderr or r.stdout).strip()[-300:])
    return json.loads(r.stdout)

def ecouter(video, plans, sortie, complet=True, log=print):
    shots = json.load(open(plans, encoding='utf-8')); D = tempfile.mkdtemp(); wav = os.path.join(D, 'son.wav')
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', video, '-vn', '-ac', '1', '-ar', '48000', wav], check=True)
    scenes = []   # scènes = suites de plans dans le même décor
    for s in shots:
        d = s.get('decor') or s.get('decor_name') or '?'
        t0 = s.get('t0', 0); fin = t0 + s.get('dur', 0)
        if scenes and scenes[-1]['decor'] == d: scenes[-1]['fin'] = fin; scenes[-1]['ambiance'] = scenes[-1]['ambiance'] or s.get('ambiance', '') or ''
        else: scenes.append({'decor': d, 'debut': t0, 'fin': fin, 'ambiance': s.get('ambiance', '') or ''})
    mm = lambda t: f'{int(t // 60)}:{int(t % 60):02d}'
    L, alertes = [], []
    g = _cmd(['measure', wav]); L.append(f"SON DE LA VIDÉO ({mm(g['duration'])}) : {g['lufs']} LUFS (cible -14), crête {g['true_peak_dbtp']} dBTP, écart de volume {g['lra_lu']} LU.")
    if g['true_peak_dbtp'] > -1: alertes.append(f"le son touche presque le maximum (crête {g['true_peak_dbtp']} dBTP) : risque de grésillement après envoi sur TikTok/Facebook")
    mes = []
    for i, sc in enumerate(scenes):
        if sc['fin'] - sc['debut'] < 3: continue
        f = os.path.join(D, f's{i}.wav'); subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-ss', str(sc['debut']), '-t', str(sc['fin'] - sc['debut']), '-i', wav, f], check=True)
        m = _cmd(['measure', f]); b = m.get('bands_db') or {}; mes.append((sc, m, b))
    pres = [b.get('presence') for _, _, b in mes if b.get('presence') is not None]; med = statistics.median(pres) if pres else None
    L.append('\nPAR SCÈNE (début-fin · décor · ambiance : volume, brillance, aigus « presence » 4-6 kHz par rapport aux autres scènes)')
    for sc, m, b in mes:
        p = b.get('presence'); ecart = (p - med) if (p is not None and med is not None) else 0
        L.append(f"- {mm(sc['debut'])}-{mm(sc['fin'])} · {sc['decor']}{' · ' + sc['ambiance'] if sc['ambiance'] else ''} : {m['lufs']} LUFS, brillance {m['brightness_hz']} Hz, aigus {p} dB ({ecart:+.0f} dB)")
        if ecart > 5: alertes.append(f"{mm(sc['debut'])}-{mm(sc['fin'])} ({sc['decor']}) : aigus perçants {ecart:+.0f} dB plus forts que dans les autres scènes (cri d'insecte, sifflement ?) : stressant à l'écoute")
        if m['lufs'] > g['lufs'] + 4: alertes.append(f"{mm(sc['debut'])}-{mm(sc['fin'])} ({sc['decor']}) : nettement plus fort que le reste ({m['lufs']} LUFS)")
    if complet:   # ce que l'oreille entend, seconde par seconde (modèles CLAP + AST, environ 3 à 6 min sur processeur)
        try:
            tl = subprocess.run([EAR, 'timeline', wav], capture_output=True, text=True, timeout=1500).stdout
            L.append('\nCE QUE L\'OREILLE ENTEND (earshot timeline ; les étiquettes de sons sont des indices, les temps et niveaux sont des mesures)\n' + tl.split('\nNOTES')[0].strip()[:9000])
        except Exception as e: L.append('\n(écoute détaillée impossible : ' + str(e)[:200] + ')')
    txt = ('ALERTES :\n' + '\n'.join('- ' + a for a in alertes) if alertes else 'ALERTES : aucune (rien d\'anormal entendu).') + '\n\n' + '\n'.join(L) + '\n'
    open(sortie, 'w', encoding='utf-8').write(txt); log(f'oreille : {len(alertes)} alerte(s) → {sortie}'); return alertes

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('plans'); ap.add_argument('-o', default='ecoute.txt'); ap.add_argument('--rapide', action='store_true')
    a = ap.parse_args(); ecouter(a.video, a.plans, a.o, complet=not a.rapide)
