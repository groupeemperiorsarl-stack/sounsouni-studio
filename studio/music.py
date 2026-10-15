"""Musique de fond générée (balafon, basse, percussions), à la durée exacte de l'épisode."""
def make(DUR, OUTP, seed=3):
    import numpy as np, wave
    SR=44100; BPM=112; B=60/BPM; BAR=4*B
    n=int(SR*DUR); out=np.zeros(n); rng=np.random.default_rng(seed)
    def add(sig,t,g=1.0):
        i=int(t*SR); j=min(n,i+len(sig)); 
        if i<n: out[i:j]+=g*sig[:j-i]
    def env(d,k): tt=np.arange(int(SR*d))/SR; return tt,np.exp(-tt*k)
    def mf(m): return 440*2**((m-69)/12)
    def kick():
        tt,e=env(0.35,12); f=50+70*np.exp(-tt*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*e
    def noise(d,k,hp=True):
        tt,e=env(d,k); s=rng.standard_normal(len(tt))
        if hp: s=np.diff(s,prepend=0); s=np.diff(s,prepend=0)
        return s*e
    def bala(m,d=0.6):
        tt,e=env(d,9); f=mf(m)
        return (np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*f*3.9*tt)*np.exp(-tt*25)+0.1*np.sin(2*np.pi*f*9.8*tt)*np.exp(-tt*40))*e*(1-np.exp(-tt*400))
    def bass(m,d):
        tt,e=env(d,3.5); f=mf(m); return (np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*e*(1-np.exp(-tt*200))
    def pad(ms,d):
        tt=np.arange(int(SR*d))/SR; a=np.minimum(1,tt/0.3)*np.minimum(1,(d-tt)/0.4)
        return sum(np.sin(2*np.pi*mf(m)*tt+np.sin(2*np.pi*0.3*tt))*0.25 for m in ms)*a
    CH=[(45,[57,60,64]),(41,[53,57,60]),(48,[55,60,64]),(43,[55,59,62])]
    PA=[(0,76),(3,74),(6,72),(8,69),(10,72),(12,74),(14,76)]
    PB=[(0,79),(2,76),(4,74),(6,76),(8,72),(11,69),(14,72)]
    s16=B/4; bars=int(DUR/BAR)+1
    for b in range(bars):
        t0=b*BAR; root,ch=CH[b%4]; full=b>=2; last=t0+BAR>DUR-1.5
        for k,m in enumerate([ch[0],ch[2],ch[1],ch[2],ch[0]]):
            add(bala(m-12+12,0.4),t0+[0,3,6,10,12][k]*s16,0.18)
        if b>=1:
            for st,m in (PA if (b//2)%2==0 else PB): add(bala(m),t0+st*s16,0.32)
        if full and not last:
            for bt in (0,2): add(kick(),t0+bt*B,0.9)
            add(kick(),t0+3.5*B,0.5)
            for bt in (1,3): add(noise(0.18,30),t0+bt*B,0.10)
            for i in range(16): add(noise(0.05,90),t0+i*s16,0.025 if i%2 else 0.045)
            for st,d in [(0,0.5),(3,0.3),(6,0.5),(10,0.3),(12,0.4)]: add(bass(root+(12 if st==10 else 0),d),t0+st*s16,0.45)
        add(pad(ch,BAR),t0,0.12)
    add(bala(81,2.0),DUR-1.6,0.35); add(pad([57,60,64,69],1.6),DUR-1.6,0.2)
    tt=np.arange(n)/SR; out*=np.minimum(1,(DUR-tt)/1.2).clip(0,1)
    out=np.tanh(out/np.abs(out).max()*1.6)*0.85
    st=np.stack([out,np.roll(out,int(0.012*SR))*0.9],1)
    w=wave.open(OUTP,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
