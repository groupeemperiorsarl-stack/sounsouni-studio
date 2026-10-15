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

def say_text(t):
    # écriture adaptée à la prononciation (guillemets et tirets retirés)
    return re.sub(r'[«»"“”]', '', t).replace(' – ', ', ').strip()

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
def run(events, cast, work, log=print):
    os.makedirs(work + '/voix', exist_ok=True)
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
                y = y[int(max(0, first - 0.12) * sr):int(min(len(y) / sr, last + 0.18) * sr)]
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
