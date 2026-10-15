
# ---- ép.13 « La faute »
def HAS(k): return os.path.exists(HD+k+'.png')
@lru_cache(None)
def FLOWER(r=110):
    p=Image.new('RGBA',(r*2+20,r*2+20),(0,0,0,0)); d=ImageDraw.Draw(p); c=r+10
    for i in range(8):
        a=i/8*6.283; x=c+int(r*0.55*math.cos(a)); y=c+int(r*0.55*math.sin(a)); d.ellipse([x-r*0.42,y-r*0.42,x+r*0.42,y+r*0.42],fill=(236,190,60),outline=(170,120,30),width=max(2,r//25))
    d.ellipse([c-r*0.35,c-r*0.35,c+r*0.35,c+r*0.35],fill=(255,225,120),outline=(170,120,30),width=max(2,r//20))
    for i in range(10): a=i/10*6.283; d.ellipse([c+r*0.2*math.cos(a)-4,c+r*0.2*math.sin(a)-4,c+r*0.2*math.cos(a)+4,c+r*0.2*math.sin(a)+4],fill=(255,250,210))
    return p
@lru_cache(None)
def DRESSF(w=560):
    p=DRESS(False,w).copy(); h=p.height; f=FLOWER(int(w*0.2)); p.alpha_composite(f,(w//2-f.width//2,int(h*0.6)-f.height//2)); return p
@lru_cache(None)
def BATTP(pct):
    p=BATT().copy(); d=ImageDraw.Draw(p); d.rounded_rectangle([90,180,330,250],radius=12,fill=(40,40,40))
    d.text((210,215),f'{pct} %',font=font(FB,46),fill=(255,80,60) if pct<20 else (120,255,140),anchor='mm'); return p
@lru_cache(None)
def phone13(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='search':
        d.rounded_rectangle([24,230,576,310],radius=40,fill=(240,240,240)); d.text((60,270),'fil doré broderie',font=font(FM,34),fill=ENCRE,anchor='lm')
        d.rounded_rectangle([24,350,576,1080],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        for i in range(3): d.ellipse([90+i*150,400,210+i*150,520],fill=(222,178,60),outline=(160,115,30),width=6); d.ellipse([130+i*150,440,170+i*150,480],fill=(250,235,190))
        d.text((300,590),'Fil à broder doré',font=font(FB,42),fill=ENCRE,anchor='mm'); d.text((300,645),'3 bobines',font=font(FM,32),fill=ENCRE,anchor='mm')
        d.text((300,720),'1 500 F',font=font(FB,58),fill=FONCE,anchor='mm'); d.text((300,795),'Mercerie Sogoniko',font=font(FM,32),fill=(110,110,110),anchor='mm')
        d.rounded_rectangle([60,840,540,900],radius=30,fill=(255,236,210)); d.text((300,870),'Livraison express : 20 min',font=font(FB,30),fill=(200,100,10),anchor='mm')
        d.rounded_rectangle([90,940,510,1030],radius=45,fill=FONCE); d.text((300,985),'Commander',font=font(FB,42),fill=(255,255,255),anchor='mm')
    elif kind=='confirm':
        d.rounded_rectangle([24,380,576,960],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.ellipse([230,420,370,560],fill=FONCE); check(d,300,490,34,(255,255,255),12)
        d.text((300,620),'Commande confirmée',font=font(FB,42),fill=FONCE,anchor='mm'); d.text((300,700),'Livreur : Seydou',font=font(FB,38),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([90,770,510,850],radius=40,fill=ORANGE); d.text((300,810),'Arrivée : 20 min',font=font(FB,36),fill=(255,255,255),anchor='mm')
    elif kind=='rate':
        d.rounded_rectangle([24,380,576,960],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.text((300,460),'Commande livrée',font=font(FB,44),fill=FONCE,anchor='mm'); d.text((300,530),'Fil à broder doré',font=font(FM,34),fill=ENCRE,anchor='mm')
        d.text((300,640),'Notez votre livreur',font=font(FB,36),fill=ENCRE,anchor='mm'); starrow(d,300,740,42,5)
    elif kind=='review':
        d.text((30,232),'Awa Couture',font=font(FB,48),fill=ENCRE); d.rounded_rectangle([24,320,576,470],radius=28,fill=(232,246,222)); d.text((300,365),'Commande livrée',font=font(FB,36),fill=FONCE,anchor='mm'); d.text((300,425),'15 tenues de mariage',font=font(FM,32),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([24,500,576,1080],radius=30,fill=(255,243,226),outline=ORANGE,width=6); d.text((300,560),'Votre avis',font=font(FB,40),fill=(200,100,10),anchor='mm'); starrow(d,300,640,40,5)
        tt=txt('« La robe de la mariée est une merveille. Une couturière qui sait réparer ses malheurs. »',34,ENCRE,FM,maxw=480); S.paste(tt,(300-tt.width//2,720),tt)
        d.text((300,1030),'— Tantie Kadi',font=font(FB,32),fill=(130,30,50),anchor='mm')
    return S
@lru_cache(None)
def P13(kind): return phone_with(phone13(kind))
@lru_cache(None)
def CANE():
    p=Image.new('RGBA',(60,520),(0,0,0,0)); d=ImageDraw.Draw(p); d.line([(30,40),(30,515)],fill=(110,70,35),width=16); d.arc([0,0,60,80],180,360,fill=(110,70,35),width=16); return p
@lru_cache(None)
def BULB():
    p=Image.new('RGBA',(160,220),(0,0,0,0)); d=ImageDraw.Draw(p); d.ellipse([10,0,150,140],fill=(255,230,80)); d.rectangle([50,130,110,190],fill=(160,160,170)); d.line([(40,30),(25,10)],fill=(255,255,255),width=8); return p
@lru_cache(None)
def SCISS():
    p=Image.new('RGBA',(220,220),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.line([(110,110),(200,20)],fill=(190,190,200),width=14); d.line([(110,110),(200,200)],fill=(190,190,200),width=14)
    d.ellipse([10,40,90,100],outline=(200,40,40),width=14); d.ellipse([10,120,90,180],outline=(200,40,40),width=14); return p
exec(open('/home/claude/ep13/flower.py').read().split("if __name__")[0])
@lru_cache(None)
def FLW(r): return flower(r)
def kadi(fr,key,cx,by,h,A,v,lt,bob=2):
    k={'kadi':'KADI','kadis':'KADIS','kadib':'KADIB'}[key]
    if not HAS(k) and HAS('KADI'): k='KADI'
    if HAS(k): actor(fr,k,cx,by,h,A,v,lt,bobamp=bob); return True
    return False
def kadi_off(fr,lt,A):  # Tantie Kadi hors champ : sa canne et son ombre
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse([700,1500,1250,2000],fill=(0,0,0,110)); fr.paste(sh.filter(ImageFilter.GaussianBlur(30)),(0,0),sh.filter(ImageFilter.GaussianBlur(30)))
    ps(fr,CANE(),960,1550+6*math.sin(lt*3),A,1.4,rot=-12)
def clockst(fr,lt,A,t,y=960,size=170):
    ps(fr,txt(t,size,(255,255,255)),540,y,A*eo(prog(lt,0.05,0.25)),0.6+0.4*back(prog(lt,0.05,0.3)),dy=12,op=0.5)
def grp_wide(fr,lt,A,awa='AH1',v=0,mimi=True):
    actor(fr,'BRc',240,1880,880,A,0,lt,bobamp=1); actor(fr,'DIW',470,1700,1050,A,0,lt,bobamp=1); actor(fr,'MB',940,1940,700,A,0,lt,bobamp=1)
    actor(fr,awa,700,2000,1000 if awa in('AH1','AH2') else 1100,A,0,lt,bobamp=0)
    if mimi: actor(fr,'MIW',900,1960,950,A,0,lt,bobamp=1)
def awa_walk(fr,x,by,h,lt,A,flip=False,moving=True):
    if HAS('AWW1') and HAS('AWW2'):
        seq=['AWW1','AWW3' if HAS('AWW3') else 'AWW1','AWW2','AWW3' if HAS('AWW3') else 'AWW2']; k=seq[int(lt*5)%4] if moving else ('AWW3' if HAS('AWW3') else 'AWW1')
        actor(fr,k,x,by,h,A,0,lt,flip=flip,bobamp=0,rot=0)
    else: actor(fr,'AWK',x,by-abs(10*math.sin(lt*7.5)) if moving else by,h,A,0,lt,flip=flip,bobamp=0,rot=2*math.sin(lt*7.5) if moving else 0)
def draw(n,lt,dd,li,A):
    v=talk(li,lt)
    if n=='titre':
        fr=bgd(K,lt,blur=6); ps(fr,ICON.resize((220,220),Image.LANCZOS),540,620,A*eo(prog(lt,0,0.4)),0.5+0.5*back(prog(lt,0,0.5)))
        ps(fr,dpanel('Les Plans de Bakary',78),540,880,A*eo(prog(lt,0.2,0.4)),0.6+0.4*back(prog(lt,0.2,0.5))); pp(fr,'Épisode 13 · La faute',lt,0.6,A,1040,50); return fr
    if n=='robe':
        fr=cl(K,lt,0.1); z=1+0.15*eo(prog(lt,0,dd)); ps(fr,PH('ROBEH',int(1500*z)),540,1050,A,1.0,dy=20); greysmoke(fr,540,1150,lt,A,5); return fr
    if n=='grp':
        fr=bgd(K,lt,zoom=0.1); grp_wide(fr,lt,A); sweat(fr,240,1100,lt,A)
        if li is not None:
            kadi(fr,'kadi',560,1980,1000,A,0,lt) or kadi_off(fr,lt,A); sub(fr,li,lt)
        return fr
    if n in('miw','miwyes'):
        fr=cl(K,lt); actor(fr,'MIW',540,2350,1900,A,v,lt,bobamp=3)
        if n=='miwyes': stars(fr,540,700,lt,A,200,7)
        sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.4,8) if li==IX['i02'] else fr
    if n in('ah1','ah2'):
        fr=cl(K,lt); actor(fr,n.upper(),540,2400,2000,A,v if n=='ah1' else 0,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='dic':
        fr=cl(K,lt); actor(fr,'DIC',540,3150,2650,A,v,lt); sub(fr,li,lt); return fr
    if n=='diw':
        fr=cl(K,lt,0.12); actor(fr,'DIW',540,3300,2900,A,v,lt); sub(fr,li,lt); return fr
    if n=='die':
        fr=cl(K,lt); actor(fr,'DIE',540,3150,2650,A,v,lt,bobamp=6); sub(fr,li,lt); return fr
    if n=='mbw':
        fr=cl(K,lt); actor(fr,'MB',540,2100,1300,A,0,lt,bobamp=1); sticker(fr,'chut…',800,620,lt,0.2,A,70,(255,255,255),(60,60,60)); sub(fr,li,lt); return fr
    if n=='md':
        fr=cl(K if li not in(IX['m06'],) else AT,lt); actor(fr,'MD',540,1990,1180,A,v,lt,bobamp=4); sub(fr,li,lt); return fr
    if n=='mr':
        fr=cl(K,lt); actor(fr,'MR',540,2080,1350,A,0,lt,bobamp=10); sub(fr,li,lt); return fr
    if n in('toc','toc2'):
        fr=bgd(K,lt,zoom=0.1); grp_wide(fr,lt,A,'AH2'); kadi_off(fr,lt,A)
        for i in range(3):
            if lt>0.2+i*0.6: sticker(fr,'toc…',[300,560,820][i],[460,520,460][i],lt,0.2+i*0.6,A,80,(255,255,255),(110,70,35))
        return shake(fr,lt,0.2,dd,6 if n=='toc' else 10)
    if n in('a5','a5at'):
        fr=cl(K if n=='a5' else AT,lt); key='A5o' if v>0.15 else 'A5c'; actor(fr,key,540,2050,1650,A,0,lt,bobamp=3); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.4,8)
    if n=='panic':
        fr=bgd(K,lt,zoom=0.1); r=12*math.sin(lt*14); actor(fr,'MIW',540,1980,1250,A,0,lt,rot=r,bobamp=10); ps(fr,PH('ROBEH',700),540,1450,A,1.0,rot=-r)
        sweat(fr,540,700,lt,A); sticker(fr,'Où ? Où ?',540,480,lt,0.2,A,90,(255,255,255),(200,30,30)); return fr
    if n in('kadi','kadis','kadib'):
        fr=cl(K,lt)
        if not kadi(fr,n,540,2250 if n!='kadib' else 2100,1850 if n!='kadib' else 1500,A,v,lt):
            actor(fr,'BRc' if n=='kadib' else 'AH1',540,2050,1600,A,0,lt,bobamp=0); kadi_off(fr,lt,A)
        if li in(IX['k16'],): stars(fr,540,600,lt,A,180,5)
        sub(fr,li,lt); return fr
    if n=='sweatA':
        fr=cl(K,lt,0.1); actor(fr,'AH1',540,2500,2200,A,0,lt,bobamp=0); D_=Image.new('RGBA',(90,130),(0,0,0,0)); ImageDraw.Draw(D_).ellipse([5,35,85,125],fill=(140,200,255,235)); ImageDraw.Draw(D_).polygon([(45,0),(10,70),(80,70)],fill=(140,200,255,235))
        ps(fr,D_,760,lerp(560,760,eo(prog(lt,0.3,1.4))),A,1.0); return fr
    if n=='give':
        fr=cl(K,lt,0.1); k=eo(prog(lt,0,0.8)); ps(fr,PH('ROBEH',int(lerp(600,1550,k))),540,lerp(1500,1050,k),A,1.0,dy=20)
        if lt>0.9: fr=shake(fr,lt,0.9,0.5,12)
        return fr
    if n=='bstep':
        fr=cl(K,lt); k=eo(prog(lt,0,0.6)); actor(fr,'BJ',540,int(lerp(2900,3050,k)),int(lerp(2300,2550,k)),A,v,lt,bobamp=2); sub(fr,li,lt); return fr
    if n in('bj','bjsad'):
        fr=cl(K,lt); actor(fr,'BJ',540,3050,2550,A,v,lt,bobamp=2)
        sub(fr,li,lt); return fr
    if n=='shockA':
        fr=cl(K,lt,0.1); actor(fr,'A14',540,2050,1600,A,0,lt,bobamp=0); sticker(fr,'!!!',540,380,lt,0.0,A,130,(255,255,255),(200,30,30)); return shake(fr,lt,0,0.4,10)
    if n=='mute':
        fr=cl(K,lt,0.1); actor(fr,'MUTE',540+int(6*math.sin(lt*16)),2420,2000,A,0,lt,bobamp=4)
        sticker(fr,'Mmmh !',820,520,lt,0.1,A,90,(255,255,255),(60,140,60)); sub(fr,li,lt); return shake(fr,lt,0,dd,4)
    if n=='a20':
        fr=cl(K,lt); actor(fr,'A20',540,2400,2100,A,v,lt,bobamp=0); sub(fr,li,lt); return fr
    if n in('ba','brh'):
        fr=cl(K,lt); actor(fr,'BA' if n=='ba' else 'BR',540,2350,2000,A,v,lt,bobamp=3)
        if n=='brh': big_hearts(fr,lt,0.0,A*0.9)
        sub(fr,li,lt); return fr
    if n in('c60','c52','c31'):
        fr=night(bgd(K if n!='c52' else AT,lt,blur=8),0.3); clockst(fr,lt,A,{'c60':'60:00','c52':'52:00','c31':'31:00'}[n]); return fr
    if n=='atel':
        fr=bgd(AT,lt,zoom=0.08); card(fr,'Atelier Awa Couture',lt,A); actor(fr,'MIM',380,1900,950,A,0,lt,bobamp=1); ps(fr,BATTP(64),160,1700,A,0.5); actor(fr,'AW',830,1960,1150,A,0,lt,bobamp=2); return fr
    if n in('aw','awbulb'):
        fr=cl(AT,lt); actor(fr,'AW',540,2700,2300,A,v,lt,bobamp=3)
        if n=='awbulb': ps(fr,BULB(),820,520,A*eo(prog(lt,0.1,0.3)),1.0+0.05*math.sin(lt*8))
        sub(fr,li,lt); return fr
    if n=='mim':
        fr=cl(AT,lt); actor(fr,'MIM',460,2350,1700,A,v,lt,bobamp=2)
        if li==IX['i06']: fr=shake(fr,lt,LEAD[li],0.4,8)
        sub(fr,li,lt); return fr
    if n in('app1','app2','app3','app4'):
        fr=bgd(AT if n!='app4' else K,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P13({'app1':'search','app2':'confirm','app3':'rate','app4':'review'}[n]),540,lerp(1300,1100,k),A,1.15,dy=30)
        if n=='app1' and lt>2.0: sticker(fr,'Commander',540,1800,lt,2.0,A,70,(255,255,255),FONCE)
        return fr
    if n=='af7':
        fr=cl(AT,lt); actor(fr,'AF7',540,2600,2300,A,v,lt,bobamp=2); sub(fr,li,lt); return fr
    if n=='cutp':
        fr=cl(AT,lt,0.1); actor(fr,'AW',540,2700,2300,A,0,lt,bobamp=2); ps(fr,SCISS(),760,1400,A,1.2,rot=25*math.sin(lt*16))
        for i in range(4):
            if lt>0.3+i*0.45: ps(fr,FLOWER(40),300+i*120,1650+20*math.sin(i),A,1.0)
        sticker(fr,'tchak tchak !',540,480,lt,0.2,A,80,(255,255,255),(200,40,40)); return fr
    if n=='pour':
        fr=cl(K,lt); actor(fr,'BV1',540,2400,2000,A,0,lt,bobamp=2); kadi(fr,'kadib',900,2050,900,A,0,lt,0); return fr
    if n=='sip':
        fr=cl(K,lt)
        if not kadi(fr,'kadib',540,2100,1500,A,0,lt,0): actor(fr,'BRc',540,2050,1600,A,0,lt,bobamp=0); kadi_off(fr,lt,A)
        sticker(fr,'slurp…',780,600,lt,0.3,A,70,(255,255,255),(110,70,35)); return fr
    if n=='freeze':
        fr=cl(K,lt,0.1); actor(fr,'BRc',540,2350,2000,A,0,lt,bobamp=0); sticker(fr,'?!',800,560,lt,0.1,A,100,(255,255,255),(40,40,40)); return fr
    if n=='cough':
        fr=cl(K,lt); actor(fr,'BP',540,3050,2550,A,v,lt,bobamp=8); drops(fr,560,700,lt,A,12,300,(190,120,40)); sweat(fr,760,520,lt,A); sub(fr,li,lt); return shake(fr,lt,LEAD[li],1.0,10)
    if n=='whistle':
        fr=cl(K,lt); actor(fr,'MD',540,1990,1180,A,0,lt,bobamp=6,rot=4*math.sin(lt*3)); sticker(fr,'♪ fiou fiou ♪'.replace('♪','~'),540,480,lt,0.2,A,80,(255,255,255),(60,120,200)); return fr
    if n=='ksmile':
        fr=cl(K,lt)
        if not kadi(fr,'kadib',540,2100,1500,A,0,lt,0): actor(fr,'BRc',540,2050,1600,A,0,lt,bobamp=0); kadi_off(fr,lt,A)
        sticker(fr,':)',780,620,lt,0.4,A,90,(255,255,255),(130,30,50)); return fr
    if n=='beep':
        fr=cl(AT,lt); actor(fr,'MIM',460,2350,1700,A,0,lt,bobamp=2); sticker(fr,'bip… bip…',540,480,lt,0.1,A,80,(255,255,255),(200,30,30)); return fr
    if n=='batt':
        fr=cl(AT,lt,0.1); ps(fr,BATTP(10),540,1100,A,2.0,dy=20)
        if int(lt*4)%2: sticker(fr,'10 %',540,560,lt,0.0,A,110,(255,255,255),(200,30,30))
        return shake(fr,lt,0,dd,3)
    if n=='mirun':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'MB',900,1940,720,A,0,lt,bobamp=1); k=eo(prog(lt,0,1.6)); actor(fr,'MIW',lerp(-150,620,k),1960,1000,A,0,lt*3,bobamp=12 if k<1 else 2)
        if k<1: speed(fr,1300,1800,lt,A)
        sticker(fr,'Modibooo !',540,480,lt,0.4,A,80,(255,255,255),(200,120,20)); return fr
    if n=='mik':
        fr=cl(K,lt); actor(fr,'MI',1080-int(1900*520/1517)//2,2350,1900,A,v,lt,bobamp=6); sweat(fr,700,560,lt,A); sub(fr,li,lt); return fr
    if n=='mrun':
        fr=cl(K,lt); actor(fr,'MRUN',540,1990,1100,A,0,lt,bobamp=12); speed(fr,1300,1800,lt,A); sub(fr,li,lt); return fr
    if n=='moto':
        fr=bgd(AT,lt,zoom=0.08); k=eo(prog(lt,0,1.2)); actor(fr,'SEY',lerp(1300,700,k),1960,1150,A,0,lt,bobamp=6 if k<1 else 1); speed(fr,1300,1800,lt,A) if k<1 else None
        sticker(fr,'Pouet pouet !',400,520,lt,0.0,A,80,(255,255,255),(30,120,60)); return fr
    if n=='sey':
        fr=cl(AT,lt); actor(fr,'SEY',540,2350,1900,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='plug':
        fr=cl(AT,lt,0.1); ps(fr,BATTP(100),540,1100,A,2.0,dy=20); sticker(fr,'clic !',780,600,lt,0.2,A,90,(255,255,255),(40,40,40)); return fr
    if n=='montage':
        fr=cl(AT,lt,0.1); ps(fr,PH('ROBEF' if lt>3.2 else 'ROBEH',1500),540,1100,A,1.0,dy=20); k=prog(lt,0.3,2.9)
        if 0<k and lt<=3.2: f=FLW(int(20+130*k)//10*10); ps(fr,f,474,1275,A,1.0)
        nx=540+80*math.sin(lt*9); ny=1250+60*math.cos(lt*9); D_=Image.new('RGBA',(20,200),(0,0,0,0)); ImageDraw.Draw(D_).line([(10,0),(10,200)],fill=(230,190,60),width=6); ps(fr,D_,nx,ny-150,A,1.0,rot=20)
        t=['20:00','10:00','02:00'][min(2,int(lt/1.5))]; ps(fr,txt(t,130,(255,255,255)),540,380,A,1.0,dy=10,op=0.6); return fr
    if n=='door':
        fr=bgd(AT,lt,zoom=0.06); actor(fr,'A21',540,2000,1550,A,0,lt,bobamp=0); return fr
    if n=='reveal':
        fr=cl(K,lt,0.1); z=1+0.1*eo(prog(lt,0,dd)); ps(fr,PH('ROBEF',int(1550*z)),540,1050,A,1.0,dy=20); stars(fr,500,1150,lt,A,260,8); sparkle(fr,500,1150,lt,A); return fr
    if n=='blush':
        fr=cl(K,lt); actor(fr,'BJ',540,3050,2550,A,0,lt,bobamp=0); redface(fr,560,560,lt,A); return fr
    if n=='leave':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',260,1900,940,A,0,lt,bobamp=0); actor(fr,'DIW',600,1700,1050,A,0,lt,bobamp=1); actor(fr,'MB',920,1940,700,A,0,lt,bobamp=1)
        for i in range(3):
            if lt>0.2+i*0.7: sticker(fr,'toc…',[800,600,400][i],[500,460,420][i],lt,0.2+i*0.7,A*0.8,70,(255,255,255),(110,70,35))
        return fr
    if n=='awalk':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',290,1900,940,A,0,lt,bobamp=0); k=prog(lt,0,dd*0.85); awa_walk(fr,lerp(1200,640,k),1960,1050,lt,A,flip=True,moving=k<1); return fr
    if n=='abk':
        fr=cl(K,lt); actor(fr,'ABK',540,2350,1900,A,0,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='abk2':
        fr=cl(K,lt); k=prog(lt,0,0.9); key=['AWB1','AWB3','AWB2','AWB3'][int(lt*5)%4] if k<1 else 'AWB3'
        actor(fr,key,lerp(500,600,eo(k)),int(lerp(2350,2250,eo(k))),int(lerp(1900,1750,eo(k))),A,0,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='grin':
        fr=cl(K,lt,0.1); actor(fr,'BR',540,2500,2200,A,0,lt,bobamp=4); big_hearts(fr,lt,0.0,A); return fr
    if n=='heels':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',290,1900,940,A,0,lt,bobamp=0); actor(fr,'MB',920,1940,700,A,0,lt,bobamp=0); sticker(fr,'tac tac tac',540,480,lt,0.1,A,80,(255,255,255),(200,40,120)); return fr
    if n in('ft2','ft4'):
        fr=cl(K,lt); k=eo(prog(lt,0,0.8)) if n=='ft2' else 1; actor(fr,n.upper(),lerp(900,540,k),2350,1900,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='stop':
        fr=bgd(AT,lt,zoom=0.06); actor(fr,'A21c',540,2000,1550,A,0,lt,bobamp=0)
        if 0.3<lt<0.5: fr=Image.blend(fr.convert('RGB'),Image.new('RGB',fr.size,(255,255,255)),0.6)
        return shake(fr,lt,0.3,0.6,12)
    if n=='look':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'FT2',820,1960,1050,A,0,lt,bobamp=1); actor(fr,'BPc',480,1950,1050,A,0,lt,bobamp=0); actor(fr,'A20',150,1990,1050,A,0,lt,bobamp=0); sweat(fr,480,1050,lt,A)
        sticker(fr,'!!',480,600,lt,0.5,A,110,(255,255,255),(200,30,30)); return shake(fr,lt,0,dd,5)
    if n=='facepalm':
        fr=cl(K,lt); actor(fr,'MS',540,2050,1250,A,0,lt,bobamp=2); sticker(fr,'Paf !',800,560,lt,0.3,A,90,(255,255,255),(40,40,40)); return fr
    if n=='suite':
        fr=night(bgd(K,lt,blur=10),0.55); ps(fr,txt('À suivre…',130,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.5)),1.0,dy=10,op=0.5); return fr
    if n in('finb','finc','fin2'):
        fr=bg(lt); fin11(fr,lt,A,{'finb':1,'finc':2,'fin2':3}[n]); return fr
