import sys,time,torch
torch.set_num_threads(2)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torchaudio as ta
m=ChatterboxMultilingualTTS.from_pretrained(device='cpu'); import functools; m.s3gen.inference=functools.partial(m.s3gen.inference,n_cfm_timesteps=5)
jobs=[l.rstrip('\n').split('|') for l in open(sys.argv[1]) if l.strip()]
for out,refw,ex,cfg,text in jobs:
    t=time.time(); w=m.generate(text,language_id='fr',audio_prompt_path=refw,exaggeration=float(ex),cfg_weight=float(cfg))
    ta.save(out,w,m.sr); print(out,round(time.time()-t,1),flush=True)
