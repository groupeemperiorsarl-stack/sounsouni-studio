@lru_cache(None)
def heart_img():
    D=Image.new('RGBA',(90,80),(0,0,0,0)); d=ImageDraw.Draw(D); c=(235,60,90,240)
    d.ellipse([4,4,48,48],fill=c); d.ellipse([42,4,86,48],fill=c); d.polygon([(8,34),(82,34),(45,76)],fill=c); return D
def frame_at(Tm):
    for i,(n,t0,dd,li) in enumerate(T):
        if t0<=Tm<t0+dd or i==len(T)-1:
            lt=Tm-t0; A=min(1,lt/0.18,(dd-lt)/0.18) if 0<i<len(T)-1 else (min(1,(dd-lt)/0.18) if i==0 else min(1,lt/0.18))
            return draw(n,lt,dd,li,max(0.0,A))
if __name__=='__main__':
    if sys.argv[1]=='timeline':
        sfx=[]
        for n,t0,dd,li in T:
            for o,f in SFX.get(n,[]):
                tt=t0+dd+float(o[3:]) if isinstance(o,str) else t0+o; sfx.append((round(tt,3),f))
        json.dump({'lines':[(n,round(t0+LEAD[li],3),li) for n,t0,dd,li in T if li is not None],'sfx':sfx,'TOT':TOT},open(EP+'timeline.json','w')); print('TOT',round(TOT,2)); sys.exit()
    if sys.argv[1]=='preview':
        for s in sys.argv[2:]: frame_at(float(s)).save(EP+f'pv_{s}.png')
        sys.exit()
    N=int(TOT*FPS); A0,A1=0,N
    if sys.argv[1]=='seg': A0,A1=int(sys.argv[2]),min(N,int(sys.argv[3])); sys.argv[1]=sys.argv[4]
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','medium','-tune','animation',sys.argv[1]],stdin=subprocess.PIPE)
    for n in range(A0,A1):
        ff.stdin.write(frame_at(n/FPS).convert('RGB').tobytes())
        if n%150==0: print(n,N,flush=True)
        if n%600==599:
            for _f in (PH,BGI): _f.cache_clear()
    ff.stdin.close(); ff.wait(); print('ok',TOT,N)
