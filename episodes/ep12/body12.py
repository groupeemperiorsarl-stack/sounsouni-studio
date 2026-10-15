
# ---- ép.12 « La coupure »
def HAS(k): return any(os.path.exists(d+k+'.png') for d in (HD,))
@lru_cache(None)
def DRESS(burn=False,w=560):
    h=int(w*1.3); p=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(p); c=w//2
    gold=(214,170,56); dk=(165,122,34); hi=(250,224,130)
    d.polygon([(c-int(w*0.17),20),(c-int(w*0.45),int(h*0.12)),(c-int(w*0.5),int(h*0.3)),(c-int(w*0.36),int(h*0.32)),(c-int(w*0.22),int(h*0.2)),(c-int(w*0.2),int(h*0.4)),
               (c-int(w*0.46),h-30),(c+int(w*0.46),h-30),(c+int(w*0.2),int(h*0.4)),(c+int(w*0.22),int(h*0.2)),(c+int(w*0.36),int(h*0.32)),(c+int(w*0.5),int(h*0.3)),(c+int(w*0.45),int(h*0.12)),(c+int(w*0.17),20)],fill=gold)
    d.ellipse([c-int(w*0.47),h-80,c+int(w*0.47),h-5],fill=gold)
    d.chord([c-int(w*0.12),0,c+int(w*0.12),int(h*0.1)],0,180,fill=dk)
    for i in range(9):
        x=c-int(w*0.4)+i*int(w*0.8)//8; d.line([(c+(x-c)*0.4,int(h*0.42)),(x,h-40)],fill=hi,width=max(3,w//110))
    for i in range(18):
        a=i/18*6.283; x=c+int(w*0.13*math.cos(a)); y=int(h*0.2)+int(h*0.07*math.sin(a)); r=max(4,w//80); d.ellipse([x-r,y-r,x+r,y+r],fill=(255,242,180))
    d.line([(c-int(w*0.2),int(h*0.4)),(c+int(w*0.2),int(h*0.4))],fill=dk,width=max(6,w//40))
    for x in range(c-int(w*0.42),c+int(w*0.42),max(20,w//14)): r=max(5,w//70); d.ellipse([x-r,h-50-r,x+r,h-50+r],fill=(255,236,150))
    p=p.filter(ImageFilter.SMOOTH)
    if burn:
        cx,cy=c,int(h*0.6); s=w/560; D=Image.new('RGBA',p.size,(0,0,0,0)); dd=ImageDraw.Draw(D)
        poly=lambda k:[(cx-80*s*k,cy+80*s*k),(cx+80*s*k,cy+80*s*k),(cx+70*s*k,cy-10*s*k),(cx,cy-120*s*k),(cx-70*s*k,cy-10*s*k)]
        dd.polygon(poly(1.4),fill=(100,55,12,210)); D=D.filter(ImageFilter.GaussianBlur(int(14*s)+1)); D.putalpha(Image.composite(D.getchannel('A'),Image.new('L',D.size,0),p.getchannel('A'))); p.alpha_composite(D)
        d2=ImageDraw.Draw(p); d2.polygon(poly(1.0),fill=(25,16,10,255)); d2.polygon(poly(0.72),fill=(0,0,0,0))
    return p
@lru_cache(None)
def IRON():
    p=Image.new('RGBA',(320,230),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.polygon([(10,215),(310,215),(290,120),(150,95),(40,140)],fill=(48,46,50)); d.rectangle([20,200,300,222],fill=(28,28,30))
    for x in range(70,280,40): d.ellipse([x,150,x+16,166],fill=(255,110,30))
    d.line([(90,100),(110,30),(240,30),(250,100)],fill=(120,80,40),width=18); return p
@lru_cache(None)
def BATT():
    p=Image.new('RGBA',(420,330),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.polygon([(30,10),(390,10),(410,120),(10,120)],fill=(30,60,140));
    for i in range(1,6): d.line([(30+i*60,10),(10+i*67,120)],fill=(150,190,255),width=3)
    d.line([(20,65),(400,65)],fill=(150,190,255),width=3)
    d.rounded_rectangle([60,150,360,320],radius=24,fill=(230,120,20)); d.rounded_rectangle([90,180,330,250],radius=12,fill=(40,40,40))
    d.text((210,215),'SOLAIRE',font=font(FB,40),fill=(120,255,140),anchor='mm'); d.ellipse([300,270,326,296],fill=(80,255,90))
    for i in range(3): d.rounded_rectangle([90+i*60,268,130+i*60,298],radius=6,fill=(30,30,30))
    return p
@lru_cache(None)
def MACH():
    p=Image.new('RGBA',(520,420),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rectangle([10,330,510,360],fill=(120,80,40)); d.rectangle([40,360,70,420],fill=(90,60,30)); d.rectangle([450,360,480,420],fill=(90,60,30))
    d.rounded_rectangle([60,250,470,330],radius=20,fill=(25,25,28)); d.rounded_rectangle([360,60,450,300],radius=30,fill=(25,25,28))
    d.rounded_rectangle([90,40,450,130],radius=40,fill=(25,25,28)); d.rectangle([110,120,140,250],fill=(25,25,28)); d.rectangle([118,250,128,300],fill=(200,200,200))
    d.text((270,85),'COUTURE',font=font(FB,36),fill=(212,168,52),anchor='mm'); d.ellipse([440,120,500,240],fill=(60,60,64)); return p
def embers(fr,x,y,lt,A,s=1.0):
    for i in range(14):
        k=(lt*0.9+i/14)%1; D=Image.new('RGBA',(30,30),(0,0,0,0)); ImageDraw.Draw(D).ellipse([6,6,24,24],fill=(255,int(120+100*(i%3)/2),30,255)); put(fr,D,x+((i*47)%200-100)*s+15*math.sin(lt*3+i),y-k*300*s,A*(1-k))
    D=Image.new('RGBA',(int(300*s),int(90*s)),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,int(300*s)-1,int(90*s)-1],fill=(255,90,20,200+int(40*math.sin(lt*9)))); put(fr,D.filter(ImageFilter.GaussianBlur(6)),x,y,A)
def puff(fr,x,y,lt,A):
    for i in range(4):
        k=(lt*1.2+i/4)%1; D=Image.new('RGBA',(80,40),(0,0,0,0)); ImageDraw.Draw(D).line([(0,20),(70,20)],fill=(255,255,255,200),width=8); put(fr,D,x+k*160,y+(i-1.5)*30,A*(1-k))
def greysmoke(fr,x,y,lt,A,n=6):
    for i in range(n):
        k=(lt*0.5+i/n)%1; r=int(30+k*90); D=Image.new('RGBA',(r*2+40,r*2+40),(0,0,0,0)); ImageDraw.Draw(D).ellipse([20,20,r*2+19,r*2+19],fill=(150,150,150,int(170*(1-k)))); put(fr,D.filter(ImageFilter.GaussianBlur(8)),x+25*math.sin(i*1.7+lt*2),y-k*420,A)
def bubbleT(fr,lt,A):  # bulle de pensée
    for i,(x,y,r) in enumerate([(700,1150,26),(760,1060,40)]): D=Image.new('RGBA',(r*2,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*2-1,r*2-1],fill=(255,255,255,220)); put(fr,D,x,y,A)
@lru_cache(None)
def phone12(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.text((30,232),'Ma boutique',font=font(FM,32),fill=(110,130,100)); d.text((30,272),'Awa Couture',font=font(FB,50),fill=ENCRE)
    if kind=='order':
        d.rounded_rectangle([24,370,576,1120],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,430),'Grosse commande',font=font(FB,42),fill=(200,100,10),anchor='mm'); r=DRESS(False,200); S.paste(r,(200,470),r)
        d.text((300,780),'15 tenues de mariage',font=font(FB,40),fill=ENCRE,anchor='mm'); d.text((300,840),'Cliente : Tantie Kadi',font=font(FM,34),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([50,900,550,980],radius=40,fill=(220,50,40)); d.text((300,940),"Retrait aujourd'hui · 12h",font=font(FB,34),fill=(255,255,255),anchor='mm')
        d.text((300,1040),'14 / 15 prêtes',font=font(FB,36),fill=FONCE,anchor='mm')
    else:
        d.rounded_rectangle([24,400,576,820],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.ellipse([60,440,170,550],fill=(130,30,50)); d.text((115,495),'K',font=font(FB,60),fill=(255,255,255),anchor='mm')
        d.text((190,470),'Tantie Kadi',font=font(FB,42),fill=ENCRE); d.text((190,525),'maintenant',font=font(FM,28),fill=(120,120,120))
        d.text((300,640),"J'arrive dans 10 minutes,",font=font(FB,38),fill=ENCRE,anchor='mm'); d.text((300,700),'ma fille.',font=font(FB,38),fill=ENCRE,anchor='mm')
    return S
@lru_cache(None)
def P12(kind): return phone_with(phone12(kind))
AW_='AW'
def dark(fr): return night(fr,0.5)
def awm(fr,lt,A,v,h=1500,cx=540,by=2050):
    if HAS('AWM'): actor(fr,'AWM',cx,by,h,A,v,lt,bobamp=2)
    else:
        actor(fr,'A20',cx+60,by,int(h*1.1),A,0,lt,bobamp=2); ps(fr,MACH(),cx-170,by-int(h*0.32),A,h/1500*1.2,dy=20)
        ps(fr,DRESS(False,300),cx-170,by-int(h*0.13),A,h/1500,dy=10)
def draw(n,lt,dd,li,A):
    v=talk(li,lt); D=dark
    if n=='titre':
        fr=bgd(AT,lt,blur=6); ps(fr,ICON.resize((220,220),Image.LANCZOS),540,620,A*eo(prog(lt,0,0.4)),0.5+0.5*back(prog(lt,0,0.5)))
        ps(fr,dpanel('Les Plans de Bakary',78),540,880,A*eo(prog(lt,0.2,0.4)),0.6+0.4*back(prog(lt,0.2,0.5))); pp(fr,'Épisode 12 · La coupure',lt,0.6,A,1040,50); return fr
    if n=='atel':
        fr=bgd(AT,lt,zoom=0.08); card(fr,'10 h 30 · Atelier',lt,A); actor(fr,'MP1',360,1900,900,A,0,lt,bobamp=1); actor(fr,'AW',820,1960,1150,A,0,lt,bobamp=2)
        ps(fr,DRESS(False,260),640,1500,A,1.0,dy=10); return fr
    if n=='aw':
        fr=cl(AT,lt); actor(fr,'AW',540,2700,2300,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n in('mp1','mp3','mp2','mp1d','mp2d'):
        key=n[:3].upper(); fr=cl(AT,lt); actor(fr,key,500,2350,1700,A,0,lt,bobamp=2)
        if n.endswith('d'): fr=D(fr)
        if n=='mp2' and li==IX['i11']: greysmoke(fr,900,1500,lt,A); fr=shake(fr,lt,LEAD[li],0.5,10)
        sub(fr,li,lt); return fr
    if n=='app':
        fr=bgd(AT,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P12('order'),540,lerp(1300,1100,k),A,1.15,dy=30)
        pp(fr,'Commande de Tantie Kadi',lt,0.3,A,230,40,bg=(130,30,50),fg=(255,255,255)); return fr
    if n=='cut':
        fr=bgd(AT,lt,zoom=0.08); actor(fr,'MP1',360,1900,900,A,0,lt,bobamp=0); actor(fr,'AW',820,1960,1150,A,0,lt,bobamp=0)
        if lt>0.3:
            fr=night(fr,0.75)
            if lt<0.45: fr=Image.blend(fr.convert('RGB'),Image.new('RGB',fr.size,(255,255,255)),0.7)
            sticker(fr,'COUPURE !',540,520,lt,0.4,A,120,(255,255,255),(30,30,30))
        return shake(fr,lt,0.3,0.5,14)
    if n=='a14d':
        fr=D(cl(AT,lt)); actor(fr,'A14',540,2050,1600,A,0,lt,bobamp=0); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.5,8)
    if n in('a5d','a5'):
        bgk=AT if n=='a5d' else K; fr=cl(bgk,lt); fr=D(fr) if n=='a5d' else fr; key='A5o' if v>0.15 else 'A5c'; actor(fr,key,540,2050,1650,A,0,lt,bobamp=3); sub(fr,li,lt); return fr
    if n in('a20d','a20'):
        fr=cl(AT if n=='a20d' else K,lt); fr=D(fr) if n=='a20d' else fr; actor(fr,'A20',540,2400,2100,A,0,lt,bobamp=0)
        if li==IX['a09']: sticker(fr,'Jamais !',800,560,lt,LEAD[li]+0.3,A,90,(255,255,255),(150,40,40))
        sub(fr,li,lt); return fr
    if n=='kcard':
        fr=bgd(K,lt,blur=10); card(fr,'Pendant ce temps, au kiosque…',lt,A); return fr
    if n=='kwide':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'DSG',560,1560,820,A,0,lt,bobamp=2); grillfx(fr,520,1250,lt,A*0.8)
        actor(fr,'BV1',280,1920,1000,A,0,lt,bobamp=2); actor(fr,'MB',830,1930,760,A,0,lt,bobamp=1); ps(fr,BATT(),900,1640,A,0.55,dy=10)
        pp(fr,'Ici, pas de coupure !',lt,0.6,A,300,44,bg=(255,255,255),fg=FONCE); return fr
    if n=='dsg':
        fr=cl(K,lt); actor(fr,'DSG',540,2300,1700,A,v,lt,bobamp=3); grillfx(fr,520,1700,lt,A*0.8); sub(fr,li,lt); return fr
    if n in('mbat','mdk','mbw'):
        fr=cl(K,lt)
        if n=='mbw': actor(fr,'MB',540,2100,1300,A,0,lt,bobamp=1); sticker(fr,'psst…',800,620,lt,0.2,A,70,(255,255,255),(60,60,60))
        else: actor(fr,'MD',540,1990,1180,A,v,lt,bobamp=4)
        if n=='mbat': ps(fr,BATT(),830,1500,A,0.9,dy=14); stars(fr,830,1400,lt,A,160,5)
        sub(fr,li,lt); return fr
    if n=='bv':
        fr=cl(K,lt); actor(fr,'BA',540,2350,2000,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n in('br','ba','bj','bp'):
        key=n.upper(); fr=cl(K,lt); actor(fr,key,540,2350 if key in('BR','BA') else 3050,2000 if key in('BR','BA') else 2550,A,v,lt,bobamp=3)
        if n=='br' and li==IX['b06']: ps(fr,IRON(),800,1500,A,1.0,dy=10); greysmoke(fr,800,1350,lt,A*0.6,4)
        if n=='bp': sweat(fr,740,520,lt,A)
        if n=='bj' and li==IX['b08']: fr=night(fr,0.25)
        sub(fr,li,lt); return fr
    if n=='mrun':
        fr=bgd(K,lt,zoom=0.1); k=eo(prog(lt,0,1.8)); actor(fr,'MI',560,1930,1050,A,0,lt*3,bobamp=10)
        if lt<0.6: speed(fr,1300,1800,lt,A)
        actor(fr,'BV1',880,1920,1000,A,0,lt,bobamp=2); sweat(fr,600,960,lt,A); sticker(fr,'Hhh… hhh…',380,620,lt,0.3,A,70,(255,255,255),(200,120,20))
        return fr
    if n in('me','meclock'):
        fr=cl(K,lt); actor(fr,'MI',1080-int(1900*520/1517)//2,2350,1900,A,v,lt,bobamp=4)
        if li in(IX['i06'],IX['i07'],IX['i12']): sweat(fr,700,560,lt,A)
        if li==IX['i11']: greysmoke(fr,900,1500,lt,A); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.5,10)
        if n=='meclock': sticker(fr,'11 h 05',280,900,lt,LEAD[li]+0.8,A,100,(255,255,255),(200,30,30))
        sub(fr,li,lt); return fr
    if n=='dic':
        fr=cl(K,lt); actor(fr,'DIC',540,3150,2650,A,v,lt); sub(fr,li,lt); return fr
    if n=='awalk':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',290,1900,940,A,0,lt,bobamp=2); actor(fr,'MI',1080-int(900*520/1517)//2,1900,900,A,0,lt,bobamp=1)
        k=prog(lt,0,dd); actor(fr,'AWK',lerp(-150,560,k),1960,1050,A,0,lt,bobamp=6); sticker(fr,'Brrr…',540,480,lt,1.2,A,80,(255,255,255),(60,120,200)); return fr
    if n=='teeth':
        z=1+0.25*eo(prog(lt,0,dd)); fr=cl(K,lt); actor(fr,'A20',540,int(2400+(z-1)*1300),int(2100*z),A,0,lt,bobamp=0); return fr
    if n=='d10':
        fr=bgd(K,lt,zoom=0.08); actor(fr,'DI10',540,1950,1300,A,0,lt,bobamp=10); ps(fr,MACH(),560,950,A,0.75,dy=10); sub(fr,li,lt); return fr
    if n=='bonk':
        fr=bgd(K,lt,zoom=0.1); k=eo(prog(lt,0,0.4)); actor(fr,'DI10',lerp(300,560,k),1950,1300,A,0,lt,bobamp=4); ps(fr,MACH(),lerp(320,580,k),950,A,0.75,dy=10)
        if lt>0.35: stars(fr,600,620,lt,A,140,6); sticker(fr,'BONK !',540,420,lt,0.35,A,120,(255,255,255),(200,30,30))
        return shake(fr,lt,0.35,0.6,16)
    if n=='die':
        fr=cl(K,lt); actor(fr,'DIE',540,3150,2650,A,v,lt,bobamp=8); sweat(fr,700,520,lt,A); sub(fr,li,lt)
        return shake(fr,lt,LEAD[li],dd,4) if li==IX['d07'] else fr
    if n=='mr':
        fr=cl(K,lt); actor(fr,'MR',540,2080,1350,A,0,lt,bobamp=10); sub(fr,li,lt); return fr
    if n=='sewwide':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',230,1900,900,A,0,lt,bobamp=1); embers(fr,330,1700,lt,A,0.6); ps(fr,IRON(),330,1640,A,0.5)
        awm(fr,lt,A,0,1150,640,1980); actor(fr,'MB',940,1940,700,A,0,lt,bobamp=1); ps(fr,BATT(),930,1740,A,0.45)
        pp(fr,'Atelier de secours',lt,0.4,A,300,44,bg=(255,255,255),fg=FONCE); return fr
    if n=='awm':
        fr=cl(K,lt); awm(fr,lt,A,v); sub(fr,li,lt); return fr
    if n=='blow':
        fr=cl(K,lt)
        if HAS('BLOW'): actor(fr,'BLOW',540,2200,1700,A,0,lt,bobamp=2); embers(fr,540,1900,lt,A,1.0)
        else: actor(fr,'BR',540,2350,2000,A,0,lt,bobamp=3); embers(fr,540,1850,lt,A,1.2); ps(fr,IRON(),540,1760,A,1.1); puff(fr,560,1280,lt,A)
        sub(fr,li,lt); return fr
    if n=='touch':
        fr=cl(K,lt,0.1); k=eo(prog(lt,0,0.6)); actor(fr,'BR',lerp(-100,300,k),2350,2000,A,0,lt,bobamp=0); ps(fr,IRON(),lerp(100,560,k),1300,A,0.9)
        actor(fr,'A20',lerp(1200,820,k)+(60*eo(prog(lt,1.6,0.3)) if lt>1.6 else 0),2400,2100,A,0,lt,bobamp=0)
        if 0.8<lt<1.6: big_hearts(fr,lt,0.8,A*0.8)
        if lt>1.6: sticker(fr,'!',960,520,lt,1.6,A,120,(255,255,255),(200,30,30))
        return fr
    if n in('think','think2'):
        fr=cl(K,lt); actor(fr,'A20',540,2400,2100,A,0,lt,bobamp=0); bubbleT(fr,lt,A)
        if n=='think2': greysmoke(fr,300,1700,lt,A*0.5,4)
        sub(fr,li,lt); return fr
    if n=='diw':
        fr=cl(K,lt); actor(fr,'DIW',540,3150,2650,A,v,lt); sub(fr,li,lt); return fr
    if n=='buzz':
        fr=bgd(KE,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P11('call'),540+8*math.sin(lt*60),lerp(1300,1100,k),A,1.15,rot=-4,dy=30); ringfx(fr,540,500,lt,A)
        sticker(fr,'Bzzz… Bzzz…',540,1800,lt,0.2,A,80,(255,255,255),(40,40,40)); return fr
    if n=='grpcall':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'DIW',500,1700,1080,A,v,lt,bobamp=1); actor(fr,'BRc',250,1900,900,A,0,lt,bobamp=1); awm(fr,lt,A,0,900,820,1990)
        ps(fr,PHONE_S(),600,980,A,0.55,rot=-15); ringfx(fr,600,920,lt,A*0.8); sub(fr,li,lt); return fr
    if n=='stare':
        z=1+0.35*eo(prog(lt,0,dd)); fr=cl(K,lt); fr=night(fr,0.2); actor(fr,'A20',540,int(2400+(z-1)*1500),int(2100*z),A,0,lt,bobamp=0)
        if 0.15<lt<0.35: fr=Image.blend(fr.convert('RGB'),Image.new('RGB',fr.size,(255,255,255)),0.5)
        return fr
    if n=='ironrest':
        fr=cl(K,lt,0.1); ps(fr,DRESS(False,700),540,1250,A,1.0,dy=20); ps(fr,IRON(),540,1150,A,1.4,dy=14); greysmoke(fr,540,1000,lt,A*min(1,lt/1.5),5)
        sticker(fr,'Le fer…',540,420,lt,0.6,A,90,(255,255,255),(30,30,30)); return fr
    if n=='ms':
        fr=cl(K,lt); actor(fr,'MS',540,2050,1250,A,0,lt,bobamp=2); greysmoke(fr,200,1500,lt,A*0.8); sub(fr,li,lt); return fr
    if n=='lift':
        fr=cl(K,lt,0.1); k=eo(prog(lt,0.3,0.8)); ps(fr,DRESS(lt>0.5,700),540,1250,A,1.0,dy=20); ps(fr,IRON(),540,lerp(1150,500,k),A,1.4,dy=14); greysmoke(fr,540,1100,lt,A,7); return shake(fr,lt,0.5,0.6,10)
    if n=='hole':
        fr=night(cl(K,lt,0.1),0.15); z=1+0.25*eo(prog(lt,0,dd))
        if HAS('ROBEH'): ps(fr,PH('ROBEH',int(1300*z)),540,1150,A,1.0,dy=20)
        else: ps(fr,DRESS(True,int(720*z)),540,1150,A,1.0,dy=20)
        greysmoke(fr,540,1050,lt,A*0.5,4); return fr
    if n=='notif':
        fr=night(bgd(K,lt,blur=8),0.2); k=eo(prog(lt,0,0.35)); ps(fr,P12('kadi'),540,lerp(1300,1100,k),A,1.15,dy=30)
        pp(fr,'Tantie Kadi',lt,0.3,A,230,44,bg=(130,30,50),fg=(255,255,255)); return fr
    if n=='steps':
        fr=night(bgd(K,lt,zoom=0.1),0.3); actor(fr,'DIE',300,1950,1100,A,0,lt,bobamp=0); actor(fr,'MS',800,1950,800,A,0,lt,bobamp=0)
        for i in range(3):
            if lt>0.3+i*0.75: sticker(fr,'BOUM',[250,800,540][i],[520,700,420][i],lt,0.3+i*0.75,A,100,(255,255,255),(90,40,30))
        return shake(fr,lt,0.3,dd,10)
    if n=='final':
        z=1+0.2*eo(prog(lt,0,dd)); fr=night(cl(K,lt),0.2)
        if HAS('AROBE'): actor(fr,'AROBE',540,int(2300+(z-1)*1300),int(1900*z),A,0,lt,bobamp=0)
        else: actor(fr,'A14',540,int(2050+(z-1)*1300),int(1600*z),A,0,lt,bobamp=0); ps(fr,DRESS(True,int(440*z)),540,1880,A,1.0,dy=20)
        if lt>1.6: actor(fr,'BPc',900,2200,900,A*eo(prog(lt,1.6,0.4)),0,lt,bobamp=0)
        return fr
    if n=='suite':
        fr=night(bgd(K,lt,blur=10),0.55); ps(fr,txt('À suivre…',130,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.5)),1.0,dy=10,op=0.5); return fr
    if n in('fin','finb','finc','fin2'):
        fr=bg(lt); fin12(fr,lt,A,{'fin':0,'finb':1,'finc':2,'fin2':3}[n]); return fr
def fin12(fr,lt,A,step):
    ps(fr,ICON.resize((260,260),Image.LANCZOS),540,330+bob(lt,2.5,8),A,1.0,dy=30)
    ps(fr,txt('Sounsouni',120,FONCE),540,580,A,1.0,dy=8,op=0.25)
    if step>=0: pp(fr,'Votre boutique reste ouverte',lt,0.2 if step==0 else -1,A,760,40,bg=(255,255,255),fg=FONCE)
    if step>=1: pp(fr,"Téléchargez l'application sur",lt,0.1 if step==1 else -1,A,860,44)
    if step>=1: ps(fr,txt('sounsouni.pro',130,FONCE),540,1010,A*eo(prog(lt,0.4,0.4)) if step==1 else A,1.0,dy=8,op=0.25)
    if step>=2:
        step=min(step,3); pp(fr,'Ou achetez directement sur le site',lt,0.1 if step==2 else -1,A,1200,42,bg=(255,255,255),fg=FONCE)
        for i,kd in enumerate(['android','iphone']):
            kk=prog(lt,1.5+i*0.8,0.4) if step==2 else 1; ps(fr,badge(kd),540,1420+i*200,A*eo(kk),0.85*(0.5+0.5*back(kk)))
