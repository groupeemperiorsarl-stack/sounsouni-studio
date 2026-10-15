import json,subprocess,librosa,soundfile as sf,numpy as np
IX=json.load(open('ix.json'))
def ld(n): return librosa.load(f'v/{n}.wav',sr=24000)[0]
for n,i in IX.items():
    if n.startswith('vo'): continue
    if n=='g':
        a=[ld(x) for x in ('g1','g2','g3')]; L=max(len(x)+int(0.12*24000*k) for k,x in enumerate(a)); y=np.zeros(L)
        for k,x in enumerate(a): o=int(0.12*24000*k); y[o:o+len(x)]+=x/np.abs(x).max()*0.6
    else:
        y=ld(n)
    if n=='d03':
        import scipy.signal as ss; b,a_=ss.butter(4,600/12000); y=ss.lfilter(b,a_,y)
    sf.write('vo/tmp.wav',y/np.abs(y).max()*0.9,24000,subtype='PCM_16'); subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i','vo/tmp.wav','-filter:a','atempo=1.1','-c:a','pcm_s16le',f'vo/L{i:02d}.wav'])
print('ok')
