"""Piste son : voix placées au bon instant, bruitages, ambiance, musique, mixage final."""
import os, subprocess, wave
import numpy as np, soundfile as sf, librosa
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); SR = 44100
GAIN = {'thunder': 0.6, 'cricket': 0.45, 'heart': 0.45, 'crowd': 0.3, 'boum': 0.8, 'door': 0.9, 'sew': 0.5, 'klaxon': 0.45, 'pourw': 0.35, 'whistlew': 0.35,
        'beeps': 0.35, 'motor': 0.5, 'sparkle': 0.4, 'heels': 0.6, 'steps': 0.5, 'call': 0.5, 'buzz': 0.6}
def rd(p):
    y, sr = sf.read(p); y = y if y.ndim == 1 else y.mean(1)
    if sr != SR: y = librosa.resample(y.astype(np.float32), orig_sr=sr, target_sr=SR)
    return y
def build(shots, tot, work, log=print):
    out = np.zeros(int(tot * SR) + SR, np.float32)
    def put(y, t, g=1.0):
        i = int(t * SR); j = min(len(out), i + len(y))
        if 0 <= i < len(out): out[i:j] += y[:j - i] * g
    for s in shots:
        ln = s.get('line')
        if ln and ln.get('wav'): y = rd(ln['wav']); put(y / (np.abs(y).max() + 1e-6) * 0.75, s['t0'] + s.get('lead', 0))
        for sx in s.get('sfx', []):
            t, f = sx[0], sx[1]; g = sx[2] if len(sx) > 2 else None
            if f.startswith('rire:'):   # rire du personnage, fabriqué avec sa propre voix
                c, _, so = f[5:].partition(':'); p = f'{work}/voix/rire_{c}' + (f'_{so}' if so else '') + '.wav'
                if not os.path.exists(p): p = f'{work}/voix/rire_{c}.wav'
                if os.path.exists(p): y = rd(p); put(y / (np.abs(y).max() + 1e-6) * 0.7, s['t0'] + t, g or 0.9)
                continue
            p = f'{A}/sfx/{f}.wav'
            if os.path.exists(p): put(rd(p), s['t0'] + t, g or GAIN.get(f, 0.6))
    # ambiances par scène
    for s in shots:
        amb = s.get('ambiance', '')
        f = 'crowd' if 'marche' in amb else ('cricket' if 'grillon' in amb else None)
        if f:
            y = rd(f'{A}/sfx/{f}.wav'); y = np.resize(y, int(s['dur'] * SR)); put(y, s['t0'], 0.10)
    w = f'{work}/voix.wav'; sf.write(w, np.clip(out[:int(tot * SR)], -1, 1), SR, subtype='PCM_16')
    import music; m = f'{work}/musique.wav'; music.make(tot, m)
    return w, m
def mix(video, voice, music, final):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', voice, '-i', music, '-filter_complex',
                    '[1:a]aresample=44100,asplit=2[v1][v2];[2:a]aresample=44100,volume=0.5[m];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];'
                    '[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-shortest', '-movflags', '+faststart', final], check=True)
def light(final, light_out, tot, max_mb=28):
    kbps = int(max_mb * 8 * 1024 / tot) - 100
    if os.path.getsize(final) < max_mb * 1024 * 1024 * 0.9: import shutil; shutil.copy(final, light_out); kbps = 0
    if kbps:
     subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', final, '-c:v', 'libx264', '-b:v', f'{kbps}k', '-preset', 'fast', '-tune', 'animation',
                    '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', light_out], check=True)
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', light_out, '-f', 'null', '-'], capture_output=True, text=True)
    return r.stderr.strip() == ''
