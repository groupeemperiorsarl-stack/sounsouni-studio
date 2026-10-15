"""Exécuté dans l'environnement Chatterbox : génère les voix d'une liste de travaux (JSON).
Chaque travail : {"out": "...wav", "ref": "...wav", "text": "...", "exag": 0.5, "cfg": 0.5}"""
import sys, json, time, functools, torch
torch.set_num_threads(2)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torchaudio as ta
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
m.s3gen.inference = functools.partial(m.s3gen.inference, n_cfm_timesteps=5)
CUR = {'mx': 1000}
_t3 = m.t3.inference
def _inf(*a, **k):
    k['max_new_tokens'] = CUR['mx']; return _t3(*a, **k)
m.t3.inference = _inf
jobs = json.load(open(sys.argv[1]))
for j in jobs:
    t = time.time()
    # limite la longueur générée (évite les voix qui « déraillent » et saturent la mémoire)
    CUR['mx'] = min(1000, int(60 + len(j['text']) * 2.9))
    w = m.generate(j['text'], language_id='fr', audio_prompt_path=j['ref'], exaggeration=j['exag'], cfg_weight=j['cfg'])
    ta.save(j['out'], w, m.sr); print('OK', j['out'], round(time.time() - t, 1), flush=True)
