
# ---- ép.11 : décors, écrans, effets
K='KIOSK'; KE='KIOSKe'; MK='D8'; AT='D4'
@lru_cache(None)
def phone11(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    if kind=='call':
        for y in range(SH):
            c=int(30+40*y/SH); d.line([(0,y),(SW,y)],fill=(c,c+10,c+40))
        d.text((300,260),'Appel entrant',font=font(FM,40),fill=(220,230,255),anchor='mm')
        d.ellipse([200,360,400,560],fill=(200,40,120)); d.text((300,460),'F',font=font(FB,110),fill=(255,255,255),anchor='mm')
        d.text((300,640),'Fatim',font=font(FB,70),fill=(255,255,255),anchor='mm'); d.text((300,720),'Boutique de crédit',font=font(FM,32),fill=(200,210,240),anchor='mm')
        d.ellipse([90,880,230,1020],fill=(220,50,50)); d.ellipse([370,880,510,1020],fill=(40,180,80))
        d.text((160,950),'✕'.replace('✕','x'),font=font(FB,60),fill=(255,255,255),anchor='mm'); d.text((440,950),'OK',font=font(FB,44),fill=(255,255,255),anchor='mm')
        return S
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.text((30,230),'Sali Délices',font=font(FB,50),fill=ENCRE); d.text((30,300),'Beignets chauds',font=font(FM,32),fill=(110,130,100))
    d.rounded_rectangle([24,370,576,520],radius=28,fill=(220,50,40)); d.text((300,445),'3 nouvelles commandes !',font=font(FB,40),fill=(255,255,255),anchor='mm')
    for i,(a,b) in enumerate([('10 beignets','Badalabougou'),('6 beignets','Sotelco'),('15 beignets','Bougouba')]):
        y=560+i*150; d.rounded_rectangle([30,y,570,y+125],radius=24,fill=(255,243,226),outline=ORANGE,width=4)
        d.text((60,y+42),a,font=font(FB,38),fill=ENCRE,anchor='lm'); d.text((60,y+90),b,font=font(FM,30),fill=(120,120,120),anchor='lm')
    return S
@lru_cache(None)
def P11(kind): return phone_with(phone11(kind))
@lru_cache(None)
def tomato(r=34):
    D=Image.new('RGBA',(r*2+8,r*2+8),(0,0,0,0)); d=ImageDraw.Draw(D); d.ellipse([4,8,r*2+4,r*2+6],fill=(215,35,30)); d.ellipse([r-6,12,r+14,r],fill=(255,140,120,150))
    d.polygon([(r+4,4),(r-10,16),(r+4,12),(r+18,16)],fill=(40,140,40)); return D
@lru_cache(None)
def leaf():
    D=Image.new('RGBA',(120,60),(0,0,0,0)); d=ImageDraw.Draw(D); d.ellipse([0,8,110,52],fill=(150,100,40)); d.line([(5,30),(115,30)],fill=(100,60,20),width=4); return D
def rolling(fr,lt,A,y=1700,n=7):
    for i in range(n):
        x=200+i*120+lt*(140+i*40)*(1 if i%2 else -1); ps(fr,tomato(),x,y+((i*37)%120),A,1.0,rot=lt*300*(1 if i%2 else -1),dy=6,op=0.2)
def ringfx(fr,x,y,lt,A):
    for i in range(3):
        k=(lt*1.5+i/3)%1; r=int(60+k*160); D=Image.new('RGBA',(r*2+10,r*2+10),(0,0,0,0)); ImageDraw.Draw(D).arc([5,5,r*2+5,r*2+5],200,340,fill=(255,255,255,int(230*(1-k))),width=10); put(fr,D,x,y,A)
def drops2(fr,x,y,lt,A):
    for i in range(4):
        k=(lt*0.8+i/4)%1; D=Image.new('RGBA',(40,60),(0,0,0,0)); ImageDraw.Draw(D).ellipse([4,14,36,56],fill=(140,200,255,220)); ImageDraw.Draw(D).polygon([(20,0),(6,30),(34,30)],fill=(140,200,255,220))
        put(fr,D,x+(i-1.5)*70,y+k*260,A*(1-k))
def blacksmoke(fr,x,y,lt,A):
    for i in range(7):
        k=(lt*0.6+i/7)%1; r=int(35+k*110); D=Image.new('RGBA',(r*2+40,r*2+40),(0,0,0,0)); ImageDraw.Draw(D).ellipse([20,20,r*2+19,r*2+19],fill=(45,45,45,int(190*(1-k)))); put(fr,D.filter(ImageFilter.GaussianBlur(9)),x+30*math.sin(i*1.3+lt*2),y-k*600,A)
def redface(fr,x,y,lt,A):
    k=prog(lt,0.2,1.0); L_=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(L_).ellipse([x-200,y-220,x+200,y+200],fill=(230,40,30,int(90*k))); L_=L_.filter(ImageFilter.GaussianBlur(40)); fr.paste(L_,(0,0),L_)
def fin11(fr,lt,A,step):
    ps(fr,ICON.resize((260,260),Image.LANCZOS),540,330+bob(lt,2.5,8),A,1.0,dy=30)
    ps(fr,txt('Sounsouni',120,FONCE),540,580,A,1.0,dy=8,op=0.25)
    if step>=0: pp(fr,'Chaque petit commerce a sa boutique',lt,0.2 if step==0 else -1,A,760,40,bg=(255,255,255),fg=FONCE)
    if step>=1: pp(fr,"Téléchargez l'application sur",lt,0.1 if step==1 else -1,A,860,44)
    if step>=1: ps(fr,txt('sounsouni.pro',130,FONCE),540,1010,A*eo(prog(lt,0.4,0.4)) if step==1 else A,1.0,dy=8,op=0.25)
    if step>=2:
        step=min(step,3)
        pp(fr,'Ou achetez directement sur le site',lt,0.1 if step==2 else -1,A,1200,42,bg=(255,255,255),fg=FONCE)
        for i,kd in enumerate(['android','iphone']):
            kk=prog(lt,1.5+i*0.8,0.4) if step==2 else 1; ps(fr,badge(kd),540,1420+i*200,A*eo(kk),0.85*(0.5+0.5*back(kk)))
def cl(bg,lt,z=0.06): return bgd(bg,lt,blur=BL,zoom=z)
def draw(n,lt,dd,li,A):
    v=talk(li,lt)
    if n=='titre':
        fr=bgd(K,lt,blur=6); ps(fr,ICON.resize((220,220),Image.LANCZOS),540,620,A*eo(prog(lt,0,0.4)),0.5+0.5*back(prog(lt,0,0.5)))
        ps(fr,dpanel('Les Plans de Bakary',78),540,880,A*eo(prog(lt,0.2,0.4)),0.6+0.4*back(prog(lt,0.2,0.5))); pp(fr,'Épisode 11 · Le haut-parleur',lt,0.6,A,1040,50); return fr
    if n=='open':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'DSG',560,1560,820,A,0,lt,bobamp=2); grillfx(fr,520,1250,lt,A*0.8)
        actor(fr,'BRc',290,1900,940,A,0,lt,bobamp=2); actor(fr,'MBN',800,1930,820,A,0,lt,bobamp=1); big_hearts(fr,lt,0.3,A*0.7); return fr
    # ---- gros plans
    if n in('mdC','mdK','mdM','mdH'):
        fr=cl(MK if n in('mdM','mdH') else (KE if n=='mdK' else K),lt); actor(fr,'MD',540,1990,1180,A,v,lt,bobamp=4)
        if n=='mdH': big_hearts(fr,lt,0.0,A*0.7)
        sub(fr,li,lt); return fr
    if n in('brC','brC2'):
        fr=cl(K if n=='brC' else KE,lt); actor(fr,'BR',540,2350,2000,A,v,lt,bobamp=3)
        if n=='brC': big_hearts(fr,lt,0.0,A*0.8)
        sub(fr,li,lt); return fr
    if n=='baC':
        fr=cl(K if li==IX['b_arb'] else KE,lt); actor(fr,'BA',540,2350,2000,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='ds4':
        fr=cl(K,lt); actor(fr,'DS4',540,3050,2550,A,v,lt); sub(fr,li,lt); return fr
    if n=='laugh':
        fr=cl(K,lt,0.08); actor(fr,'BL',330,2650,2000,A,0,lt,bobamp=14); actor(fr,'MR',790,2080,1350,A,0,lt,bobamp=14)
        for i,(x,y) in enumerate([(250,420),(800,380),(540,300)]): sticker(fr,'Ha ha ha !',x,y,lt,0.3+i*0.6,A,70,(255,255,255),(240,150,20))
        return shake(fr,lt,0,dd,6)
    if n in('di6','dic','did','diw'):
        key={'di6':'DI6','dic':'DIC','did':'DID','diw':'DIW'}[n]; fr=cl(KE if li in(IX['d_madame'],IX['d_bobo']) else K,lt); actor(fr,key,540,3150,2650,A,v,lt)
        sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.5,10) if li==IX['d_parie'] else fr
    # ---- marché
    if n=='midi':
        fr=bgd(MK,lt,blur=10); card(fr,'Midi – Grand marché',lt,A); return fr
    if n=='mwide':
        fr=bgd(MK,lt,zoom=0.08); k=eo(prog(lt,0,2.0)); actor(fr,'MP',300,1880,1150,A,0,lt,bobamp=2); actor(fr,'SA1',lerp(1250,760,k),1890,1180,A,0,lt,flip=True,bobamp=8 if k<1 else 1); return fr
    if n in('sa2','sa2y'):
        fr=cl(MK,lt); actor(fr,'SA2',540,2030,1500,A,v,lt,bobamp=3)
        if n=='sa2y': stars(fr,540,500,lt,A,160,6)
        sub(fr,li,lt); return fr
    if n=='slaugh':
        fr=cl(MK,lt); actor(fr,'SA6b',540,3000,2500,A,0,lt,bobamp=6); sticker(fr,'Hi hi hi…',780,520,lt,0.3,A,70,(255,255,255),(30,120,190)); return fr
    if n=='spy':
        fr=bgd(MK,lt,zoom=0.1); actor(fr,'DI9',540,1900,950,A,0,lt,bobamp=2); k=prog(lt,1.4,0.6)
        if 0<k<1 or lt>2.0: ps(fr,tomato(),380-k*60,lerp(1480,1880,eo(k)) if lt<2.0 else 1880,A,1.0,rot=k*200)
        sticker(fr,'Hmm…',760,700,lt,0.3,A,70,(255,255,255),(60,140,60)); return fr
    if n in('sa5',):
        fr=cl(MK,lt); actor(fr,'SA5',540,2030,1500,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n in('mt','click'):
        fr=cl(MK,lt); actor(fr,'MT',540,1990,1180,A,v,lt,bobamp=2)
        if n=='click': sticker(fr,'clic !',780,700,lt,0.2,A,80,(255,255,255),(40,40,40))
        sub(fr,li,lt); return fr
    if n=='app':
        fr=bgd(MK,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P11('sali'),540,lerp(1300,1100,k),A,1.15,dy=30)
        pp(fr,"L'écran remarche !",lt,0.3,A,230,40,bg=(30,120,190),fg=(255,255,255)); return fr
    if n=='sa6b':
        fr=cl(MK,lt); actor(fr,'SA6b',540,3000,2500,A,0,lt,bobamp=3); sub(fr,li,lt); return fr
    if n=='sa6':
        fr=cl(MK,lt); actor(fr,'SA6',540,3000,2500,A,0,lt,bobamp=3); big_hearts(fr,lt,0.2,A*0.4); sub(fr,li,lt); return fr
    if n=='sleave':
        fr=bgd(MK,lt,zoom=0.08); k=prog(lt,0,2.2); actor(fr,'SAB',lerp(700,820,k),int(lerp(1900,1700,k)),int(lerp(1200,820,k)),A,0,lt,bobamp=6); actor(fr,'MP',300,1880,1150,A,0,lt,bobamp=2); big_hearts(fr,lt,0.2,A*0.8); return fr
    if n=='tback':
        fr=bgd(MK,lt,zoom=0.1); key='DI9' if lt<0.5 else 'DI9b'; actor(fr,key,540,1900,950 if key=='DI9' else 1050,A,0,lt,bobamp=2)
        if lt>0.5: rolling(fr,lt-0.5,A,1750,4)
        return shake(fr,lt,0.6,0.6,12)
    if n=='crash':
        fr=cl(MK,lt); actor(fr,'ET2',540,1800,900,A,0,lt,bobamp=0); rolling(fr,lt,A,1650,8); sticker(fr,'CRAAAC !',540,520,lt,0.0,A,120,(255,255,255),(200,30,30)); return shake(fr,lt,0,0.8,16)
    if n=='to':
        fr=cl(MK,lt); actor(fr,'TO',540,2500,2100,A,v,lt,bobamp=6); sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.6,8)
    if n=='di10':
        fr=bgd(MK,lt,zoom=0.08); k=eo(prog(lt,0,dd)); speed(fr,900,1700,lt,A); actor(fr,'DI10',lerp(380,900,k),1900,1250,A,0,lt,bobamp=16)
        for i in range(3): ps(fr,tomato(),lerp(250,780,k)-i*120,1100+i*90+40*math.sin(lt*8+i),A,1.0,rot=lt*400)
        sub(fr,li,lt); return fr
    # ---- kiosque, fin d'après-midi
    if n=='soir':
        fr=bgd(KE,lt,blur=10); card(fr,"Fin d'après-midi",lt,A); return fr
    if n=='kw2':
        fr=bgd(KE,lt,zoom=0.1); actor(fr,'DSG',560,1560,820,A,0,lt,bobamp=2); grillfx(fr,520,1250,lt,A*0.8); actor(fr,'BV1',300,1920,1000,A,0,lt,bobamp=2)
        k=eo(prog(lt,0.8,1.4)); actor(fr,'MRUN',lerp(1300,800,k),1900,780,A,0,lt,flip=True,bobamp=10); return fr
    if n=='mj':
        fr=cl(KE,lt); actor(fr,'MJ',540,1990,700,A,v,lt,bobamp=10); stars(fr,540,700,lt,A,200,7); sub(fr,li,lt); return fr
    if n=='die':
        fr=cl(KE,lt); actor(fr,'DIE',540,3150,2650,A,v,lt,bobamp=8); sweat(fr,700,520,lt,A); sub(fr,li,lt); return fr
    if n=='bl':
        fr=cl(KE,lt); actor(fr,'BL',540,3050,2400,A,0,lt,bobamp=12); sticker(fr,'Ha ha !',780,520,lt,0.1,A,80,(255,255,255),(240,150,20)); return fr
    if n=='awalk':
        fr=bgd(KE,lt,zoom=0.1); actor(fr,'BRc',290,1900,940,A,0,lt,bobamp=2); actor(fr,'DIW',800,1880,1150,A,0,lt,bobamp=1)
        k=prog(lt,0,dd); actor(fr,'AWK',lerp(-150,600,k),1960,1050,A,0,lt,bobamp=6); big_hearts(fr,lt,1.2,A*0.8); return fr
    if n=='ring':
        fr=cl(KE,lt); actor(fr,'BRc',540,2350,2000,A,0,lt,bobamp=0); ringfx(fr,860,1300,lt,A); sticker(fr,'Driiing !',800,520,lt,0.1,A,80,(255,255,255),(40,40,40)); return shake(fr,lt,0,dd,3)
    if n=='callscr':
        fr=bgd(KE,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P11('call'),540,lerp(1300,1100,k),A,1.15,dy=30); ringfx(fr,540,500,lt,A); return fr
    if n=='di7':
        fr=cl(KE,lt); actor(fr,'DI7',600,1990,1250,A,v,lt,bobamp=3); sub(fr,li,lt); return fr
    if n in('hp','spk'):
        fr=cl(KE,lt); actor(fr,'DI1',540,2350,1900,A,0,lt,bobamp=2); ringfx(fr,560,1480,lt,A*0.7)
        if n=='hp': sticker(fr,'HAUT-PARLEUR',540,560,lt,0.3,A,90,(255,255,255),(200,40,120))
        sub(fr,li,lt); return fr
    if n=='react':
        fr=cl(KE,lt,0.04)
        if lt<1.0: actor(fr,'A14',540,2050,1600,A,0,lt,bobamp=0)
        elif lt<2.0: actor(fr,'MSU',540,1990,1180,A,0,lt,bobamp=0)
        else: actor(fr,'DI1',540,2350,1900,A,0,lt,bobamp=2)
        return fr
    if n=='bp':
        fr=cl(KE,lt); actor(fr,'BP',540,3050,2550,A,v,lt,bobamp=4); sweat(fr,740,520,lt,A); sub(fr,li,lt); return fr
    if n=='endcall':
        fr=cl(KE,lt); actor(fr,'BPc',540,3050,2550,A,0,lt,bobamp=0); sticker(fr,'bip',780,600,lt,0.1,A,70,(255,255,255),(40,40,40)); return fr
    if n=='silence':
        fr=cl(KE,lt,0.04+0.08*prog(lt,1.8,2.0) if lt>1.8 else 0.04); fr=night(fr,0.25)
        if lt<1.8: actor(fr,'BPc',540,3050,2550,A,0,lt,bobamp=0); drops2(fr,540,420,lt,A)
        else: actor(fr,'A14',540,2050,int(1600*(1+0.15*prog(lt,1.8,2.0))),A,0,lt,bobamp=0)
        k=prog(lt,2.2,1.4)
        if 0<k<1: ps(fr,leaf(),lerp(-100,1180,k),1500+60*math.sin(k*9),A,1.2,rot=k*360)
        return fr
    if n=='taistoi':
        fr=cl(KE,lt); actor(fr,'N14',540,2150,1650,A,0,lt,bobamp=8); sticker(fr,'TAIS-TOI !',540,480,lt,0.2,A,110,(255,255,255),(200,30,30)); return shake(fr,lt,0.2,dd,6)
    if n=='flyshot':
        fr=cl(KE,lt); actor(fr,'DI1',540,2350,1900,A,0,lt,bobamp=0); k=eo(prog(lt,0,0.9))
        ps(fr,fly(),lerp(950,548,k)+(0 if k>=1 else 40*math.sin(lt*20)),lerp(300,640,k),A,0.7); return fr
    if n=='a5':
        fr=cl(KE,lt); key='A5o' if v>0.15 else 'A5c'; actor(fr,key,540,2050,1650,A,0,lt,bobamp=3); redface(fr,560,560,lt,A) if li==IX['a_vdb'] else None
        sub(fr,li,lt); return shake(fr,lt,LEAD[li],0.5,10)
    if n=='loserhit':
        fr=cl(KE,lt); actor(fr,'BPc',540,3050,2550,A,0,lt,bobamp=0); k=eo(prog(lt,0,0.25)); sticker(fr,'LOSER !',540,int(lerp(-100,480,k)),lt,0.0,A,120,(255,255,255),(150,40,40)); return shake(fr,lt,0.2,0.6,14)
    if n=='mrun':
        fr=cl(KE,lt); actor(fr,'MRUN',540,1990,1100,A,0,lt,bobamp=4); blacksmoke(fr,980,1500,lt,A); sub(fr,li,lt); return fr
    if n=='run':
        fr=bgd(KE,lt,zoom=0.1); k=eo(prog(lt,0,1.6)); blacksmoke(fr,560,1250,lt,A); 
        actor(fr,'DI10c',lerp(1150,600,k),1880,900,A,0,lt,flip=True,bobamp=14); speed(fr,1300,1800,lt,A); return fr
    if n=='mef':
        fr=cl(KE,lt); actor(fr,'A20',540,2400,2100,A,0,lt,bobamp=0); return fr
    if n=='bj':
        fr=cl(KE,lt); actor(fr,'BJ',540,3050,2550,A,v,lt,bobamp=2); sub(fr,li,lt); return fr
    if n=='a20':
        fr=cl(KE,lt); actor(fr,'A20',540,2400,2100,A,0,lt,bobamp=0); sticker(fr,'Tchiiip !',540,520,lt,LEAD[li],A,110,(255,255,255),(150,40,40)); return fr
    if n=='aleave':
        fr=bgd(KE,lt,zoom=0.1); k=prog(lt,0,2.2); actor(fr,'ABK',lerp(600,640,k),int(lerp(1960,1650,k)),int(lerp(1100,620,k)),A,0,lt,bobamp=6); actor(fr,'BPc',260,1900,1050,A,0,lt,bobamp=0); return fr
    if n=='db':
        fr=cl(KE,lt); actor(fr,'DB',540,2150,1800,A,v,lt,bobamp=3); blacksmoke(fr,820,900,lt,A*0.7); sub(fr,li,lt); return fr
    if n=='door':
        fr=night(bgd(AT,lt,zoom=0.06),0.55); actor(fr,'A21c',540,2000,1550,A,0,lt,bobamp=0); return shake(fr,lt,0.15,0.5,14)
    if n=='a21':
        fr=night(bgd(AT,lt,zoom=0.06),0.55); actor(fr,'A21c',540,2000,1550,A,0,lt,bobamp=2); sub(fr,li,lt); return fr
    if n=='zoomA':
        z=1+0.5*eo(prog(lt,0,dd)); fr=night(bgd(AT,lt,zoom=0.06),0.55); actor(fr,'A21c',540,int(2000+ (z-1)*1500),int(1550*z),A,0,lt,bobamp=0)
        if 0.1<lt<0.35: fr=Image.blend(fr.convert('RGB'),Image.new('RGB',fr.size,(255,255,255)),0.6)
        return fr
    if n=='suite':
        fr=night(bgd(AT,lt,blur=10),0.55); ps(fr,txt('À suivre…',130,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.5)),1.0,dy=10,op=0.5); return fr
    if n in('fin','finb','finc','fin2'):
        fr=bg(lt); fin11(fr,lt,A,{'fin':0,'finb':1,'finc':2,'fin2':3}[n]); return fr
