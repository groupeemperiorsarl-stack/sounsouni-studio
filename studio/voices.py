"""Voix : génération (Chatterbox), contrôle par transcription (faster-whisper), nouvelles tentatives,
nettoyage des fins ratées, accélération légère, effets (téléphone, pensée) et temps de chaque mot."""
import os, json, hashlib, subprocess, difflib, re, unicodedata
import numpy as np, soundfile as sf
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
TTS_PY = os.environ.get('STUDIO_TTS_PY', '/home/claude/tts/venv/bin/python')
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tts_worker.py')
SR = 24000; TEMPO = 1.1

def words(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9' ]", ' ', s.replace('-', ' ')).split()

def style(line):
    v = line.get('voice', 'normal'); e = line.get('emotion', 'neutre')
    ex = 0.5
    if 'crie' in v or e in ('colere', 'furieux', 'panique', 'choc'): ex = 0.7
    if 'chuchote' in v or e in ('triste', 'gene', 'timide'): ex = 0.35
    if 'rit' in v or e in ('rire', 'joie'): ex = 0.6
    return ex, 0.5

def plus_muet(t):
    """« plus » négatif (ne… plus, non plus, plus jamais/rien) se dit « plu » : on l'écrit ainsi pour la voix."""
    out = []
    for clause in re.split(r'([.!?;,…:])', t):
        neg = re.search(r"\b(ne|n['’])", clause, re.I)
        def rep(m):
            nxt = clause[m.end():].lstrip().lower()
            if re.match(r"(jamais|rien|personne|du tout|aucun)", nxt) or neg or re.search(r'non\s+$', clause[:m.start()].lower()):
                return m.group(0)[:-1]   # « plus » → « plu »
            return m.group(0)
        out.append(re.sub(r'\b[Pp]lus\b', rep, clause))
    return ''.join(out)

def speech_end(y, sr, t_last):
    """Fin réelle de la parole : depuis le dernier mot reconnu, on avance tant que la voix continue
    (jusqu'à un silence de 0,35 s), au plus 1,6 s plus loin."""
    hop = int(sr * 0.02); n = len(y) // hop
    if n < 3: return t_last
    rms = np.sqrt(np.array([np.mean(y[i * hop:(i + 1) * hop] ** 2) for i in range(n)]))
    thr = max(rms.max() * 0.07, 1e-4); i = int(t_last / 0.02); end = i; quiet = 0
    while i < n and i * 0.02 < t_last + 1.6:
        if rms[i] > thr: end = i; quiet = 0
        else:
            quiet += 1
            if quiet * 0.02 >= 0.35: break
        i += 1
    return max(t_last, (end + 1) * 0.02)
LEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lexique.txt')
def lexique(t):
    """Prononciations corrigées (fichier lexique.txt : « écrit = prononcé », une par ligne)."""
    if not os.path.exists(LEX): return t
    for line in open(LEX, encoding='utf-8'):
        if '=' not in line or line.strip().startswith('#'): continue
        a, b = [x.strip() for x in line.split('=', 1)]
        if a: t = re.sub(re.escape(a), b, t, flags=re.I)
    return t
def say_text(t):
    # écriture adaptée à la prononciation (guillemets et tirets retirés, « plus » négatif sans S)
    return lexique(plus_muet(re.sub(r'[«»"“”]', '', t).replace(' – ', ', ').strip()))

def gen(jobs, work):
    if not jobs: return
    p = os.path.join(work, 'tts_jobs.json'); json.dump(jobs, open(p, 'w'))
    subprocess.run([TTS_PY, WORKER, p], check=False)

def fake(lines, work):
    # mode essai rapide : fausses voix (bips rythmés) de durée réaliste
    for e in lines:
        n = len(words(e['text'])); d = max(0.8, n * 0.28); t = np.arange(int(d * SR)) / SR
        y = 0.3 * np.sin(2 * np.pi * 180 * t) * (np.sin(2 * np.pi * 4 * t) > 0)
        e['wav'] = f"{work}/voix/{e['id']}.wav"; sf.write(e['wav'], y, SR, subtype='PCM_16'); e['dur'] = d
        e['word_times'] = {str(i): i * d / max(1, n) for i in range(n)}
        tok = e['text'].split(); tw = []; c = 0
        for tk in tok: tw.append(c); c += len(words(say_text(tk)))
        tw.append(c); e['tok_word'] = tw
        e['tag_times'] = [[tw[min(i, len(tw) - 1)] * d / max(1, n), tag] for i, tag in e['tags']]
    return lines
LAUGH = {'rire', 'rire_retenu', 'rit', 'rigole', 'eclate_de_rire', 'moqueur'}
def laughers(events):
    """Qui rit dans le script, et quelle sorte de rire (éclat / petit rire retenu)."""
    out = set()
    for e in events:
        if e['type'] == 'reaction' and set(e.get('actions', [])) & LAUGH: out |= {(e['who'], 'eclat'), (e['who'], 'petit')}
        if e['type'] == 'line' and (e.get('emotion') in ('rire', 'rire_retenu', 'moqueur') or 'rit' in e.get('voice', '') or any(tg in ('rire', 'rire_retenu') for _, tg in e.get('tags', []))):
            out.add((e['who'], 'petit' if e.get('emotion') in ('rire_retenu', 'moqueur') else 'eclat'))
    return out
def make_laughs(events, cast, work, log=print, only_jobs=False):
    """Rires des personnages (studio/rires.py) : ceux choisis par Issa, sinon de vrais rires fabriqués avec Chatterbox Turbo."""
    if only_jobs: return []   # fabriqués à l'étape « plans » (souvent déjà choisis et gardés dans assets/rires)
    import rires; rires.pour_episode(laughers(events), work, log)
def run(events, cast, work, log=print):
    os.makedirs(work + '/voix', exist_ok=True)
    if not os.environ.get('STUDIO_FAUSSES_VOIX'): make_laughs(events, cast, work, log)
    lines = [e for e in events if e['type'] == 'line']
    for e in lines: e['_say'] = say_text(e['text'])
    if os.environ.get('STUDIO_FAUSSES_VOIX'): log('voix : mode essai (fausses voix)'); return fake(lines, work)
    todo = {}
    for e in lines:
        ref = A + '/voix/' + cast['voices'].get(e['who'], 'ref_bakary.wav')
        ex, cfg = style(e); txt = say_text(e['text'])
        e['_ref'], e['_ex'], e['_cfg'], e['_say'] = ref, ex, cfg, txt
    from faster_whisper import WhisperModel
    wm = None
    for attempt in range(3):
        jobs = []
        for e in lines:
            if e.get('_ok'): continue
            h = hashlib.md5(f"{e['_say']}|{e['_ref']}|{e['_ex']}|{e['_cfg']}|{attempt}".encode()).hexdigest()[:12]
            e['_raw'] = f"{work}/voix/raw_{h}.wav"
            if not os.path.exists(e['_raw']): jobs.append({'out': e['_raw'], 'ref': e['_ref'], 'text': e['_say'], 'exag': e['_ex'], 'cfg': e['_cfg']})
        log(f'voix : essai {attempt + 1}, {len(jobs)} répliques à générer')
        gen(jobs, work)
        if wm is None: wm = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=2)
        for e in lines:
            if e.get('_ok') or not os.path.exists(e.get('_raw', '')): continue
            y, sr = sf.read(e['_raw']); y = y if y.ndim == 1 else y.mean(1)
            import librosa
            y16 = librosa.resample(y.astype(np.float32), orig_sr=sr, target_sr=16000)
            segs, _ = wm.transcribe(y16, language='fr', word_timestamps=True, beam_size=1)
            ws = [w for s in segs for w in s.words]
            ref = words(e['_say']); hyp = [(words(w.word) or [''])[0] for w in ws]
            sm = difflib.SequenceMatcher(None, ref, hyp); score = sm.ratio()
            mapping = {}
            for a, b, n in sm.get_matching_blocks():
                for k in range(n): mapping[a + k] = (ws[b + k].start, ws[b + k].end)
            e['_score'] = round(score, 2)
            if score >= 0.6 or attempt == 2:
                # fin : juste après le dernier mot reconnu du texte (supprime les sons parasites ajoutés)
                last = max([v[1] for v in mapping.values()] or [len(y) / sr]); first = min([v[0] for v in mapping.values()] or [0])
                last = speech_end(y, sr, last)   # ne jamais couper le dernier mot : on suit la voix jusqu'au vrai silence
                y = y[int(max(0, first - 0.12) * sr):int(min(len(y) / sr, last + 0.22) * sr)]
                e['_ok'] = True; e['_map'] = {k: ((v[0] - max(0, first - 0.12)) / TEMPO, (v[1] - max(0, first - 0.12)) / TEMPO) for k, v in mapping.items()}
                tmp = f"{work}/voix/tmp.wav"; sf.write(tmp, y / (np.abs(y).max() + 1e-6) * 0.9, sr, subtype='PCM_16')
                af = f'atempo={TEMPO}'
                if 'telephone' in e.get('voice', ''): af += ',highpass=f=400,lowpass=f=3200'
                if e.get('thought'): af += ',aecho=0.8:0.7:40:0.25'
                out = f"{work}/voix/{e['id']}.wav"
                subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', tmp, '-ar', str(SR), '-ac', '1', '-filter:a', af, '-c:a', 'pcm_s16le', out])
                e['wav'] = out; e['dur'] = sf.info(out).duration
            else:
                e['_ex'] = max(0.3, e['_ex'] - 0.15)   # nouvelle tentative, plus calme
        if all(e.get('_ok') for e in lines): break
    # temps des balises accrochées aux mots
    for e in lines:
        n = len(words(e['_say'])); mp = e.get('_map', {})
        def t_of(i):
            if i in mp: return mp[i][0]
            ks = sorted(mp)
            if not ks: return e.get('dur', 1) * i / max(1, n)
            lo = [k for k in ks if k < i]; hi = [k for k in ks if k > i]
            if lo and hi: return (mp[lo[-1]][1] + mp[hi[0]][0]) / 2
            return mp[lo[-1]][1] if lo else mp[hi[0]][0]
        tok = e['text'].split(); tw = []; c = 0
        for tk in tok: tw.append(c); c += len(words(say_text(tk)))
        tw.append(c)
        e['tag_times'] = [[t_of(tw[min(i, len(tw) - 1)]), tag] for i, tag in e['tags']]
        e['tok_word'] = tw
        e['word_times'] = {str(i): t_of(i) for i in range(n)}
    bad = [(e['id'], e['_score']) for e in lines if e.get('_score', 1) < 0.6]
    if bad: log('voix à vérifier : ' + ', '.join(f'{i} ({s})' for i, s in bad))
    return lines

def first_jobs(events, cast, work):
    """Toutes les voix à fabriquer (premier essai) : sert à répartir le travail sur plusieurs ordinateurs."""
    os.makedirs(work + '/voix', exist_ok=True)
    jobs = list(make_laughs(events, cast, work, only_jobs=True) or [])
    for e in [e for e in events if e['type'] == 'line']:
        ref = A + '/voix/' + cast['voices'].get(e['who'], 'ref_bakary.wav')
        ex, cfg = style(e); txt = say_text(e['text'])
        h = hashlib.md5(f"{txt}|{ref}|{ex}|{cfg}|0".encode()).hexdigest()[:12]
        out = f"{work}/voix/raw_{h}.wav"
        if not os.path.exists(out): jobs.append({'out': out, 'ref': ref, 'text': txt, 'exag': ex, 'cfg': cfg})
    return jobs
def gen_part(events, cast, work, i, n, log=print):
    jobs = first_jobs(events, cast, work)[i::n]; log(f'voix : part {i + 1}/{n}, {len(jobs)} à fabriquer'); gen(jobs, work)
