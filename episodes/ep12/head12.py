# Épisode 1 « Le cadeau » – rendu 1080x1920
import sys, json, wave, math, numpy as np, subprocess
from functools import lru_cache
src=open('/home/claude/w3.py').read().split('\nSC=[')[0]
exec(src)
from PIL import ImageFilter, ImageEnhance
HD='/home/claude/ep12/hd/'; EP='/home/claude/ep12/'; HD11='/home/claude/ep11/hd/'; HD10='/home/claude/ep10/hd/'; HD9='/home/claude/ep9/hd/'; HD8='/home/claude/ep8/hd/'; HD7='/home/claude/ep7/hd/'; HD5='/home/claude/ep5/hd/'; HD6='/home/claude/ep6/hd/'; HD1='/home/claude/ep1/hd/'; HD2='/home/claude/ep2/hd/'; HD3='/home/claude/ep3/hd/'
@lru_cache(None)
def P(k):
    import os
    for d in (HD,HD11,HD10,HD9,HD8,HD7,HD6,HD5,HD3,HD2,HD1):
        if os.path.exists(d+k+'.png'): return Image.open(d+k+'.png').convert('RGBA')
@lru_cache(None)
def PH(k,h):
    im=P(k); return im.resize((max(1,int(im.width*h/im.height)),h),Image.LANCZOS)
@lru_cache(None)
def BGI(k,blur):
    import os; eve=k.endswith('e'); k=k.rstrip('e')
    im=Image.open([d for d in (HD,HD11,HD10,HD9,HD8,HD7,HD6,HD5,HD3,HD2,HD1) if os.path.exists(d+k+'.png')][0]+k+'.png').convert('RGB'); s=max(2000/im.height,(W+80)/im.width)
    if eve:  # ambiance du soir
        a=np.asarray(im).astype(np.float32); a=a*np.array([0.62,0.52,0.62])+np.array([18,6,28]); im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    return im
def bgd(k,t,blur=0,zoom=0.0):
    im=BGI(k,blur); x=int((im.width-W)/2+18*math.sin(t*0.25)); y=40 if im.height<2100 else int((im.height-H)*0.55)
    fr=im.crop((x,y,x+W,y+H))
    if zoom: fr=fr.resize((int(W*(1+zoom)),int(H*(1+zoom))),Image.BILINEAR).crop((int(W*zoom/2),int(H*zoom/2),int(W*zoom/2)+W,int(H*zoom/2)+H))
    return fr
# ---- voix : timeline et enveloppes
L=json.load(open(EP+'dialogue.json'))
def loadw(i):
    w=wave.open(EP+f'vo/L{i:02d}.wav'); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    if w.getnchannels()==2: a=a[::2]
    idx=np.nonzero(np.abs(a)>0.015)[0]; a=a[max(0,idx[0]-300):idx[-1]+1200]; return a,sr
VO=[loadw(i) for i in range(len(L))]
def env_of(a,sr):
    hop=sr//FPS; n=len(a)//hop+1; e=np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)) if i*hop<len(a) else 0 for i in range(n)])
    e=np.convolve(e,[0.25,0.5,0.25],'same'); return np.clip(e/ (np.percentile(e,95)+1e-6),0,1)
ENV=[env_of(a,sr) for a,sr in VO]
DUR=[len(a)/sr for a,sr in VO]
# ---- plans : (nom, durée fixe ou réplique, fonction)
SHAPE={'X':0,'A':0.05,'B':0.35,'C':0.65,'D':1.0,'E':0.55,'F':0.3,'G':0.25,'H':0.45}
import os
RH={}
for _i in range(len(L)):
    _p=EP+f'vo/L{_i:02d}.json'
    if os.path.exists(_p): RH[_i]=json.load(open(_p))['mouthCues']
OFF={}
def talk(li,lt):
    if li is None: return 0
    s=lt-LEAD[li]; k=int(s*FPS); e=ENV[li]; ev=float(e[k]) if 0<=k<len(e) else 0.0
    if li in RH:
        s2=s+OFF.get(li,0)
        for c in RH[li]:
            if c['start']<=s2<c['end']: return SHAPE[c['value']]*(0.55+0.45*ev)
        return 0.0
    return ev
# ---- bouche : position (fraction x,y dans l'image HD) et largeur relative
MOUTH={}
for _p in ('/home/claude/ep1/mouth.json','/home/claude/ep2/mouth.json','/home/claude/ep3/mouth.json','/home/claude/ep5/mouth.json','/home/claude/ep6/mouth.json','/home/claude/ep7/mouth.json','/home/claude/ep8/mouth.json','/home/claude/ep9/mouth.json','/home/claude/ep10/mouth.json','/home/claude/ep11/mouth.json'): MOUTH.update(json.load(open(_p)))
ORIG_OPEN={'K1','B1','K3','B6c','M1','M2','M0','W7','W4','T2'}
def mouthify(im,key,v):
    # 2 images par pose (bouche ouverte / bouche fermée) qui alternent selon la voix
    if v<0.08 or not any(os.path.exists(d+key+'~alt.png') for d in (HD,HD11,HD11,HD10,HD9,HD8,HD7,HD6,HD5,HD2,HD1)): return im
    want_open=v>0.3; is_open=key in ORIG_OPEN
    return im if want_open==is_open else PH(key+'~alt',im.height)

def WET(key,h):
    im=PH(key,h).copy(); w,hh=im.size; import random; R=random.Random(7)
    L=Image.new('RGBA',(w,hh),(0,0,0,0)); d=ImageDraw.Draw(L)
    for i in range(22):
        x=R.randint(int(w*0.25),int(w*0.75)); y=R.randint(0,int(hh*0.25)); ln=R.randint(int(hh*0.08),int(hh*0.4)); ww=R.randint(8,20)
        d.rounded_rectangle([x,y,x+ww,y+ln],radius=ww//2,fill=(170,95,25,150))
        d.ellipse([x-4,y+ln-6,x+ww+4,y+ln+ww+2],fill=(170,95,25,170))
    L=L.filter(ImageFilter.GaussianBlur(2)); a=Image.composite(L.getchannel('A'),Image.new('L',L.size,0),im.getchannel('A').point(lambda p:255 if p>200 else 0))
    L.putalpha(a); im.alpha_composite(L); return im
def actor(fr,key,cx,by,h,A=1.0,v=0.0,t=0,flip=False,rot=0,bobamp=6,wet=False):
    im=WET(key,h) if wet else PH(key,h)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    im=mouthify(im,key+('F' if flip else ''),v) if not flip else im
    sy=1+0.012*v; im2=im.resize((im.width,int(im.height*sy))) if v>0.05 else im
    cy=by-im2.height/2+bobamp*math.sin(t*2.2)
    ps(fr,im2,cx,cy,A,dy=14,op=0.28,rot=rot)
# ---- sous-titres
COL={'BAKARY':(32,72,200),'AWA':(230,120,20),'CLIENTE':(200,80,20),'CLIENTE2':(120,60,170),'MODIBO':(200,40,40),'DJENE':(20,150,150),'TANTIE':(130,30,50),'KARIM':(40,60,120),'SEYDOU':(20,120,60),'MIMI':(200,120,20),'FANTA':(220,90,20),'AWA_P':(150,90,170),'SALI':(30,120,190),'MOUSSA':(90,90,90),'NENE':(200,50,120),'AICHA':(200,160,0),'KADIDIA_P':(200,40,60),'DIASABI':(60,140,60),'FATIM':(200,40,120),'FATIM_P':(200,40,120),'LASSANA':(160,120,40),'BINTOU':(20,130,90),'ASSITAN':(30,60,170),'MOUSSA_P':(90,90,90),'VENDEUSE':(200,30,30),'VOIX_OFF':FONCE}
NOM={'BAKARY':'Bakary','AWA':'Awa','CLIENTE':'La cliente','CLIENTE2':'Une cliente','MODIBO':'Modibo','DJENE':'Djéné','TANTIE':'Tantie Kadi','KARIM':'Karim','SEYDOU':'Seydou','MIMI':'Mimi','FANTA':'Fanta','AWA_P':'Awa · pensée','SALI':'Sali','MOUSSA':'Moussa','NENE':'Nènè','AICHA':'Aïcha','KADIDIA_P':'Kadidia · pensée','DIASABI':'Diasabi','FATIM':'Fatim','FATIM_P':'Fatim · pensée','LASSANA':'Tonton Lassana','BINTOU':'Bintou','ASSITAN':'Tantie Assitan','MOUSSA_P':'Moussa · pensée','VENDEUSE':'La vendeuse de tomates','VOIX_OFF':''}
@lru_cache(None)
def subt(li):
    who,shown=L[li][0],L[li][2]; tt=txt(shown,52,ENCRE,FB,maxw=900)
    p=Image.new('RGBA',(tt.width+70,tt.height+40),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle([0,0,p.width-1,p.height-1],radius=36,fill=(255,255,255,240),outline=COL[who],width=6)
    p.paste(tt,(35,22),tt)
    if NOM[who]:
        tag=pill(NOM[who],38,(255,255,255),COL[who],28,14); q=Image.new('RGBA',(max(p.width,tag.width+40),p.height+tag.height-20),(0,0,0,0))
        q.paste(p,(0,tag.height-20),p); q.paste(tag,(30,0),tag); return q
    return p
def sub(fr,li,lt,y=300):
    if li is None: return
    k=prog(lt,LEAD[li]-0.1,0.25); ps(fr,subt(li),540,y+lerp(-30,0,eo(k)),eo(k),0.9+0.1*back(k),dy=8,op=0.2)
# ---- écran téléphone : fiche robe
def robe_ui(tap):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic)
    d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.rounded_rectangle([30,230,570,700],radius=30,fill=(250,244,228)); r=PH('R1',440); S.paste(r,(300-r.width//2,245),r)
    d.text((30,720),'Robe brodée Tabaski',font=font(FB,40),fill=ENCRE)
    d.rounded_rectangle([30,785,350,840],radius=27,fill=(222,242,200)); check(d,62,812,16,FONCE,5); d.text((90,792),'Vendeur vérifié',font=font(FM,30),fill=FONCE)
    d.text((30,860),'35 000 FCFA',font=font(FB,60),fill=FONCE)
    d.rounded_rectangle([30,955,570,1010],radius=27,fill=(255,236,210)); d.text((300,982),'Paiement à la livraison',font=font(FB,30),fill=(200,100,10),anchor='mm')
    bc=tuple(int(lerp(a,b,tap)) for a,b in zip(VERT,FONCE)); d.rounded_rectangle([30,1040,570,1150],radius=40,fill=bc)
    d.text((300,1095),'Commander' if tap<1 else 'Commande envoyée',font=font(FB,44 if tap<1 else 36),fill=(255,255,255),anchor='mm')
    return S
@lru_cache(None)
def robe_phone(tapq): return phone_with(robe_ui(tapq/4))
def sweat(fr,x,y,t,A):
    for i in range(3):
        k=((t*1.3+i*0.33)%1); D=Image.new('RGBA',(40,60),(0,0,0,0)); ImageDraw.Draw(D).ellipse([6,16,34,56],fill=(120,190,255,230)); ImageDraw.Draw(D).polygon([(20,0),(8,28),(32,28)],fill=(120,190,255,230))
        put(fr,D,x+i*55-55,y+k*120,A*(1-k))
@lru_cache(None)
def label():
    p=Image.new('RGBA',(620,170),(0,0,0,0)); d=ImageDraw.Draw(p); d.rounded_rectangle([0,0,619,169],radius=26,fill=(255,255,255),outline=ORANGE,width=7)
    d.text((310,58),'Awa Couture',font=font(FB,56),fill=ENCRE,anchor='mm'); d.text((310,122),'Boutique Sounsouni',font=font(FM,38),fill=FONCE,anchor='mm'); return p
def stars(fr,cx,cy,t,A,r=170,n=6):
    for i in range(n):
        a=i*6.283/n+t*1.5; x=cx+r*math.cos(a); y=cy+r*0.6*math.sin(a); s=10+6*math.sin(t*6+i)
        D=Image.new('RGBA',(60,60),(0,0,0,0)); ImageDraw.Draw(D).regular_polygon((30,30,s+8),4,rotation=45,fill=(255,215,80,240)); put(fr,D,x,y,A)
@lru_cache(None)
def heart_img():
    D=Image.new('RGBA',(90,80),(0,0,0,0)); d=ImageDraw.Draw(D); c=(235,60,90,240)
    d.ellipse([4,4,48,48],fill=c); d.ellipse([42,4,86,48],fill=c); d.polygon([(8,34),(82,34),(45,76)],fill=c); return D
def notif_ui():
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic)
    d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.text((30,232),'Ma boutique',font=font(FM,32),fill=(110,130,100)); d.text((30,272),'Awa Couture',font=font(FB,50),fill=ENCRE)
    d.rounded_rectangle([24,370,576,1010],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
    d.text((300,425),'Nouvelle commande !',font=font(FB,44),fill=(200,100,10),anchor='mm')
    r=PH('R1',300); S.paste(r,(300-r.width//2,470),r)
    d.text((300,800),'Robe brodée Tabaski',font=font(FB,36),fill=ENCRE,anchor='mm')
    d.text((300,850),'35 000 FCFA',font=font(FB,42),fill=FONCE,anchor='mm')
    d.rounded_rectangle([90,900,510,975],radius=36,fill=(32,72,200)); d.text((300,938),'Client : Bakary',font=font(FB,36),fill=(255,255,255),anchor='mm')
    d.rounded_rectangle([30,1060,570,1150],radius=40,fill=VERT); d.text((300,1105),'Préparer la commande',font=font(FB,34),fill=(255,255,255),anchor='mm')
    return S
@lru_cache(None)
def notif_phone(): return phone_with(notif_ui())

# ---- éléments dessinés
@lru_cache(None)
def sign():
    p=Image.new('RGBA',(760,230),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([0,0,759,229],radius=24,fill=(120,72,36),outline=(80,45,20),width=8)
    for y in range(30,220,38): d.line([(14,y),(746,y)],fill=(105,62,30),width=3)
    d.text((380,82),'Chez Bakary',font=font(FB,78),fill=(255,236,190),anchor='mm')
    d.text((380,170),'Thé · Café · Petit détail',font=font(FM,40),fill=(255,214,140),anchor='mm'); return p
@lru_cache(None)
def bill():
    p=Image.new('RGBA',(300,150),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([0,0,299,149],radius=10,fill=(110,170,200),outline=(40,90,120),width=5)
    d.ellipse([20,25,120,125],outline=(40,90,120),width=4); d.text((70,75),'F',font=font(FB,50),fill=(40,90,120),anchor='mm')
    d.text((205,62),'1000',font=font(FB,54),fill=(25,60,90),anchor='mm'); d.text((205,112),'FRANCS',font=font(FM,26),fill=(25,60,90),anchor='mm'); return p
def drops(fr,cx,cy,t,A,n=10,spread=160,col=(205,120,30)):
    for i in range(n):
        k=((t*1.6+i/n)%1); x=cx+((i*37)%spread-spread/2); y=cy+k*260
        D=Image.new('RGBA',(44,64),(0,0,0,0)); dd_=ImageDraw.Draw(D); dd_.ellipse([4,18,40,62],fill=col+(235,)); dd_.polygon([(22,0),(6,32),(38,32)],fill=col+(235,)); dd_.ellipse([12,30,22,42],fill=(255,240,200,200))
        put(fr,D,x,y,A*(1-k))
@lru_cache(None)
def stains(w,h):
    p=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(p); import random; R=random.Random(4)
    for i in range(16):
        x=R.randint(0,w); y=R.randint(0,int(h*0.4)); L=R.randint(40,int(h*0.6)); ww=R.randint(10,24)
        d.rounded_rectangle([x,y,x+ww,y+L],radius=ww//2,fill=(160,90,25,150))
    return p.filter(ImageFilter.GaussianBlur(3))
@lru_cache(None)
def mint():
    p=Image.new('RGBA',(170,110),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.ellipse([10,20,160,90],fill=(60,170,60)); d.line([(15,55),(160,55)],fill=(30,110,30),width=5)
    for x in range(40,150,28): d.line([(x,55),(x+18,30)],fill=(30,110,30),width=3); d.line([(x,55),(x+18,80)],fill=(30,110,30),width=3)
    return p.rotate(25,expand=True,resample=Image.BICUBIC)
def splash_fx(fr,x0,y0,t,A):
    for i in range(26):
        a=math.radians(150+((i*53)%70)-35); sp=900+((i*97)%500); k=t
        x=x0+math.cos(a)*sp*k; y=y0-math.sin(a)*sp*k+900*k*k; r=10+(i*7)%18
        D=Image.new('RGBA',(r*2+4,r*2+4),(0,0,0,0)); ImageDraw.Draw(D).ellipse([2,2,r*2+2,r*2+2],fill=(165,95,30,230)); put(fr,D,x,y,A*max(0,1-k*1.1))
def sticker(fr,text,x,y,lt,t0,A,size=86,col=(255,255,255),bgc=(30,30,30)):
    k=prog(lt,t0,0.25)
    if k<=0: return
    s=txt(text,size,col,FB); p=Image.new('RGBA',(s.width+60,s.height+40),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle([0,0,p.width-1,p.height-1],radius=40,fill=bgc+(235,)); p.paste(s,(30,20),s)
    ps(fr,p,x,y,A*eo(k),0.5+0.5*back(k),rot=-8,dy=10)
def phone_screen(kind,step=0):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.text((30,232),'Ma boutique',font=font(FM,32),fill=(110,130,100)); d.text((30,272),'Awa Couture',font=font(FB,50),fill=ENCRE)
    if kind=='track':
        d.text((30,370),'Commande n° 2041',font=font(FB,38),fill=ENCRE); r=PH('R1',190); S.paste(r,(420,330),r)
        st=['Commande confirmée','Livreur en route','Livrée à la cliente']
        for i,s_ in enumerate(st):
            y=560+i*160; done=i<step; cur=(i==step)
            c=FONCE if done else (ORANGE if cur else (200,200,200))
            d.ellipse([40,y-30,100,y+30],fill=c)
            if done: check(d,70,y,16,(255,255,255),6)
            if i<2: d.line([(70,y+32),(70,y+128)],fill=FONCE if i<step-1 or done and i+1<step else (210,210,210),width=8)
            d.text((130,y),s_,font=font(FB if cur or done else FM,38),fill=ENCRE if (done or cur) else (150,150,150),anchor='lm')
        d.rounded_rectangle([30,1050,570,1150],radius=40,fill=(255,236,210)); d.text((300,1100),'Livraison partout au Mali',font=font(FB,32),fill=(200,100,10),anchor='mm')
    elif kind=='neworder':
        d.text((30,230),'Chez Bakary',font=font(FB,46),fill=ENCRE); d.rounded_rectangle([24,300,576,1000],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,360),'Nouvelle commande !',font=font(FB,44),fill=(200,100,10),anchor='mm')
        for i,l in enumerate(['3 thermos de café','3 thermos de thé']): d.text((300,460+i*70),l,font=font(FB,38),fill=ENCRE,anchor='mm')
        for i,l in enumerate(['Client : Karim Konaté','Konaté Import-Export','ACI 2000']): d.text((300,640+i*62),l,font=font(FM,32),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([110,880,490,960],radius=40,fill=FONCE); d.text((300,920),'Accepter',font=font(FB,38),fill=(255,255,255),anchor='mm')
    elif kind=='done':
        d.rounded_rectangle([24,380,576,1000],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.ellipse([230,420,370,560],fill=FONCE); check(d,300,490,34,(255,255,255),12)
        d.text((300,620),'Commande livrée !',font=font(FB,46),fill=FONCE,anchor='mm')
        d.text((300,690),'Robe brodée · 35 000 FCFA',font=font(FM,34),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([60,760,540,840],radius=40,fill=ORANGE); d.text((300,800),'Paiement : vendredi',font=font(FB,38),fill=(255,255,255),anchor='mm')
        d.text((300,900),'Orange Money · Moov · Wave',font=font(FM,30),fill=(90,110,80),anchor='mm')
    elif kind=='paid':
        d.rounded_rectangle([24,380,576,900],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,450),'Paiement reçu !',font=font(FB,50),fill=(200,100,10),anchor='mm')
        d.text((300,560),'+ 35 000 FCFA',font=font(FB,72),fill=FONCE,anchor='mm')
        d.text((300,660),'Orange Money · vendredi',font=font(FM,34),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([60,740,540,830],radius=44,fill=FONCE); d.text((300,785),'Payée mardi et vendredi',font=font(FB,32),fill=(255,255,255),anchor='mm')
    return S
@lru_cache(None)
def PHN(kind,step=0): return phone_with(phone_screen(kind,step))
MED=dict(by=3050,h=2550)   # plan rapproché pour les poses en pied
for _i in range(len(L)):
    _w=wave.open(EP+f'vo/L{_i:02d}.wav'); _sr=_w.getframerate(); _a=np.frombuffer(_w.readframes(_w.getnframes()),np.int16).astype(np.float32)/32768
    _ix=np.nonzero(np.abs(_a)>0.015)[0]; OFF[_i]=max(0,_ix[0]-300)/_sr
