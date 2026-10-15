import json, numpy as np, wave, librosa
EP='/home/claude/ep12/'
TL=json.load(open(EP+'timeline.json')); TOT=TL['TOT']; SR=44100; L=json.load(open(EP+'dialogue.json'))
GAIN={k:0 for k in ('normal','crie','chuchote','moqueur','lentement','vite')}
def rd(p):
    w=wave.open(p); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    if w.getnchannels()==2: a=a[::2]
    return a,sr
out=np.zeros(int(TOT*SR)+SR,np.float32)
for n,t,li in TL['lines']:
    a,s=rd(EP+f'vo/L{li:02d}.wav'); idx=np.nonzero(np.abs(a)>0.015)[0]; a=a[max(0,idx[0]-300):idx[-1]+1200]
    if s!=SR: a=librosa.resample(a,orig_sr=s,target_sr=SR)
    a=a/(np.abs(a).max()+1e-6)*0.75*10**(GAIN[L[li][1]]/20); i=int(t*SR); out[i:i+len(a)]+=a
G={'ding':0.5,'pop':0.5,'thunder':0.6,'whoosh':0.5,'heels':0.6,'cricket':0.45,'heart':0.4,'crowd':0.3,'click':0.7,'coin':0.5,'steps':0.5,'boum':0.8,'clac':0.9,'call':0.5,'bip':0.5,'sizzle':0.5,'door':0.9,'sew':0.5,'bigsteps':0.9,'buzz':0.6}
for t,f in TL['sfx']:
    a,s=rd(('/home/claude/ep12/' if f in ('sew','bigsteps') else '/home/claude/ep11/')+f+'.wav'); i=int(t*SR); out[i:i+len(a)]+=a*G[f]

w=wave.open(EP+'ep12_voix.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out[:int(TOT*SR)],-1,1)*32767).astype(np.int16).tobytes()); w.close()
print('ok',TOT)
