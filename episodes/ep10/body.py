
def phone10(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.ellipse([230,250,370,390],fill=FONCE); check(d,300,320,40,(255,255,255),12); d.text((300,440),'Commande envoyée',font=font(FB,44),fill=FONCE,anchor='mm')
    d.rounded_rectangle([24,500,576,1060],radius=28,fill=(255,243,226),outline=ORANGE,width=5)
    if kind=='mimi': ls=[('Chez Bakary',FB),('3 brochettes',FB),('Livraison :',FM),('Atelier Awa Couture',FM)]
    else: ls=[('Chez Bakary',FB),('6 brochettes · 1 500 F',FB),('Cliente : Fatim',FB),('Boutique de crédit Fatim',FM),('Paiement à la livraison',FM)]
    for i,(l,f) in enumerate(ls): d.text((300,570+i*90),l,font=font(f,38),fill=ENCRE,anchor='mm')
    return S
@lru_cache(None)
def P10(kind): return phone_with(phone10(kind))
def bubbles(fr,lt,A,x,y,col):
    for i,(bx,by,r) in enumerate([(x,y,20),(x+40,y-80,30),(x+80,y-170,40)]):
        D=Image.new('RGBA',(r*2,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*2-1,r*2-1],fill=(255,255,255,235),outline=col,width=4); put(fr,D,bx,by,A)
def redface(fr,x,y,lt,A):
    k=prog(lt,0.2,1.0); L_=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(L_).ellipse([x-170,y-200,x+170,y+170],fill=(230,40,30,int(110*k))); fr.alpha_composite(L_.filter(ImageFilter.GaussianBlur(30))) if fr.mode=='RGBA' else fr.paste(L_.filter(ImageFilter.GaussianBlur(30)),(0,0),L_.filter(ImageFilter.GaussianBlur(30)))
    for sx in (-210,210):
        for i in range(4):
            kk=(lt*1.4+i/4)%1; r=int(25+kk*60); D=Image.new('RGBA',(r*2+20,r*2+20),(0,0,0,0)); ImageDraw.Draw(D).ellipse([10,10,r*2+9,r*2+9],fill=(255,255,255,int(170*(1-kk)*k))); put(fr,D.filter(ImageFilter.GaussianBlur(5)),x+sx+sx*0.4*kk,y-60-kk*260,A)
def deflate(fr,x,y,lt,A):
    k=prog(lt,0.3,1.4); h=heart_img().resize((max(20,int(200*(1-0.6*k))),max(18,int(180*(1-0.6*k)))),Image.LANCZOS); ps(fr,h,x,y+80*k,A*(1-0.4*k),1.0,rot=20*k)
CAB='D10'
def draw(n,lt,dd,li,A):
    v=talk(li,lt)
    if n=='titre':
        fr=bgd(ATEL,lt,blur=6); ps(fr,ICON.resize((220,220),Image.LANCZOS),540,620,A*eo(prog(lt,0,0.4)),0.5+0.5*back(prog(lt,0,0.5)))
        ps(fr,dpanel('Les Plans de Bakary',78),540,880,A*eo(prog(lt,0.2,0.4)),0.6+0.4*back(prog(lt,0.2,0.5))); pp(fr,'Épisode 10 · Le pari',lt,0.6,A,1040,52); return fr
    if n in('open','mphone'):
        fr=bgd(ATEL,lt); actor(fr,'MI',330,1900,1050,A,0,lt,bobamp=2); actor(fr,'AC',800,1950,1350,A,0,lt,bobamp=1); return fr
    if n=='pause':
        fr=bgd(ATEL,lt,blur=10); card(fr,'13h00 – Pause',lt,A); return fr
    if n in('app1','app2'):
        fr=bgd(ATEL if n=='app1' else CAB,lt,blur=8); k=eo(prog(lt,0,0.35)); ps(fr,P10('mimi' if n=='app1' else 'awa'),540,lerp(1300,1100,k),A,1.15,dy=30)
        pp(fr,'Mimi commande en cachette' if n=='app1' else 'Awa commande au nom de Fatim',lt,0.3,A,230,40,bg=(200,40,120),fg=(255,255,255)); return fr
    if n=='knock':
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'MEc',540,2150,1650,A,0,lt); sticker(fr,'Toc toc…',780,640,lt,0.2,A,80,(255,255,255),(90,70,50)); return fr
    if n=='s0':
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'MEo',540,2150,1650,A,0,lt); sub(fr,li,lt); return fr
    if n=='s2':
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'MS',540,MED['by'],MED['h'],A,v,lt); sub(fr,li,lt); return fr
    if n in('s1','s4'):
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'TA',540,2350,2100,A,v,lt); sub(fr,li,lt); return fr
    if n=='s3':
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'GR',540,2350,2100,A,v,lt); sticker(fr,'BEURK !',780,560,lt,0.2,A,110,(255,255,255),(110,170,50)); sub(fr,li,lt); return shake(fr,lt,0.1,0.5,12)
    if n=='back':
        fr=bgd(ATEL,lt); actor(fr,'MI',330,1900,1050,A,0,lt,bobamp=2); actor(fr,'TA',760,2000,1500,A,0,lt); return fr
    if n=='s5':
        fr=bgd(ATEL,lt,blur=BL,zoom=0.06); actor(fr,'AE',540,MED['by'],MED['h'],A,v,lt); sub(fr,li,lt); return fr
    if n=='cab':
        fr=bgd(CAB,lt); actor(fr,'FT1',470,1850,1000,A,0,lt,bobamp=2); k=eo(prog(lt,0,1.5)); actor(fr,'W1',lerp(1300,830,k),1950,1350,A,0,lt,flip=True,bobamp=0 if k>=1 else 8); return fr
    if n in('s6','take'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'W7',540,MED['by'],MED['h'],A,v,lt); sub(fr,li,lt) if n=='s6' else None; return fr
    if n in('s7','s30'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'FT1',540,MED['by'],MED['h'],A,v,lt); sub(fr,li,lt); return fr
    if n in('s8','s20'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'NX',540,MED['by'],MED['h'],A,v,lt); sub(fr,li,lt); return fr
    if n=='hide':
        fr=bgd(CAB,lt); actor(fr,'AK1',800,1950,1150,A,0,lt,bobamp=1); fr=night(fr,0.85); return fr
    if n in('s9','s10','s17','s34'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); k=eo(prog(lt,0,1.2)) if n=='s9' else 1; actor(fr,'BW',540,int(lerp(2250,2150,k)),int(lerp(1500,1700,k)),A,v,lt,bobamp=8)
        if n=='s17': ps(fr,BILL().resize((200,103)),760,1350,A,1.0,rot=-10)
        sub(fr,li,lt) if n!='s9' else None; return fr
    if n in('s11','s13'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'FT2',540,MED['by'],MED['h'],A,v,lt); big_hearts(fr,lt,0.0,A*0.8); sub(fr,li,lt); return fr
    if n in('s12','s22','s23','s31','s32'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'BQ',540,2150,1700,A,v,lt); sub(fr,li,lt); return fr
    if n=='bgo':
        fr=bgd(CAB,lt); k=eo(prog(lt,0,1.2)); actor(fr,'RB',lerp(540,-200,k),1950,1300,A,0,lt,bobamp=6); actor(fr,'FT2',820,1950,1250,A,0,lt); big_hearts(fr,lt,0,A*0.6); return fr
    if n in('s14','s15'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'FT3',540,MED['by'],MED['h'],A,v,lt)
        if n=='s15': bubbles(fr,lt,A,640,560,(200,40,120)); big_hearts(fr,lt,0.0,A*0.6)
        sub(fr,li,lt); return fr
    if n=='s16':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); fr=night(fr,0.85); actor(fr,'CR',540,2350,2050,A,v,lt); stars(fr,540,560,lt,A,120,6); sub(fr,li,lt); return fr
    if n=='ghost':
        fr=bgd(CAB,lt,blur=4,zoom=0.06+0.12*eo(prog(lt,0,0.4))); fr=night(fr,0.85); actor(fr,'AK2',540,2150,int(1700*(1+0.25*eo(prog(lt,0,0.4)))),A,0,lt,bobamp=0); return shake(fr,lt,0.2,1.0,8)
    if n in('s18','s19'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'B1',540,2100,1650,A,v,lt); big_hearts(fr,lt,0.0,A*0.6); sub(fr,li,lt); return fr
    if n=='swal':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); fr=night(fr,0.85); actor(fr,'AK2',540,2150,1700,A,0,lt); sticker(fr,'Gloups !',780,560,lt,0.1,A,90,(255,255,255),(110,170,50)); return fr
    if n=='s21':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'BP',540,2000,1450,A,v,lt); sweat(fr,720,560,lt,A); sub(fr,li,lt); return fr
    if n in('s24','s25'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'GR',540,2350,2100,A,v,lt); sub(fr,li,lt); return fr
    if n=='zap':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'B0',540,2100,1650,A,0,lt,bobamp=0)
        if lt>0.1: sticker(fr,'⚡'.replace('⚡','!!!'),540,420,lt,0.1,A,110,(255,255,255),(240,180,0))
        return shake(fr,lt,0.1,0.5,10)
    if n in('s26','s27','s28','s33'):
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'FT4',540,MED['by'],MED['h'],A,v,lt)
        if n=='s33': big_hearts(fr,lt,0.0,A*0.7)
        sub(fr,li,lt); return fr
    if n=='give':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'BQ',540,2150,1700,A,0,lt); k=prog(lt,0.1,0.8); ps(fr,BILL().resize((220,113)),lerp(700,1100,eo(k)),1300,A,1.0,rot=-10); return fr
    if n=='cricket':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); fr=night(fr,0.85); actor(fr,'AK2',540,2150,1700,A,0,lt); redface(fr,540,700,lt,A); return fr
    if n=='gather':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); fr=night(fr,0.85); actor(fr,'AK3',540,MED['by'],MED['h'],A,0,lt,bobamp=10); return shake(fr,lt,0,dd,6)
    if n=='s29':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); fr=night(fr,0.85); actor(fr,'AK4',560,MED['by'],MED['h'],A,0,lt,bobamp=4); sticker(fr,'Tchiiip !',540,520,lt,0.0,A,110,(255,255,255),(150,40,40)); return shake(fr,lt,0.1,0.4,8)
    if n=='leave':
        fr=bgd(CAB,lt); k=prog(lt,0,1.6); actor(fr,'W6',540,int(lerp(1950,1880,k)),int(lerp(1500,1250,k)),A,0,lt,bobamp=6); return fr
    if n=='bleave':
        fr=bgd(CAB,lt); k=prog(lt,0,1.6); actor(fr,'RB',540,int(lerp(1960,1880,k)),int(lerp(1400,1150,k)),A,0,lt,bobamp=6); actor(fr,'FT4',200,1950,1150,A,0,lt); return fr
    if n=='s35':
        fr=bgd(CAB,lt,blur=BL,zoom=0.06); actor(fr,'FT5',540,MED['by'],MED['h'],A,v,lt); deflate(fr,780,600,lt,A); sub(fr,li,lt); return fr
    if n=='suite':
        fr=bgd(CAB,lt,blur=10); ps(fr,txt('À suivre…',130,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.5)),1.0,dy=10,op=0.5); return fr
    if n=='fin':
        fr=bg(lt); k=prog(lt,0.1,0.5); ps(fr,ICON.resize((300,300),Image.LANCZOS),540,420+bob(lt,2.5,8),A*eo(k),0.4+0.6*back(k),dy=30)
        ps(fr,txt('Sounsouni',130,FONCE),540,690,A*eo(prog(lt,0.4,0.4)),0.8+0.2*back(prog(lt,0.4,0.5)),dy=8,op=0.25)
        pp(fr,'Chaque petit commerce a sa boutique',lt,0.9,A,830,40,bg=(255,255,255),fg=FONCE); pp(fr,'Commandes à toute heure',lt,1.5,A,935,42)
        ps(fr,P10('awa'),300,1450,A*eo(prog(lt,2.2,0.4)),0.58*(0.6+0.4*back(prog(lt,2.2,0.5))),rot=-5,dy=24)
        for i,kd in enumerate(['android','iphone']):
            kk=prog(lt,7.5+i*0.8,0.4); ps(fr,badge(kd),790,1300+i*190,A*eo(kk),0.8*(0.5+0.5*back(kk)))
        ps(fr,txt('sounsouni.pro',96,FONCE),540,1810,A*eo(prog(lt,2.8,0.4)),dy=6,op=0.2)
        return fr
