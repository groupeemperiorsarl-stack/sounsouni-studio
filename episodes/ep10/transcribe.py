import json, glob, os
from faster_whisper import WhisperModel
import soundfile as sf, numpy as np, scipy.signal as ss
def decode_audio(f,sr):
    a,r=sf.read(f,dtype='float32'); a=a.mean(1) if a.ndim>1 else a; return ss.resample_poly(a,sr,r).astype('float32')
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=1)
out={}
for f in sorted(glob.glob('rec/*.wav')):
    k=os.path.basename(f).split('_-_')[1][:-4]; y=decode_audio(f,16000)
    segs,_=m.transcribe(y,language='fr',beam_size=2,word_timestamps=True)
    W=[(round(w.start,2),round(w.end,2),w.word.strip()) for s in segs for w in s.words]
    out[k]={'f':f,'w':W}
    with open('rec/tr.txt','a') as fh: fh.write(f'== {k}\n'+' '.join(f'{w[2]}[{w[0]:.1f}-{w[1]:.1f}]' for w in W)+'\n')
    json.dump(out,open('rec/words.json','w'),ensure_ascii=False)
print('TR_DONE')
