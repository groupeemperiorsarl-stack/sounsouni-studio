import numpy as np, subprocess, soundfile as sf, librosa, math, os
from PIL import Image, ImageFilter, ImageDraw, ImageFont
W,H=1080,1920; FPS=30; SR=24000
D='/home/claude/lp/ep12t/'; HD='/home/claude/ep11/hd/'
FB='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def font(s): return ImageFont.truetype(FB,s)
def bgimg(name,blur=0,zoom=1.12,dark=0.0):
    bg=Image.open(HD+name+'.png').convert('RGB'); s=max(W/bg.width,H/bg.height)*zoom; bg=bg.resize((int(bg.width*s),int(bg.height*s)))
    bg=bg.crop(((bg.width-W)//2,bg.height-H,(bg.width-W)//2+W,bg.height))
    if blur: bg=bg.filter(ImageFilter.GaussianBlur(blur))
    if dark: bg=Image.blend(bg,Image.new('RGB',bg.size,(40,20,60)),dark)
    return bg
BG={'k':bgimg('KIOSK',0),'kb':bgimg('KIOSK',5)}
# personnages : image entière + zone du haut remplacée par les visages animés
CH={'mod':('MD',1.0),'bak':('BRc',0.5),'awa':('A20',0.55)}
CACHE={}
JV='/home/claude/jv/ep/'
from scipy import ndimage
ALPHA={}
def fixA(body):
    a=np.asarray(body.getchannel('A'))>100; p=np.vstack([a,np.ones((1,a.shape[1]),bool)]); f=ndimage.binary_fill_holes(p)[:-1]
    na=np.maximum(np.asarray(body.getchannel('A')),(f*255).astype(np.uint8)); body.putalpha(Image.fromarray(na)); return body
def jvfig(ch,li,k,h):
    key=('jv',li,k,h)
    if key in CACHE: return CACHE[key]
    src,frac=CH[ch]; body=fixA(Image.open(HD+src+'.png').convert('RGBA')); bw,bh=body.size; top=int(bh*frac)
    fs=sorted(os.listdir(JV+f'L{li}')); idx=[int(x[:5]) for x in fs]; j=max([q for q in range(len(idx)) if idx[q]<=k] or [0])
    f=Image.open(JV+f'L{li}/'+fs[j]).convert('RGB').resize((bw,top),Image.LANCZOS)
    a=np.asarray(f).astype(int); key_bg=(np.abs(a-np.array([200,200,200])).sum(2)<30)
    if ch not in ALPHA:
        oa=np.asarray(body.getchannel('A').crop((0,0,bw,top)))>128; ALPHA[ch]=(ndimage.binary_erosion(oa,iterations=3),ndimage.binary_dilation(oa,iterations=int(bw*0.03)))
    inner,rim=ALPHA[ch]
    fill=inner&key_bg
    if fill.any():
        a2=np.asarray(f).copy(); a2[fill]=(a2[fill].astype(int)*0+np.array([238,236,230])).astype(np.uint8); f=Image.fromarray(a2)
    al=inner|(rim&~key_bg); al=ndimage.binary_opening(al,iterations=1)
    alI=Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    fr_=f.convert('RGBA'); fr_.putalpha(alI)
    body2=body.copy(); clear=Image.new('RGBA',(bw,top),(0,0,0,0)); body2.paste(clear,(0,0)); body2.alpha_composite(fr_,(0,0))
    im=body2.resize((int(bw*h/bh),h),Image.LANCZOS)
    if len(CACHE)>40: CACHE.clear()
    CACHE[key]=im; return im
def figure(ch,frame,h):
    key=(ch,frame,h)
    if key in CACHE: return CACHE[key]
    src,frac=CH[ch]; body=Image.open(HD+src+'.png').convert('RGBA'); bw,bh=body.size; top=int(bh*frac)
    if frame:
        f=Image.open(D+f'{ch}/{frame}.png').convert('RGBA').resize((bw,top),Image.LANCZOS); f.putalpha(body.getchannel('A').crop((0,0,bw,top))); body.paste(f,(0,0))
    im=body.resize((int(bw*h/bh),h),Image.LANCZOS)
    if len(CACHE)>80: CACHE.clear()
    CACHE[key]=im; return im
def put(fr,im,cx,by): fr.paste(im,(int(cx-im.width/2),int(by-im.height)),im)
def bubble(fr,who,col,text,a=1.0):
    f=font(46); lines=[]; cur=''
    for w in text.split():
        t=(cur+' '+w).strip()
        if f.getlength(t)>860: lines.append(cur); cur=w
        else: cur=t
    lines.append(cur); h=len(lines)*60+50; L=Image.new('RGBA',(W,h+60),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle([60,40,W-60,40+h],radius=34,fill=(255,255,255,240),outline=col,width=6)
    for i,l in enumerate(lines): d.text((W/2,40+30+i*60+28),l,font=f,fill=(30,30,30),anchor='mm')
    tw=font(34).getlength(who)+40; d.rounded_rectangle([90,10,90+tw,62],radius=26,fill=col); d.text((110,36),who,font=font(34),fill='white',anchor='lm')
    if a<1: L.putalpha(L.getchannel('A').point(lambda p:int(p*a)))
    fr.paste(L,(0,230),L)
def sticker(fr,text,x,y,col,size=90):
    f=font(size); w=f.getlength(text)+60; L=Image.new('RGBA',(int(w),size+50),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle([0,0,w-1,size+49],radius=30,fill=col); d.text((w/2,(size+50)/2),text,font=f,fill='white',anchor='mm'); L=L.rotate(-6,expand=True,resample=Image.BICUBIC); fr.paste(L,(int(x-L.width/2),int(y-L.height/2)),L)
def eo_(x): return 1-(1-x)**3
COL={'Modibo':(200,40,40),'Bakary':(32,72,200),'Awa':(230,120,20)}
# --- répliques : (qui, ch, émotion, texte)
LN=[('Modibo','mod','taquin',"Bakarin ! Alors, cette nuit, tu as bien dormi ? Ou bien tu as rêvé de Fatim ?"),
('Bakary','bak','gene',"Arrête, Van. Ce n'est pas drôle. Awa ne me parle plus."),
('Modibo','mod','taquin',"Envoie-lui un cadeau sur Sounsouni. Ça arrive directement à son atelier."),
('Bakary','bak','idee',"Un cadeau… Hmm… Des fleurs ! Oui, des fleurs !"),
('Awa','awa','froide',"Des fleurs ? Garde-les pour ta Fatim."),
('Bakary','bak','panique',"Awa, attends ! Ce n'est pas ce que tu crois !"),
('Modibo','mod','rire',"Ha ha ha ! Mon frère, tu es vraiment dans le pétrin.")]
AUD=[librosa.load(f'/home/claude/tts/ep12t/L{i}.wav',sr=SR)[0] for i in range(len(LN))]
AUD=[a[np.argmax(np.abs(a)>0.01):len(a)-np.argmax(np.abs(a[::-1])>0.01)] for a in AUD]
# --- plans
SH=[('titre',1.4,None),('l',None,0),('l',None,1),('l',None,2),('l',None,3),('awain',1.6,None),('l',None,4),('l',None,5),('awaout',1.3,None),('l',None,6),('fin',2.2,None)]
if os.environ.get('PART'): SH=SH[:6]+[('fin',2.0,None)]
T=[];t=0
for n,d,li in SH:
    dd=d if d else len(AUD[li])/SR+0.75; T.append((n,t,dd,li)); t+=dd
TOT=t; N=int(TOT*FPS)
voice=np.zeros(int(TOT*SR)+SR)
for n,t0,dd,li in T:
    if li is not None: i=int((t0+0.35)*SR); voice[i:i+len(AUD[li])]+=AUD[li]/np.abs(AUD[li]).max()*0.8
hop=SR//FPS; env=np.array([np.sqrt(np.mean(voice[i*hop:(i+1)*hop]**2)) for i in range(N)]); env=np.convolve(env,[0.25,0.5,0.25],'same'); env=env/(np.percentile(env[env>0.001],90)+1e-6)
def mouth(n):
    e=env[n]
    if e<0.12: return 0
    if e<0.4: return 1
    return 3 if (e>0.75 and (n//4)%2) else 2
def blink(n,period=97): return (n%period) in (0,1,2)
def draw(n):
    tm=n/FPS
    for name,t0,dd,li in T:
        if t0<=tm<t0+dd: break
    lt=tm-t0; A=min(1,lt/0.2,(dd-lt)/0.2)
    if name=='titre':
        fr=BG['kb'].copy(); d=ImageDraw.Draw(fr); d.rounded_rectangle([90,820,990,1040],radius=40,fill=(20,110,60)); d.text((540,900),'Les Plans de Bakary',font=font(78),fill='white',anchor='mm'); d.text((540,985),'Test animation · voix open source',font=font(40),fill=(255,230,150),anchor='mm')
    elif name=='wide':
        fr=BG['k'].copy(); put(fr,figure('bak','gene_0',900),300,1900); put(fr,Image.open(HD+'MBN.png').convert('RGBA').resize((int(1428*760/1475),760)),800,1930)
    elif name=='awain' or name=='awaout':
        fr=BG['k'].copy(); put(fr,figure('bak','panique_0' if name=='awaout' else 'idee_0',900),300,1900)
        k=min(1,lt/(dd-0.2)); key='AWK' if name=='awain' else 'ABK'
        im=Image.open(HD+key+'.png').convert('RGBA'); h=int(1050 if name=='awain' else 1050-400*k); im=im.resize((int(im.width*h/im.height),h)); x=(-150+800*k) if name=='awain' else 700+60*k
        put(fr,im,x,1960 if name=='awain' else 1960-300*k+math.sin(lt*12)*6)
    elif name=='l':
        who,ch,emo,txt=LN[li]; fr=BG['kb'].copy()
        k=max(0,int((lt-0.35)*2))*12
        H_={'mod':1250,'bak':2000,'awa':1900}[ch]; BY={'mod':1980,'bak':2350,'awa':2250}[ch]
        im=jvfig(ch,li,k,H_)
        # corps : respiration + léger balancement qui suit la parole
        e=float(np.mean(env[max(0,n-8):n+1])); breath=1+0.006*math.sin(tm*2*math.pi/3.6)
        ang=0.8*math.sin(tm*1.3)+1.2*e*math.sin(tm*3.1); sc=breath*(1+0.012*eo_(min(1,lt/dd)))
        im2=im.resize((int(im.width*sc),int(im.height*sc)),Image.BILINEAR).rotate(ang,resample=Image.BICUBIC,expand=True,center=(im.width*sc/2,im.height*sc))
        put(fr,im2,540,BY+(im2.height-im.height*sc)/2+3*math.sin(tm*2*math.pi/3.6))
        bubble(fr,who,COL[who],txt,min(1,lt/0.25))
        if emo=='idee' and lt>0.8: sticker(fr,'Idée !',820,760,(240,160,0))
        if emo=='panique': sticker(fr,'!!',830,700,(200,30,30),110)
    else:
        fr=Image.new('RGB',(W,H),(236,247,226)); d=ImageDraw.Draw(fr); ic=Image.open('/home/claude/v2kit/uploads/favicon-512.png').convert('RGBA').resize((280,280)); fr.paste(ic,(400,420),ic)
        d.text((540,800),'Sounsouni',font=font(120),fill=(20,110,60),anchor='mm'); d.text((540,1000),'sounsouni.pro',font=font(90),fill=(20,110,60),anchor='mm'); d.text((540,1110),'À suivre…',font=font(56),fill=(80,80,80),anchor='mm')
    if A<1: fr=Image.blend(Image.new('RGB',(W,H),(0,0,0)),fr,max(0,A))
    return fr
VW=D+('voice_part.wav' if os.environ.get('PART') else 'voice.wav'); sf.write(VW,voice[:int(TOT*SR)],SR)
mus,msr=sf.read('/home/claude/ep11/ep11_music.wav'); mus=mus[:int(TOT*msr)]; sf.write(D+('music_part.wav' if os.environ.get('PART') else 'music.wav'),mus,msr)
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','fast',D+'silent_2fps.mp4'],stdin=subprocess.PIPE)
for n in range(N): ff.stdin.write(draw(n).tobytes())
ff.stdin.close(); ff.wait(); print('ok',round(TOT,1))
