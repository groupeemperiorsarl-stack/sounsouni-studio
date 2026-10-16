"""Exécuté dans l'environnement Chatterbox : génère les voix d'une liste de travaux (JSON).
Chaque travail : {"out": "...wav", "ref": "...wav", "text": "...", "exag": 0.5, "cfg": 0.5}"""
import sys, json, time, functools, torch
torch.set_num_threads(2)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torchaudio as ta
import perth
if getattr(perth, 'PerthImplicitWatermarker', None) is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker   # module de filigrane absent sur certaines machines
jobs = json.load(open(sys.argv[1]))
CUR = {'mx': 1000}
if any(not j.get('turbo') for j in jobs):
    m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
    m.s3gen.inference = functools.partial(m.s3gen.inference, n_cfm_timesteps=5)
    _t3 = m.t3.inference
    def _inf(*a, **k):
        k['max_new_tokens'] = CUR['mx']; return _t3(*a, **k)
    m.t3.inference = _inf
TURBO = None
def turbo():
    """Chatterbox Turbo (MIT) : vrais rires [laugh] / [chuckle] avec la voix du personnage."""
    global TURBO
    if TURBO is None:
        import numpy as np
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        TURBO = ChatterboxTurboTTS.from_pretrained(device='cpu'); _nl = TURBO.norm_loudness
        TURBO.norm_loudness = lambda w, sr: np.asarray(_nl(w, sr), dtype=np.float32)
    return TURBO
for j in jobs:
    t = time.time()
    if j.get('turbo'):
        tm = turbo(); w = tm.generate(j['text'], audio_prompt_path=j['ref'], exaggeration=j.get('exag', 0.5), temperature=j.get('temp', 0.8))
        ta.save(j['out'], w, tm.sr); print('OK', j['out'], round(time.time() - t, 1), flush=True); continue
    # limite la longueur générée (évite les voix qui « déraillent » et saturent la mémoire)
    CUR['mx'] = min(1000, int(60 + len(j['text']) * 2.9))
    w = m.generate(j['text'], language_id='fr', audio_prompt_path=j['ref'], exaggeration=j['exag'], cfg_weight=j['cfg'])
    ta.save(j['out'], w, m.sr); print('OK', j['out'], round(time.time() - t, 1), flush=True)
