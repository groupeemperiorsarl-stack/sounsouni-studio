
# ---- ép.14 v2 : mise en scène corrigée (sol commun, profondeur, regards, chute pas à pas)
GROUND=1900   # ligne du sol, premier rang
BACK=1560     # ligne du sol, arrière-plan
HEADF={'AWW1':0.453,'AWW2':0.393,'AWW3':0.432,'AWB1':0.441,'AWB2':0.403,'AWB3':0.421}
def walkframe(fr,key,x,by,h,A,flip=False):
    im=PH(key,h)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    hf=HEADF.get(key,0.5); hf=1-hf if flip else hf
    cx=x-hf*im.width+im.width/2; ps(fr,im,cx,by-im.height/2,A,1.0,dy=14,op=0.28)
def regal_walk(fr,x,by,h,lt,A,flip=False,moving=True,back=False,rate=3.2):
    seq=(['AWB1','AWB3','AWB2','AWB3'] if back else ['AWW1','AWW3','AWW2','AWW3'])
    key=seq[int(lt*rate)%4] if moving else seq[1]
    walkframe(fr,key,x,by,h,A,flip)
def kwide(fr,lt,A,fatim=True,awa=True):
    # arrière-plan : voiture, Modibo sur le banc, Awa à sa porte
    bgcar(fr,lt,A)
    if awa: actor(fr,'A21',115,BACK,560,A,0,lt,bobamp=0)
    actor(fr,'MB',1000,BACK+40,430,A,0,lt,bobamp=0)
    # premier rang, tous les pieds sur la même ligne de sol
    actor(fr,'BRc',340,GROUND,860,A,0,lt,bobamp=1)
    actor(fr,'DIW',590,GROUND+10,1120,A,0,lt,bobamp=0)
    if fatim: actor(fr,'FT2',830,GROUND+20,980,A,0,lt,bobamp=1,flip=True)
def bgcar(fr,lt,A,x=720,y=1330,s=0.1):
    c=PH('CAR',int(1665*s)); c2=ImageEnhance.Brightness(c).enhance(0.7); ps(fr,c2,x,y,A*0.95,1.0,dy=4,op=0.1)
def board(fr,A,x=640,y=GROUND+5,w=420):
    ps(fr,HOVER(w),x,y-int(w*0.15),A,1.0,dy=8,op=0.35)
def cu(fr,key,x,lt,A,v=0,h=2700,flip=False,bob=3,top=330):
    # gros plan : sommet de la tête à « top », cadré jusqu'aux cuisses
    actor(fr,key,x,top+h,h,A,v,lt,flip=flip,bobamp=bob)
def ots_awa(fr,lt,A):
    # Awa de dos, floue, au premier plan à droite (contre-champ)
    im=PH('AWB3',2600).filter(ImageFilter.GaussianBlur(6)); ps(fr,im,1010,1950,A,1.0,dy=0,op=0)
def draw(n,lt,dd,li,A):
    v=talk(li,lt)
    if n=='open':
        fr=bgd(K,lt,zoom=0.1); kwide(fr,lt,A); return fr
    if n in('ft1','ft2','ft3','ft4'):
        fr=cl(K,lt); key=n.upper()
        cu(fr,key,430,lt,A,v,2900)
        if n=='ft3': ps(fr,CARD(),250,1450,A*eo(prog(lt,0.6,0.4)),0.8,rot=-12)
        if li is not None and li in(IX['f04'],IX['f05'],IX['f06'],IX['f07'],IX['f08']): ots_awa(fr,lt,A)
        sub(fr,li,lt); return fr
    if n=='laughF':
        fr=cl(K,lt); cu(fr,'FT2',430,lt,A,0,2900,bob=10); sticker(fr,'Ha ha ha !',700,520,lt,0.1,A,90,(255,255,255),(200,40,120)); return fr
    if n=='awaeyes':
        z=1+0.3*eo(prog(lt,0,dd)); fr=bgd(K,lt,zoom=0.08); actor(fr,'A20',650,int(2400+(z-1)*1500),int(2100*z),A,0,lt,bobamp=0)
        sticker(fr,'!!',300,560,lt,0.3,A,100,(255,255,255),(240,180,0)); return fr
    if n=='a20' :
        fr=cl(K,lt); actor(fr,'A20',650,2400,2100,A,v,lt,bobamp=0); sub(fr,li,lt); return fr
    if n=='shakeA':
        fr=cl(K,lt,0.15); actor(fr,'A20',650,2600,2400,A,0,lt,bobamp=0); return shake(fr,lt,0,dd,8)
    if n=='fleave':
        fr=bgd(K,lt,zoom=0.1); bgcar(fr,lt,A); actor(fr,'MB',1000,BACK+40,430,A,0,lt,bobamp=0); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); actor(fr,'DIW',590,GROUND+10,1120,A,0,lt,bobamp=0)
        k=prog(lt,0,dd); actor(fr,'FT2',lerp(850,1300,k),GROUND+20,980,A,0,lt*3,bobamp=8); sticker(fr,'Rappelle-moi !',540,480,lt,0.2,A,70,(255,255,255),(200,40,120)); return fr
    if n=='slam':
        fr=bgd(K,lt,zoom=0.1); kwide(fr,lt,A,fatim=False,awa=False); sticker(fr,'BAM !',985,1250,lt,0.1,A,110,(255,255,255),(200,30,30)); return shake(fr,lt,0.1,0.8,18)
    if n=='mou':
        fr=cl(K,lt); cu(fr,'MOU',600,lt,A,v,2800); sub(fr,li,lt); return fr
    if n in('sey','seyin'):
        fr=cl(AT if li in(IX['s06'],IX['s07']) or n=='seyin' else K,lt); cu(fr,'SEY',560,lt,A,v,2700)
        if n=='seyin': sticker(fr,'Pouet pouet !',540,480,lt,0.0,A,80,(255,255,255),(30,120,60))
        if li is not None: sub(fr,li,lt)
        return fr
    if n=='turn':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'MB',1000,BACK+40,430,A,0,lt,bobamp=0); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); actor(fr,'SEY',620,GROUND+10,1000,A,0,lt,bobamp=0)
        actor(fr,'DEAT',880,GROUND+20,1150,A,0,lt,bobamp=0); ps(fr,BOXP(1,300),800,1660,A,1.0); sticker(fr,'?',540,480,lt,0.1,A,110,(255,255,255),(40,40,40)); return fr
    if n=='motoleave':
        fr=bgd(K,lt,zoom=0.08); k=eo(prog(lt,0,1.4)); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); actor(fr,'SEY',lerp(650,1350,k),GROUND+10,1050,A,0,lt,bobamp=6,flip=True); ps(fr,BOXP(1,220),lerp(560,1260,k),GROUND-420,A,1.0); speed(fr,1300,1800,lt,A); return fr
    if n=='moto':
        fr=bgd(K,lt,zoom=0.08); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); k=eo(prog(lt,0,1.2)); actor(fr,'SEY',lerp(1300,700,k),GROUND+10,1050,A,0,lt,bobamp=6 if k<1 else 1)
        if k<1: speed(fr,1300,1800,lt,A)
        ps(fr,BOXP(24,300),lerp(1180,580,k),GROUND-420,A,1.0); sticker(fr,'Pouet pouet !',400,520,lt,0.0,A,80,(255,255,255),(30,120,60)); return fr
    if n=='hover':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'MB',1000,BACK+40,430,A,0,lt,bobamp=0); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=1); k=eo(prog(lt,0,1.8))
        actor(fr,'MOUW',lerp(1300,700,k),GROUND+20,1150,A,0,lt,bobamp=2)
        if k<1: speed(fr,1300,1800,lt,A)
        sticker(fr,'Vzzzz…',600,480,lt,0.2,A,80,(255,255,255),(60,120,200)); return fr
    if n=='jump':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'MB',1000,BACK+40,430,A,0,lt,bobamp=0); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); board(fr,A)
        k=prog(lt,0,0.7); actor(fr,'MOU',lerp(660,880,k),int(GROUND+20-260*math.sin(math.pi*k)),1050,A,0,lt,bobamp=0)
        sticker(fr,'Hop !',880,560,lt,0.1,A,80,(255,255,255),(60,120,200)); return fr
    if n=='tactac':
        fr=bgd(K,lt,zoom=0.1); kwide(fr,lt,A,fatim=False,awa=False); actor(fr,'MOU',880,GROUND+20,1050,A,0,lt,bobamp=0); board(fr,A)
        sticker(fr,'Tac-tac-tac-tac !',540,480,lt,0.1,A,80,(255,255,255),(200,40,40)); return fr
    if n=='awafast':
        # Awa traverse la rue vers le kiosque : démarche droite, pas réguliers, allure de reine
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); board(fr,A)
        k=prog(lt,0,dd); regal_walk(fr,lerp(1220,880,k),GROUND+20,int(lerp(1000,1120,k)),lt,A,flip=True,rate=3.6); return fr
    if n=='step':
        # 1) l'hoverboard au sol, bien visible ; 2) les pieds d'Awa arrivent ; 3) un pied se pose dessus
        fr=bgd(K,lt,zoom=0.35); fr=fr.filter(ImageFilter.GaussianBlur(2)); ps(fr,HOVER(860),520,1620,A,1.0,dy=14,op=0.35)
        k=prog(lt,0,1.4); seq=['AWW1','AWW3','AWW2','AWW3']; key=seq[int(lt*3.6)%4] if k<1 else 'AWW2'
        im=PH(key,3400).transpose(Image.FLIP_LEFT_RIGHT); legs=im.crop((0,int(im.height*0.62),im.width,im.height))
        x=lerp(1250,640,eo(k)); ps(fr,legs,x,1620-legs.height/2+60,A,1.0,dy=10,op=0.25)
        if lt>1.45: sticker(fr,'?!',540,560,lt,1.45,A,110,(255,255,255),(200,30,30))
        return fr
    if n=='slip':
        fr=cl(K,lt,0.06); k=eo(prog(lt,0.1,1.6)); r=-28*k
        im=PH('SLIP',1800).rotate(r,expand=True,resample=Image.BICUBIC); ps(fr,im,lerp(540,470,k),2050-im.height/2+60,A,1.0,dy=12,op=0.25)
        sticker(fr,'Ralenti…',540,360,lt,0.2,A,70,(255,255,255),(60,60,60))
        if lt>1.0: sticker(fr,'Aaaah !',820,620,lt,1.0,A,90,(255,255,255),(200,30,30))
        return fr
    if n=='leap':
        fr=bgd(K,lt,zoom=0.1); k=eo(prog(lt,0,1.0)); actor(fr,'BM',lerp(200,700,k),int(GROUND+10-200*math.sin(math.pi*k)),1150,A,0,lt,bobamp=0)
        speed(fr,1300,1800,lt,A); sticker(fr,'Bakary bondit !',540,480,lt,0.0,A,80,(255,255,255),(32,72,200)); return fr
    if n=='awaleave':
        fr=bgd(K,lt,zoom=0.1); actor(fr,'BRc',330,GROUND,860,A,0,lt,bobamp=0); k=prog(lt,0,dd*0.9)
        regal_walk(fr,lerp(640,900,k),int(lerp(GROUND+20,BACK+20,k)),int(lerp(1120,640,k)),lt,A,back=True,moving=k<1,rate=4.4); return fr
    if n=='look':
        fr=cl(K,lt,0.1); cu(fr,'BH',540,lt,A,0,2700,bob=0); return fr
    return draw_v1(n,lt,dd,li,A)
