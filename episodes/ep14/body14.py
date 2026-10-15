
# ---- ép.14 « Retour à l'expéditeur »
def HAS(k): return os.path.exists(HD+k+'.png') or os.path.exists(HD13+k+'.png')
@lru_cache(None)
def PASTRY(i,r=34):
    cols=[(240,120,150),(250,220,120),(140,90,60),(250,250,240),(170,220,120),(250,170,80)]
    p=Image.new('RGBA',(r*2+10,r*2+10),(0,0,0,0)); d=ImageDraw.Draw(p); c=cols[i%6]
    d.ellipse([5,r//2+5,r*2+5,r*2+5],fill=(200,150,80)); d.ellipse([5,5,r*2+5,r*2-5],fill=c)
    d.ellipse([r-6,r//2-4,r+10,r//2+12],fill=(220,40,60) if i%2 else (255,255,255)); return p
@lru_cache(None)
def BOXP(n,w=760):
    h=int(w*0.62); p=Image.new('RGBA',(w,h+120),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.polygon([(30,120),(w-30,120),(w-60,h+110),(60,h+110)],fill=(214,170,56)); d.rectangle([40,120,w-40,150],fill=(170,125,35))
    d.polygon([(20,0),(w-20,0),(w-30,120),(30,120)],fill=(236,196,84)); d.text((w//2,60),'Le Palais Doré',font=font(FB,int(w*0.06)),fill=(120,80,20),anchor='mm')
    d.rectangle([w//2-14,120,w//2+14,h+110],fill=(200,30,50)); d.rectangle([60,int(120+h*0.45),w-60,int(120+h*0.45)+28],fill=(200,30,50))
    k=0
    for row in range(4):
        for col in range(6):
            if k<n:
                q=PASTRY(k,int(w*0.045)); p.alpha_composite(q,(int(90+col*(w-180)/6),int(170+row*(h-80)/4))); k+=1
    return p
@lru_cache(None)
def HOVER(w=360):
    p=Image.new('RGBA',(w,int(w*0.3)),(0,0,0,0)); d=ImageDraw.Draw(p); h=p.height
    d.rounded_rectangle([0,h*0.2,w-1,h*0.75],radius=int(h*0.25),fill=(30,30,34)); d.rounded_rectangle([w*0.1,h*0.28,w*0.42,h*0.45],radius=8,fill=(70,70,80)); d.rounded_rectangle([w*0.58,h*0.28,w*0.9,h*0.45],radius=8,fill=(70,70,80))
    for x in (0.12,0.88): d.ellipse([w*x-h*0.3,h*0.4,w*x+h*0.3,h],fill=(15,15,15)); d.ellipse([w*x-h*0.12,h*0.58,w*x+h*0.12,h*0.82],fill=(90,200,255))
    return p
@lru_cache(None)
def CARD():
    p=Image.new('RGBA',(300,190),(0,0,0,0)); d=ImageDraw.Draw(p); d.rounded_rectangle([0,0,299,189],radius=20,fill=(240,120,20)); d.text((150,70),'RECHARGE',font=font(FB,40),fill=(255,255,255),anchor='mm'); d.text((150,130),'1 000 F',font=font(FB,52),fill=(255,255,255),anchor='mm'); return p
@lru_cache(None)
def phone14(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni' if kind not in('ref1','ref2') else 'Sounsouni Livreur',font=font(FB,44 if kind not in('ref1','ref2') else 38),fill=(255,255,255))
    if kind=='search':
        d.rounded_rectangle([24,230,576,310],radius=40,fill=(240,240,240)); d.text((60,270),'pâtisseries',font=font(FM,34),fill=ENCRE,anchor='lm')
        d.rounded_rectangle([24,350,576,1080],radius=30,fill=(255,243,226),outline=ORANGE,width=6); b=BOXP(24,420); S.paste(b,(90,380),b)
        d.text((300,720),'Pâtisserie Le Palais Doré',font=font(FB,36),fill=ENCRE,anchor='mm'); d.text((300,775),'Grand plateau royal',font=font(FM,32),fill=ENCRE,anchor='mm'); d.text((300,820),'24 pâtisseries assorties',font=font(FM,30),fill=(110,110,110),anchor='mm')
        d.text((300,890),'15 000 F',font=font(FB,58),fill=FONCE,anchor='mm'); d.rounded_rectangle([70,950,530,1040],radius=45,fill=FONCE); d.text((300,995),'Ajouter au panier',font=font(FB,38),fill=(255,255,255),anchor='mm')
    elif kind=='cart':
        d.text((30,240),'Panier',font=font(FB,50),fill=ENCRE); d.text((570,240),'15 000 F',font=font(FB,44),fill=FONCE,anchor='ra')
        d.rounded_rectangle([24,320,576,420],radius=24,fill=(232,246,222)); d.rectangle([50,350,90,390],fill=FONCE); check(d,70,370,14,(255,255,255),5); d.text((110,370),'Envoyer en cadeau',font=font(FB,36),fill=ENCRE,anchor='lm')
        d.text((30,460),'Destinataire',font=font(FM,30),fill=(110,110,110)); tt=txt('Kiosque de Bakary, en face de Awa Couture',34,ENCRE,FB,maxw=530); S.paste(tt,(30,500),tt)
        d.text((30,640),'Message pour le destinataire',font=font(FM,30),fill=(110,110,110)); d.rounded_rectangle([24,690,576,900],radius=24,fill=(255,243,226),outline=ORANGE,width=4)
        tt=txt('« Pour la robe. Maintenant, on est quittes. – Awa »',34,ENCRE,FM,maxw=500); S.paste(tt,(300-tt.width//2,730),tt)
        d.rounded_rectangle([90,960,510,1050],radius=45,fill=FONCE); d.text((300,1005),'Commander',font=font(FB,42),fill=(255,255,255),anchor='mm')
    elif kind=='confirm':
        d.rounded_rectangle([24,380,576,960],radius=34,fill=(232,246,222),outline=FONCE,width=6); d.ellipse([230,420,370,560],fill=FONCE); check(d,300,490,34,(255,255,255),12)
        d.text((300,620),'Commande confirmée',font=font(FB,42),fill=FONCE,anchor='mm'); d.text((300,700),'Livreur : Seydou',font=font(FB,38),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([90,770,510,850],radius=40,fill=ORANGE); d.text((300,810),'Arrivée : 25 min',font=font(FB,36),fill=(255,255,255),anchor='mm')
    elif kind=='ref1':
        d.rounded_rectangle([24,400,576,900],radius=34,fill=(255,243,226),outline=ORANGE,width=6); tt=txt('Le destinataire refuse la livraison ?',40,ENCRE,FB,maxw=480); S.paste(tt,(300-tt.width//2,470),tt)
        d.rounded_rectangle([60,700,280,800],radius=45,fill=(220,50,40)); d.text((170,750),'Oui',font=font(FB,44),fill=(255,255,255),anchor='mm'); d.rounded_rectangle([320,700,540,800],radius=45,fill=(200,200,200)); d.text((430,750),'Non',font=font(FB,44),fill=ENCRE,anchor='mm')
    elif kind=='ref2':
        d.text((30,260),'Motif du refus',font=font(FB,42),fill=ENCRE); d.rounded_rectangle([24,330,576,620],radius=24,fill=(245,245,245),outline=(180,180,180),width=4)
        tt=txt('« Ce que j\'ai fait ne se rembourse pas. »',38,ENCRE,FM,maxw=500); S.paste(tt,(300-tt.width//2,380),tt)
        d.rounded_rectangle([40,700,560,810],radius=50,fill=FONCE); tt=txt("Valider le retour à l'expéditeur",32,(255,255,255),FB,maxw=480); S.paste(tt,(300-tt.width//2,755-tt.height//2),tt)
    elif kind=='refused':
        d.rounded_rectangle([24,330,576,1060],radius=34,fill=(255,235,232),outline=(220,50,40),width=6); d.ellipse([230,370,370,510],fill=(220,50,40)); d.line([(270,410),(330,470)],fill=(255,255,255),width=14); d.line([(330,410),(270,470)],fill=(255,255,255),width=14)
        tt=txt('Livraison refusée par le destinataire',40,ENCRE,FB,maxw=500); S.paste(tt,(300-tt.width//2,550),tt)
        tt=txt('Motif : « Ce que j\'ai fait ne se rembourse pas. »',34,ENCRE,FM,maxw=500); S.paste(tt,(300-tt.width//2,700),tt)
        tt=txt("Votre colis revient à l'expéditeur.",32,(200,40,30),FB,maxw=500); S.paste(tt,(300-tt.width//2,900),tt)
    return S
@lru_cache(None)
def P14(kind): return phone_with(phone14(kind))
def bgcar(fr,lt,A,x=990,y=1290,s=0.16):
    c=PH('CAR',int(1665*s)); c2=ImageEnhance.Brightness(c).enhance(0.75); ps(fr,c2,x,y,A*0.95,1.0,dy=6,op=0.15)
def kwide(fr,lt,A,fatim=True,awa=True):
    bgcar(fr,lt,A)
    actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=1); actor(fr,'DIW',450,1700,1050,A,0,lt,bobamp=1); actor(fr,'MB',650,1940,650,A,0,lt,bobamp=1)
    if fatim: actor(fr,'FT1',820,1960,950,A,0,lt,bobamp=1)
    if awa: actor(fr,'A21',1000,1700,620,A,0,lt,bobamp=0)
def catch_pose(fr,lt,A,cx=540,by=2300,h=1900):
    if HAS('CATCH'): actor(fr,'CATCH',cx,by,h,A,0,lt,bobamp=0); return
    actor(fr,'BH',cx-260,by,int(h*1.05),A,0,lt,bobamp=0)
    im=PH('A14',int(h*0.62)).rotate(28,expand=True,resample=Image.BICUBIC); ps(fr,im,cx+190,by-int(h*0.55),A,1.0,dy=10,op=0.2)
def draw_v1(n,lt,dd,li,A):
    v=talk(li,lt)
    if n=='titre':
        fr=bgd(K,lt,blur=6); ps(fr,ICON.resize((220,220),Image.LANCZOS),540,620,A*eo(prog(lt,0,0.4)),0.5+0.5*back(prog(lt,0,0.5)))
        ps(fr,dpanel('Les Plans de Bakary',78),540,880,A*eo(prog(lt,0.2,0.4)),0.6+0.4*back(prog(lt,0.2,0.5))); pp(fr,"Épisode 14 · Retour à l'expéditeur",lt,0.6,A,1040,46); return fr
    if n=='open':
        fr=bgd(K,lt,zoom=0.1); kwide(fr,lt,A); return fr
    if n=='dic':
        fr=cl(K,lt); actor(fr,'DIC',540,3150,2650,A,v,lt); sub(fr,li,lt); return fr
    if n=='diw':
        fr=cl(K,lt,0.12); actor(fr,'DIW',540,3300,2900,A,v,lt); sub(fr,li,lt); return fr
    if n=='die':
        fr=cl(K,lt); actor(fr,'DIE',540,3150,2650,A,v,lt,bobamp=6); sub(fr,li,lt); return fr
    if n=='facepalm':
        fr=cl(K,lt); actor(fr,'MS',540,2050,1250,A,0,lt,bobamp=2); sticker(fr,'Paf !',800,560,lt,0.3,A,90,(255,255,255),(40,40,40)); return fr
    if n in('ft1','ft2','ft3','ft4'):
        fr=cl(K,lt); key=n.upper()
        if n=='ft3' and HAS('FLAUGH'): key='FLAUGH'
        actor(fr,key,540,2350,1900,A,v,lt,bobamp=3)
        if n=='ft3' and key=='FT3': ps(fr,CARD(),300,1350,A*eo(prog(lt,0.6,0.4)),0.8,rot=-12)
        sub(fr,li,lt); return fr
    if n=='laughF':
        fr=cl(K,lt); actor(fr,'FLAUGH' if HAS('FLAUGH') else 'FT2',540,2350,1900,A,0,lt,bobamp=10); sticker(fr,'Ha ha ha !',540,480,lt,0.1,A,90,(255,255,255),(200,40,120)); return fr
    if n=='bp':
        fr=cl(K,lt); actor(fr,'BP',540,3050,2550,A,v,lt,bobamp=4); sweat(fr,740,520,lt,A); sub(fr,li,lt); return fr
    if n=='bq':
        fr=cl(K,lt); actor(fr,'BS7',540,2600,2200,A,0,lt,bobamp=2); sticker(fr,'?!',800,560,lt,0.1,A,110,(255,255,255),(40,40,40)); return fr
    if n in('bj',):
        fr=cl(K,lt); actor(fr,'BJ',540,3050,2550,A,v,lt,bobamp=2); sub(fr,li,lt); return fr
    if n=='awaeyes':
        z=1+0.3*eo(prog(lt,0,dd)); fr=bgd(AT,lt,zoom=0.06); actor(fr,'A20',540,int(2400+(z-1)*1500),int(2100*z),A,0,lt,bobamp=0)
        sticker(fr,'⚡'.replace('⚡','!!'),820,560,lt,0.3,A,100,(255,255,255),(240,180,0)); return fr
    if n in('a20','a20at'):
        fr=cl(K if n=='a20' else AT,lt); actor(fr,'A20',540,2400,2100,A,v,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='shakeA':
        fr=cl(K,lt,0.15); actor(fr,'A20',540,2600,2400,A,0,lt,bobamp=0); return shake(fr,lt,0,dd,8)
    if n=='fleave':
        fr=bgd(K,lt,zoom=0.1); bgcar(fr,lt,A); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=1); k=eo(prog(lt,0,dd)); actor(fr,'FT2',lerp(700,1250,k),1960,950,A,0,lt*3,bobamp=10)
        sticker(fr,'Rappelle-moi !',540,480,lt,0.2,A,70,(255,255,255),(200,40,120)); return fr
    if n in('slam','slam2'):
        fr=bgd(K if n=='slam' else AT,lt,zoom=0.1)
        if n=='slam': kwide(fr,lt,A,fatim=False,awa=False)
        sticker(fr,'BAM !',540,500,lt,0.1,A,130,(255,255,255),(200,30,30)); return shake(fr,lt,0.1,0.8,18)
    if n=='md':
        fr=cl(K,lt); actor(fr,'MD',540,1990,1180,A,v,lt,bobamp=4); sub(fr,li,lt); return fr
    if n=='mshout':
        fr=cl(K,lt); actor(fr,'MD',540,1990,1180,A,v,lt,bobamp=8); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.5,10)
    if n=='atel':
        fr=bgd(AT,lt,zoom=0.08); card(fr,'Atelier Awa Couture',lt,A); actor(fr,'MIM',380,1900,950,A,0,lt,bobamp=1); awa_walk(fr,lerp(900,700,prog(lt,0,dd)),1960,1100,lt,A,flip=True); return fr
    if n in('a5','a5at'):
        fr=cl(K if n=='a5' else AT,lt); key='A5o' if v>0.15 else 'A5c'; actor(fr,key,540,2050,1650,A,0,lt,bobamp=3); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.4,8)
    if n=='mim':
        fr=cl(AT,lt); actor(fr,'MIM',460,2350,1700,A,v,lt,bobamp=2)
        if li==IX['i04']: fr=shake(fr,lt,LEAD[li],0.4,8)
        sub(fr,li,lt); return fr
    if n=='aw':
        fr=cl(AT,lt); actor(fr,'AW',540,2700,2300,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='af7':
        fr=cl(AT,lt); actor(fr,'AF7',540,2600,2300,A,v,lt,bobamp=2); sub(fr,li,lt); return fr
    if n in('app1','app2','app3','app4','app5','app6'):
        bgk=AT if n in('app1','app2','app3','app6') else K
        fr=bgd(bgk,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P14({'app1':'search','app2':'cart','app3':'confirm','app4':'ref1','app5':'ref2','app6':'refused'}[n]),540,lerp(1300,1100,k),A,1.15,dy=30)
        if n=='app4' and lt>1.4: sticker(fr,'Oui',380,1500,lt,1.4,A,70,(255,255,255),(220,50,40))
        if n=='app2' and lt>2.2: sticker(fr,'Commander',540,1800,lt,2.2,A,70,(255,255,255),FONCE)
        return fr
    if n=='glare':
        z=1+0.3*eo(prog(lt,0,dd)); fr=cl(AT,lt); actor(fr,'A20',540,int(2400+(z-1)*1500),int(2100*z),A,0,lt,bobamp=0); return fr
    if n=='bonk':
        fr=cl(K,lt); actor(fr,'DSG',540,2300,1700,A,0,lt,bobamp=3); grillfx(fr,520,1700,lt,A*0.8)
        if lt>0.3: stars(fr,560,560,lt,A,140,6); sticker(fr,'BONG !',540,400,lt,0.3,A,120,(255,255,255),(200,30,30))
        return shake(fr,lt,0.3,0.5,14)
    if n=='moto':
        fr=bgd(K,lt,zoom=0.08); k=eo(prog(lt,0,1.2)); actor(fr,'SEY',lerp(1300,700,k),1960,1150,A,0,lt,bobamp=6 if k<1 else 1)
        if k<1: speed(fr,1300,1800,lt,A)
        ps(fr,BOXP(24,300),lerp(1100,500,k),1450,A,1.0); sticker(fr,'Pouet pouet !',400,520,lt,0.0,A,80,(255,255,255),(30,120,60)); return fr
    if n in('sey','seyin'):
        fr=cl(AT if li in(IX['s06'],IX['s07']) or n=='seyin' else K,lt); actor(fr,'SEY',540,2350,1900,A,v,lt,bobamp=3)
        if n=='seyin': sticker(fr,'Pouet pouet !',540,480,lt,0.0,A,80,(255,255,255),(30,120,60))
        if li is not None: sub(fr,li,lt)
        return fr
    if n in('ba','brh','note'):
        fr=cl(K,lt); key={'ba':'BA','brh':'BR','note':'BC7'}[n]; actor(fr,key,540,2350 if key!='BC7' else 2300,2000 if key!='BC7' else 1700,A,v,lt,bobamp=3)
        if n=='brh': big_hearts(fr,lt,0.0,A*0.9)
        sub(fr,li,lt); return fr
    if n=='boxopen':
        fr=cl(K,lt,0.1); ps(fr,BOXP(24,800),540,1150,A,1.0+0.04*eo(prog(lt,0,dd)),dy=20); stars(fr,540,1100,lt,A,320,8); sparkle(fr,540,1100,lt,A); return fr
    if n=='bbox':
        fr=cl(K,lt)
        if HAS('BBOX'): actor(fr,'BBOX',540,2400,2050,A,0,lt,bobamp=2)
        else: actor(fr,'BR',540,2350,2000,A,0,lt,bobamp=2); ps(fr,BOXP(24,620),540,1500,A,1.0,dy=14)
        sparkle(fr,540,1350,lt,A); sub(fr,li,lt); return fr
    if n in('dsf','eat','eat2'):
        fr=cl(K,lt); key='DEAT' if HAS('DEAT') else 'DSF'; actor(fr,key,540,2900 if key=='DSF' else 2400,2500 if key=='DSF' else 2050,A,0,lt,bobamp=6)
        if n!='dsf': sticker(fr,'miam !' if n=='eat' else 'miam miam !',780,560,lt,0.1,A,80,(255,255,255),(60,140,60))
        if li is not None: sub(fr,li,lt)
        return fr
    if n=='pop':
        fr=cl(K,lt); actor(fr,'BR',540,2350,2000,A,0,lt,bobamp=0)
        for i in range(3):
            if lt<0.2+i*0.4: ps(fr,heart_img(),[380,700,540][i],[520,560,420][i],A,1.2)
            elif lt<0.5+i*0.4: sticker(fr,'pop',[380,700,540][i],[520,560,420][i],lt,0.2+i*0.4,A,60,(255,255,255),(200,40,80))
        return fr
    if n=='eat3':
        fr=cl(K,lt,0.1); m=max(1,24-int(23*prog(lt,0,dd))); ps(fr,BOXP(m,800),540,1150,A,1.0,dy=20); key='DEAT' if HAS('DEAT') else 'DSF'; actor(fr,key,900,2100,1300,A,0,lt*2,bobamp=10)
        sticker(fr,'miam miam miam',540,420,lt,0.1,A,70,(255,255,255),(60,140,60)); return fr
    if n=='think':
        fr=cl(K,lt); actor(fr,'BC7',540,2300,1700,A,0,lt,bobamp=0); return fr
    if n=='turn':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=0); actor(fr,'SEY',520,1960,1000,A,0,lt,bobamp=0); actor(fr,'MB',920,1940,700,A,0,lt,bobamp=0); sticker(fr,'?',540,480,lt,0.1,A,110,(255,255,255),(40,40,40)); return fr
    if n in('onecake','onecake2'):
        z=1+0.4*eo(prog(lt,0.3,dd-0.3)); fr=cl(K if n=='onecake' else AT,lt,0.1); ps(fr,BOXP(1,int(800*z)),540,1150,A,1.0,dy=20); sticker(fr,'cri-cri…',540,420,lt,0.3,A,70,(255,255,255),(60,60,60)); return fr
    if n=='headhands':
        fr=cl(K,lt); actor(fr,'BP',540,3050,2550,A,0,lt,bobamp=4); return shake(fr,lt,0.2,0.4,8)
    if n=='motoleave':
        fr=bgd(K,lt,zoom=0.08); k=eo(prog(lt,0,1.4)); actor(fr,'SEY',lerp(600,1350,k),1960,1150,A,0,lt,bobamp=6,flip=True); speed(fr,1300,1800,lt,A); return fr
    if n=='vib':
        fr=cl(AT,lt); actor(fr,'AC7',540,2400,1800,A,0,lt,bobamp=1); sticker(fr,'Bzzz… Bzzz…',540,480,lt,0.1,A,80,(255,255,255),(40,40,40)); return fr
    if n=='ah1at':
        fr=cl(AT,lt); actor(fr,'AH1',540,2400,2000,A,v,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='red':
        fr=cl(AT,lt); actor(fr,'A5c',540,2050,1650,A,0,lt,bobamp=0); redface(fr,560,620,lt,A); greysmoke(fr,330,640,lt,A,4); greysmoke(fr,760,640,lt,A,4); return shake(fr,lt,0,dd,5)
    if n=='hover':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=1); k=eo(prog(lt,0,1.8)); actor(fr,'MOUW',lerp(1300,700,k),1960,1150,A,0,lt,bobamp=2); speed(fr,1300,1800,lt,A) if k<1 else None
        sticker(fr,'Vzzzz…',600,480,lt,0.2,A,80,(255,255,255),(60,120,200)); return fr
    if n=='mou':
        fr=cl(K,lt); actor(fr,'MOU',540,2300,1900,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='jump':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=0); k=prog(lt,0,0.6); actor(fr,'MOU',lerp(700,820,k),int(1960-200*math.sin(math.pi*k)),1050,A,0,lt,bobamp=0); ps(fr,HOVER(300),620,1900,A,1.0); return fr
    if n=='tactac':
        fr=bgd(K,lt,zoom=0.1); kwide(fr,lt,A,fatim=False,awa=False); ps(fr,HOVER(260),560,1900,A,1.0); sticker(fr,'Tac-tac-tac-tac !',540,480,lt,0.1,A,80,(255,255,255),(200,40,40)); return fr
    if n=='awafast':
        fr=bgd(K,lt,zoom=0.1); ps(fr,HOVER(260),560,1900,A,1.0); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=0); k=prog(lt,0,dd); awa_walk(fr,lerp(1250,760,k),1960,1100,lt*1.6,A,flip=True); return fr
    if n=='slip':
        fr=cl(K,lt,0.08)
        if HAS('SLIP'): r=-25*eo(prog(lt,0.3,1.6)); actor(fr,'SLIP',540,2200,1800,A,0,lt,bobamp=0,rot=r)
        else:
            r=-35*eo(prog(lt,0.3,1.8)); actor(fr,'A14',540-int(160*prog(lt,0.3,1.8)),2100,1650,A,0,lt,bobamp=0,rot=r)
        if not HAS('SLIP'): k=eo(prog(lt,0.1,1.2)); ps(fr,HOVER(520),lerp(540,1250,k),1950,A,1.0)
        sticker(fr,'Ralenti…',540,380,lt,0.3,A,70,(255,255,255),(60,60,60)); return fr
    if n=='catch':
        fr=cl(K,lt,0.06); catch_pose(fr,lt,A); stars(fr,540,800,lt,A*0.6,260,6); return fr
    if n=='heart':
        fr=bgd(K,lt,blur=14); catch_pose(fr,lt,A,540,2500,2200); big_hearts(fr,lt,0.0,A*0.7); sticker(fr,'boum-boum',540,420,lt,0.2,A,80,(255,255,255),(200,40,80)); return fr
    if n=='catchc':
        fr=bgd(K,lt,blur=10)
        if HAS('CATCH'): actor(fr,'CATCH',540,2800,2700,A,0,lt,bobamp=0)
        elif li==IX['b12']: actor(fr,'BJ',540,3050,2550,A,v,lt,bobamp=0)
        else: actor(fr,'AH1',540,2400,2000,A,v,lt,bobamp=0); redface(fr,560,720,lt,A)
        sub(fr,li,lt); return fr
    if n=='awaleave':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',230,1880,880,A,0,lt,bobamp=0); k=prog(lt,0,dd*0.9); key=['AWB1','AWB3','AWB2','AWB3'][int(lt*7)%4]
        actor(fr,key,lerp(600,900,k),int(lerp(1960,1650,k)),int(lerp(1100,700,k)),A,0,lt,bobamp=0); return fr
    if n=='look':
        fr=cl(K,lt,0.1); actor(fr,'BH',540,2500,2100,A,0,lt,bobamp=0); return fr
    if n=='car':
        fr=bgd(K,lt,zoom=0.15); fr=night(fr,0.6); ps(fr,PH('CAR',700),540,1400,A,1.0,dy=14)
        wl=Image.new('RGBA',(130,85),(15,15,20,235)); ps(fr,wl,540+int((1374-1272)*700/1665),1400-350+int(355*700/1665),A,1.0)
        sticker(fr,'Vrrrooom…',540,480,lt,0.2,A,70,(255,255,255),(30,30,30)); return fr
    if n=='window':
        fr=night(bgd(K,lt,zoom=0.15),0.6); s=1100/1665; ps(fr,PH('CAR',1100),540,1300,A,1.0,dy=14)
        k=eo(prog(lt,0.2,1.5)); hh=int(260*(1-k))
        if hh>4: wl=Image.new('RGBA',(int(610*s*1.25),hh),(15,15,20,240)); ps(fr,wl,540+int(110*s*1.25),1300-int(1665*s/2)+int(160*s*1.25)+hh//2,A,1.0)
        sticker(fr,'Bzzzz…',540,420,lt,0.2,A,70,(255,255,255),(30,30,30)); return fr
    if n=='karim':
        fr=night(bgd(K,lt,zoom=0.15),0.7)
        if HAS('KCAR'): actor(fr,'KCAR',540,2000,1300,A,v,lt,bobamp=0)
        else: actor(fr,'CAR',159,3524,3200,A,v,lt,bobamp=0)
        sub(fr,li,lt); return fr
    if n=='flash':
        fr=night(bgd(K,lt,zoom=0.15),0.6); ps(fr,PH('CAR',1100),540,1300,A,1.0,dy=14)
        if 0.1<lt<0.3: fr=Image.blend(fr.convert('RGB'),Image.new('RGB',fr.size,(255,255,255)),0.85)
        sticker(fr,'clic !',780,500,lt,0.1,A,80,(255,255,255),(30,30,30)); return fr
    if n=='suite':
        fr=night(bgd(K,lt,blur=10),0.55); ps(fr,txt('À suivre…',130,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.5)),1.0,dy=10,op=0.5); return fr
    if n in('finb','finc','fin2'):
        fr=bg(lt); fin11(fr,lt,A,{'finb':1,'finc':2,'fin2':3}[n]); return fr
