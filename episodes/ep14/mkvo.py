import json,subprocess,librosa,soundfile as sf,numpy as np
IX=json.load(open('ix.json'))
def ld(n): return librosa.load(f'v/{n}.wav',sr=24000)[0]
for n,i in IX.items():
    if n.startswith('vo'): continue
    y=ld(n)
    if False:
        import scipy.signal as ss; b,a_=ss.butter(4,600/12000); y=ss.lfilter(b,a_,y)
    sf.write('vo/tmp.wav',y/np.abs(y).max()*0.9,24000,subtype='PCM_16'); subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i','vo/tmp.wav','-filter:a','atempo=1.1','-c:a','pcm_s16le',f'vo/L{i:02d}.wav'])
print('ok')
