MED=dict(by=3050,h=2550); BL=3
@lru_cache(None)
def sign2(txt1,txt2,col=(120,72,36),c2=(255,236,190),c3=(255,214,140)):
    p=Image.new('RGBA',(760,230),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([0,0,759,229],radius=24,fill=col,outline=tuple(max(0,c-40) for c in col),width=8)
    d.text((380,82),txt1,font=font(FB,78),fill=c2,anchor='mm'); d.text((380,170),txt2,font=font(FM,40),fill=c3,anchor='mm'); return p
@lru_cache(None)
def CHEEK(key,h,fx,fy,fw):
    im=PH(key,h).copy(); w,hh=im.size; L_=Image.new('RGBA',(w,hh),(0,0,0,0)); d=ImageDraw.Draw(L_)
    cx,cy,r=fx*w,fy*hh,fw*w
    for i in range(12): rr=r*(1-i/12); d.ellipse([cx-rr,cy-rr*0.7,cx+rr,cy+rr*0.7],fill=(235,40,40,22))
    a=Image.composite(L_.getchannel('A'),Image.new('L',L_.size,0),im.getchannel('A').point(lambda p:255 if p>200 else 0)); L_.putalpha(a); im.alpha_composite(L_); return im
CK={'N5':(0.70,0.112,0.09),'B6c':(0.66,0.215,0.12)}
def actor3(fr,key,cx,by,h,A=1.0,v=0.0,t=0,flip=False,bobamp=6,cheek=False):
    if not cheek: return actor(fr,key,cx,by,h,A,v,t,flip=flip,bobamp=bobamp)
    im=CHEEK(key,h,*CK[key]); im=mouthify(im,key,v); sy=1+0.012*v; im2=im.resize((im.width,int(im.height*sy))) if v>0.05 else im
    ps(fr,im2,cx,by-im2.height/2+bobamp*math.sin(t*2.2),A,dy=14,op=0.28)
def shake(fr,lt,t0,dur,amp=26):
    k=(lt-t0)/dur
    if not 0<=k<=1: return fr
    a=amp*(1-k); dx=int(a*math.sin(lt*95)); dy=int(a*math.cos(lt*77)); out=Image.new('RGB',fr.size); out.paste(fr,(dx,dy)); return out
def speed(fr,y0,y1,lt,A):
    L_=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L_)
    for i in range(14):
        y=y0+(i*97)%(y1-y0); x=(i*211+lt*2400)%(W+600)-300; d.rounded_rectangle([x,y,x+380,y+10],radius=5,fill=(255,255,255,int(150*A)))
    fr.paste(L_,(0,0),L_)
def dust(fr,x,y,lt,A):
    for i in range(6):
        k=(lt*1.4+i/6)%1; r=int(30+k*70); D=Image.new('RGBA',(r*2,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*2-1,r*2-1],fill=(220,180,130,int(140*(1-k))))
        put(fr,D,x+i*40+k*120,y-k*40,A)
def big_hearts(fr,lt,t0,A):
    k=prog(lt,t0,1.2)
    if k<=0: return
    for i in range(10):
        a=i*0.628; rr=60+k*520; put(fr,heart_img(),540+rr*math.cos(a),980+rr*math.sin(a)*0.9,A*(1-k*0.7),1.2+1.8*k)
def phone3(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    d.text((30,232),'Restauration · Ma boutique',font=font(FM,30),fill=(110,130,100)); d.text((30,272),'Chez Bakary',font=font(FB,50),fill=ENCRE)
    if kind=='shop':
        d.rounded_rectangle([24,380,576,980],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.text((300,450),'Thé · Café',font=font(FB,54),fill=FONCE,anchor='mm')
        for i,(n_,p_) in enumerate([('Thé à la menthe','250 F'),('Café Touba','300 F'),('Café au lait','350 F')]):
            y=540+i*90; d.text((60,y),n_,font=font(FM,36),fill=ENCRE); d.text((540,y),p_,font=font(FB,36),fill=FONCE,anchor='ra')
        d.rounded_rectangle([50,850,550,940],radius=45,fill=ORANGE); d.text((300,895),'Boutique ouverte gratuitement !',font=font(FB,30),fill=(255,255,255),anchor='mm')
    elif kind in('o1','o2'):
        d.rounded_rectangle([24,380,576,1000],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,450),'Nouvelle commande !',font=font(FB,46),fill=(200,100,10),anchor='mm')
        if kind=='o1': l1,l2,l3='2 cafés','600 FCFA','Badalabougou'
        else: l1,l2,l3='10 thés à la menthe','2 500 FCFA','Cliente : Awa Couture'
        d.text((300,560),l1,font=font(FB,48),fill=ENCRE,anchor='mm'); d.text((300,640),l2,font=font(FB,44),fill=FONCE,anchor='mm')
        d.rounded_rectangle([60,720,540,800],radius=40,fill=(32,72,200) if kind=='o1' else (230,120,20)); d.text((300,760),l3,font=font(FB,34),fill=(255,255,255),anchor='mm')
        d.rounded_rectangle([60,850,540,940],radius=45,fill=VERT); d.text((300,895),'Accepter la commande',font=font(FB,34),fill=(255,255,255),anchor='mm')
    elif kind=='note':
        d.rounded_rectangle([24,380,576,960],radius=34,fill=(232,246,222),outline=FONCE,width=6)
        d.ellipse([230,420,370,560],fill=FONCE); check(d,300,490,34,(255,255,255),12)
        d.text((300,620),'Commande livrée !',font=font(FB,46),fill=FONCE,anchor='mm'); d.text((300,700),'Note de la cliente',font=font(FM,34),fill=ENCRE,anchor='mm')
        for i in range(5):
            cx_=140+i*80; d.regular_polygon((cx_,800,34),5,rotation=-18,fill=(255,180,30))
        d.text((300,900),'« Livraison très rapide ! »',font=font(FM,32),fill=(90,110,80),anchor='mm')
    elif kind=='many':
        d.rounded_rectangle([24,380,576,1100],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,450),'12 nouvelles commandes !',font=font(FB,42),fill=(200,100,10),anchor='mm')
        for i,q in enumerate(['Kalaban','Hippodrome','Djicoroni','Kati']):
            y=540+i*120; d.rounded_rectangle([60,y,540,y+90],radius=30,fill=(255,255,255)); d.text((90,y+45),q,font=font(FB,38),fill=ENCRE,anchor='lm'); d.text((520,y+45),'+3',font=font(FB,38),fill=FONCE,anchor='rm')
    return S
@lru_cache(None)
def P3(kind): return phone_with(phone3(kind))
def flybills(fr,lt,t0,tx,ty,A):
    for i in range(5):
        k=prog(lt,t0+i*0.12,0.5)
        if 0<k<1: ps(fr,bill(),lerp(1250,tx,eo(k)),lerp(800+i*90,ty,eo(k))-math.sin(k*3.14)*200,A*(1-k*0.3),0.55,rot=lerp(40,-15,k)+i*7)

def smoke(fr,x,y,lt,A,amt=1.0,col=(120,200,40)):
    for i in range(int(8*amt)+3):
        k=(lt*0.5+i/9)%1; r=int(45+k*150*amt); D=Image.new('RGBA',(r*2+60,r*2+60),(0,0,0,0)); ImageDraw.Draw(D).ellipse([30,30,r*2+29,r*2+29],fill=col+(int(185*(1-k)*min(1,amt+0.3)),))
        put(fr,D.filter(ImageFilter.GaussianBlur(8)),x+60*math.sin(i*1.7+lt)+i*8,y-k*700*min(1.3,amt+0.2),A)
    L_=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L_)
    for i in range(3+int(3*amt)):
        k=(lt*0.6+i/6)%1; bx=x-140+i*70; by=y-k*650*min(1.4,amt+0.3)
        pts=[(bx+28*math.sin(t*0.9+lt*5+i),by-t*22) for t in range(16)]
        d.line(pts,fill=(70,160,20,int(255*(1-k))),width=16,joint='curve'); d.line(pts,fill=(170,240,90,int(255*(1-k))),width=7,joint='curve')
    fr.paste(L_,(0,0),L_)

def mud(fr,x,y,A):
    for dx,dy,r in [(-60,0,26),(-20,12,18),(40,-4,24),(80,10,16)]:
        D=Image.new('RGBA',(r*4,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*4-1,r*2-1],fill=(110,75,40,220)); put(fr,D,x+dx,y+dy,A)
@lru_cache(None)
def shoe():
    p=Image.new('RGBA',(260,130),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([10,40,250,120],radius=40,fill=(240,240,240)); d.rounded_rectangle([10,95,250,125],radius=14,fill=(230,120,40)); d.polygon([(30,40),(120,10),(170,40)],fill=(230,120,40))
    for x,y,r in [(60,105,14),(140,100,18),(200,110,12),(100,70,10)]: d.ellipse([x-r,y-r,x+r,y+r],fill=(110,75,40))
    return p
@lru_cache(None)
def fly():
    p=Image.new('RGBA',(70,50),(0,0,0,0)); d=ImageDraw.Draw(p); d.ellipse([20,18,50,40],fill=(30,30,30)); d.ellipse([8,4,32,22],fill=(200,220,240,180)); d.ellipse([38,4,62,22],fill=(200,220,240,180))
    d.line([(26,40),(20,48)],fill=(30,30,30),width=3); d.line([(44,40),(50,48)],fill=(30,30,30),width=3); return p.rotate(180)
def birds(fr,x,y,lt,A):
    for i in range(4):
        a=lt*4+i*1.57; D=Image.new('RGBA',(60,40),(0,0,0,0)); d=ImageDraw.Draw(D); d.arc([0,0,30,30],200,340,fill=(255,220,60),width=6); d.arc([28,0,58,30],200,340,fill=(255,220,60),width=6)
        put(fr,D,x+150*math.cos(a),y+40*math.sin(a),A)
def pink(fr,x,y,lt,A,big=1.0):
    for i in range(10):
        k=(lt*0.9+i/10)%1; r=int((50+k*220)*big); D=Image.new('RGBA',(r*2+60,r*2+60),(0,0,0,0)); ImageDraw.Draw(D).ellipse([30,30,r*2+29,r*2+29],fill=(255,150,200,int(120*(1-k))))
        put(fr,D.filter(ImageFilter.GaussianBlur(12)),x-k*520*big+20*math.sin(i),y+30*math.sin(i*2.1),A)
def phone4(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='search':
        d.rounded_rectangle([30,240,570,320],radius=40,fill=(240,240,240)); d.text((70,280),'Recherche : Modibo',font=font(FM,34),fill=ENCRE,anchor='lm')
        d.ellipse([230,440,370,580],outline=(200,200,200),width=10); d.line([(345,555),(400,610)],fill=(200,200,200),width=14)
        d.text((300,690),'Aucune boutique',font=font(FB,46),fill=(200,60,40),anchor='mm'); d.text((300,750),'trouvée',font=font(FB,46),fill=(200,60,40),anchor='mm')
    else:
        d.text((30,232),'Beauté · Parfums & encens',font=font(FM,30),fill=(110,130,100)); d.text((30,272),'Djéné Senteurs',font=font(FB,50),fill=ENCRE)
        d.rounded_rectangle([30,350,400,410],radius=30,fill=(222,242,200)); check(d,62,380,16,FONCE,5); d.text((90,358),'Vendeur vérifié',font=font(FB,32),fill=FONCE)
        if kind=='shop':
            for i,(n_,p_) in enumerate([('Parfum Fleur de Bamako','4 000 F'),('Encens thiouraye','1 500 F'),('Brûle-parfum en terre','2 000 F')]):
                y=470+i*110; d.rounded_rectangle([30,y,570,y+90],radius=24,fill=(250,244,228)); d.text((55,y+45),n_,font=font(FM,30),fill=ENCRE,anchor='lm'); d.text((545,y+45),p_,font=font(FB,30),fill=FONCE,anchor='rm')
            d.text((300,880),'★★★★★  4,9 · 230 avis',font=font(FB,34),fill=(230,150,20),anchor='mm')
        else:
            d.rounded_rectangle([24,450,576,1050],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
            d.text((300,510),'Nouveauté !',font=font(FB,48),fill=(200,100,10),anchor='mm')
            d.text((300,600),'Encens',font=font(FB,44),fill=ENCRE,anchor='mm'); d.text((300,660),'« Adieu les mauvaises',font=font(FB,38),fill=ENCRE,anchor='mm'); d.text((300,710),'odeurs »',font=font(FB,38),fill=ENCRE,anchor='mm')
            d.text((300,800),'2 500 FCFA',font=font(FB,50),fill=FONCE,anchor='mm')
            d.rounded_rectangle([90,880,510,960],radius=40,fill=(200,60,40)); d.text((300,920),'18 vendus aujourd\'hui',font=font(FB,32),fill=(255,255,255),anchor='mm')
    return S
@lru_cache(None)
def P4(kind): return phone_with(phone4(kind))
@lru_cache(None)
def FOOT():
    im=Image.open(HD+'M6.png').convert('RGBA'); s_=4200/im.height; im=im.resize((int(im.width*s_),4200),Image.LANCZOS)
    cx,cy=int(0.58*im.width),int(0.61*im.height); return im.crop((cx-650,cy-1100,cx+650,cy+1100))
SIGN=lambda: sign2('Djéné Senteurs','Parfums · Encens',(20,140,140),(255,255,255),(255,214,170))

def starpts(cx,cy,r):
    return [(cx+(r if i%2==0 else r*0.45)*math.sin(i*math.pi/5),cy-(r if i%2==0 else r*0.45)*math.cos(i*math.pi/5)) for i in range(10)]
def starrow(d,cx,cy,r,n=5,col=(240,170,20)):
    for i in range(n): d.polygon(starpts(cx+(i-(n-1)/2)*r*2.2,cy,r),fill=col)
@lru_cache(None)
def STAR(r=50):
    p=Image.new('RGBA',(r*2+8,r*2+8),(0,0,0,0)); d=ImageDraw.Draw(p); d.polygon(starpts(r+4,r+4,r+3),fill=(160,100,0)); d.polygon(starpts(r+4,r+4,r),fill=(255,205,40)); return p
@lru_cache(None)
def STARS5():
    p=Image.new('RGBA',(560,110),(0,0,0,0)); d=ImageDraw.Draw(p); starrow(d,280,55,46); return p
KSIGN=lambda: sign2('Chez Bakary','Thé · Café · Petit détail')
def phone5(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='order':
        d.text((30,232),'Tenues · Couture',font=font(FM,30),fill=(110,130,100)); d.text((30,272),'Awa Couture',font=font(FB,50),fill=ENCRE)
        d.rounded_rectangle([24,370,576,900],radius=34,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,430),'Commande en cours',font=font(FB,42),fill=(200,100,10),anchor='mm')
        d.text((300,540),'15 tenues',font=font(FB,60),fill=ENCRE,anchor='mm'); d.text((300,610),'de mariage',font=font(FB,46),fill=ENCRE,anchor='mm')
        d.line([(80,680),(520,680)],fill=(230,210,180),width=3); d.text((300,760),'Cliente : Tantie Kadi',font=font(FB,38),fill=FONCE,anchor='mm')
    else:
        d.text((30,232),'Thé · Café',font=font(FM,30),fill=(110,130,100)); d.text((30,272),'Chez Bakary',font=font(FB,50),fill=ENCRE)
        starrow(d,300,440,40); d.text((300,540),'4,9',font=font(FB,90),fill=ENCRE,anchor='mm')
        d.text((300,630),'132 avis',font=font(FB,42),fill=(110,130,100),anchor='mm')
        d.rounded_rectangle([30,700,570,900],radius=28,fill=(240,248,232)); d.text((300,760),'« Le meilleur thé',font=font(FB,38),fill=FONCE,anchor='mm'); d.text((300,820),'de Djélibougou »',font=font(FB,38),fill=FONCE,anchor='mm')
        d.text((300,960),'— Tantie Kadi',font=font(FM,32),fill=ENCRE,anchor='mm'); starrow(d,300,1020,18)
    return S
@lru_cache(None)
def P5(kind): return phone_with(phone5(kind))
def waves(fr,x,y,lt,A):
    L_=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L_)
    for i in range(3):
        k=(lt*1.5+i/3)%1; r=int(60+k*160); d.arc([x-r,y-r,x+r,y+r],-60,60,fill=(255,255,255,int(255*(1-k))),width=10); d.arc([x-r,y-r,x+r,y+r],120,240,fill=(255,255,255,int(255*(1-k))),width=10)
    fr.paste(L_,(0,0),L_)
def fabrics(fr,lt,t0,A):
    # vraies photos de bazin : doré, vert, orange
    for i,k in enumerate(('F1','F2','F3')):
        kk=prog(lt,t0+i*0.35,0.4)
        if kk<=0: continue
        ps(fr,PH(k,380),810,800+i*360,A*eo(kk),0.5+0.5*back(kk),rot=(-6,4,-3)[i],dy=18)

def shadow(fr,lt,A):
    k=eo(prog(lt,0,1.6)); D=Image.new('RGBA',(900,1500),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,899,1499],fill=(0,0,0,int(140*A)))
    D=D.filter(ImageFilter.GaussianBlur(40)); fr.paste(D,(int(lerp(1200,250,k)),300),D)
def stars_fade(fr,cx,cy,lt,A,t0,dur):
    n=6; kk=prog(lt,t0,dur)
    for i in range(n):
        if kk*n>i+0.5: continue
        a=lt*0.8+i*6.283/n; ps(fr,STAR(45),cx+190*math.cos(a),cy+70*math.sin(a),A,0.9+0.15*math.sin(lt*6+i))

def phone6(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='search':
        d.text((30,230),'Restauration · Thé & Café',font=font(FB,34),fill=ENCRE); d.rounded_rectangle([30,285,570,345],radius=30,fill=(240,240,240)); d.text((60,315),'Trier par : meilleures notes',font=font(FM,28),fill=FONCE,anchor='lm')
        d.rounded_rectangle([24,380,576,620],radius=28,fill=(240,248,232),outline=FONCE,width=5); d.text((50,420),'1. Chez Bakary',font=font(FB,42),fill=ENCRE); starrow(d,190,500,22); d.text((330,500),'4,9 · 132 avis',font=font(FB,28),fill=FONCE,anchor='lm')
        d.text((50,570),'« Le meilleur thé de Djélibougou »',font=font(FM,26),fill=ENCRE,anchor='lm')
        for i in range(2): y=650+i*130; d.rounded_rectangle([24,y,576,y+110],radius=24,fill=(246,246,246)); d.text((50,y+55),f'{i+2}. ' + ('Thé du Marché' if i==0 else 'Café Express'),font=font(FM,32),fill=(120,120,120),anchor='lm')
    elif kind=='sent':
        d.ellipse([230,260,370,400],fill=FONCE); check(d,300,330,40,(255,255,255),12); d.text((300,450),'Commande envoyée',font=font(FB,44),fill=FONCE,anchor='mm')
        d.rounded_rectangle([24,510,576,960],radius=28,fill=(255,243,226),outline=ORANGE,width=5)
        for i,l in enumerate(['3 thermos de café','3 thermos de thé','Konaté Import-Export','ACI 2000','Dans 30 minutes']): d.text((300,575+i*80),l,font=font(FB if i<2 else FM,36),fill=ENCRE,anchor='mm')
    elif kind=='neworder':
        d.text((30,230),'Chez Bakary',font=font(FB,46),fill=ENCRE); d.rounded_rectangle([24,300,576,1000],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,360),'Nouvelle commande !',font=font(FB,44),fill=(200,100,10),anchor='mm')
        for i,l in enumerate(['3 thermos de café','3 thermos de thé']): d.text((300,460+i*70),l,font=font(FB,38),fill=ENCRE,anchor='mm')
        for i,l in enumerate(['Client : Karim Konaté','Konaté Import-Export','ACI 2000']): d.text((300,640+i*62),l,font=font(FM,32),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([110,880,490,960],radius=40,fill=FONCE); d.text((300,920),'Accepter',font=font(FB,38),fill=(255,255,255),anchor='mm')
    elif kind=='done':
        d.ellipse([230,260,370,400],fill=FONCE); check(d,300,330,40,(255,255,255),12); d.text((300,450),'Commande livrée',font=font(FB,44),fill=FONCE,anchor='mm')
        d.text((300,560),'Karim vous a laissé',font=font(FM,34),fill=ENCRE,anchor='mm'); starrow(d,300,640,34); d.text((300,740),'« Service rapide »',font=font(FB,40),fill=FONCE,anchor='mm')
    elif kind=='notif':
        d.text((30,230),'Chez Bakary',font=font(FB,46),fill=ENCRE); d.rounded_rectangle([24,300,576,1000],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,365),'Nouvelle commande !',font=font(FB,44),fill=(200,100,10),anchor='mm')
        for i,l in enumerate(['3 thermos de café','3 thermos de thé']): d.text((300,470+i*70),l,font=font(FB,40),fill=ENCRE,anchor='mm')
        for i,l in enumerate(['Client : Karim','Konaté Import-Export','ACI 2000']): d.text((300,650+i*65),l,font=font(FM,34),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([110,880,490,960],radius=40,fill=FONCE); d.text((300,920),'Accepter',font=font(FB,36),fill=(255,255,255),anchor='mm')
    else:
        d.text((30,230),'Chez Bakary',font=font(FB,46),fill=ENCRE); d.rounded_rectangle([24,300,576,1060],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,355),'Nouvelle commande !',font=font(FB,42),fill=(200,100,10),anchor='mm'); d.text((300,450),'2 cappuccinos à la crème',font=font(FB,34),fill=ENCRE,anchor='mm')
        for i,l in enumerate(['Client : Karim','Vendredi 21h','Résidence Konaté, ACI 2000']): d.text((300,540+i*65),l,font=font(FM,32),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([50,760,550,1000],radius=24,fill=(255,255,255)); d.text((300,810),'Note du client :',font=font(FM,28),fill=(120,120,120),anchor='mm')
        d.text((300,880),'« Pour moi et ma',font=font(FB,36),fill=(200,40,80),anchor='mm'); d.text((300,935),'chérie Fanta »',font=font(FB,36),fill=(200,40,80),anchor='mm')
    return S
@lru_cache(None)
def FINGER():
    p=Image.new('RGBA',(160,260),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([50,0,110,170],radius=30,fill=(150,95,60)); d.rounded_rectangle([20,110,150,260],radius=50,fill=(150,95,60)); d.ellipse([58,8,102,50],fill=(220,180,160)); return p
@lru_cache(None)
def P6(kind): return phone_with(phone6(kind))
@lru_cache(None)
def CARD():
    p=Image.new('RGBA',(820,480),(0,0,0,0)); d=ImageDraw.Draw(p); d.rounded_rectangle([0,0,819,479],radius=30,fill=(250,248,240),outline=(200,170,80),width=8)
    d.rectangle([0,0,40,479],fill=(30,45,90)); d.text((440,150),'Karim Konaté',font=font(FB,64),fill=(30,45,90),anchor='mm'); d.text((440,240),'Directeur général',font=font(FB,44),fill=(170,130,40),anchor='mm')
    d.line([(160,300),(720,300)],fill=(200,170,80),width=3); d.text((440,360),'Konaté Import-Export',font=font(FM,38),fill=ENCRE,anchor='mm'); d.text((440,420),'Bamako',font=font(FM,32),fill=(120,120,120),anchor='mm'); return p
def bills(fr,lt,A):
    for i in range(8):
        a=lt*2+i*0.785; p=Image.new('RGBA',(150,80),(0,0,0,0)); q=ImageDraw.Draw(p); q.rounded_rectangle([0,0,149,79],radius=8,fill=(120,190,110)); q.text((75,40),'10 000',font=font(FB,26),fill=(30,90,40),anchor='mm')
        ps(fr,p,540+330*math.cos(a),900+420*math.sin(a),A*0.9,0.8,rot=a*40)
def cloud(fr,x,y,lt,A):
    for dx,dy,r in [(-90,0,70),(0,-30,90),(90,0,70),(30,20,70)]:
        D=Image.new('RGBA',(r*2,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*2-1,r*2-1],fill=(110,115,130,235)); put(fr,D,x+dx,y+dy,A)
    L_=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L_)
    for i in range(12):
        k=(lt*2.2+i/12)%1; xx=x-150+i*27; yy=y+60+k*360; d.line([(xx,yy),(xx-8,yy+40)],fill=(120,170,255,int(230*(1-k))),width=6)
    fr.paste(L_,(0,0),L_)
def crackheart(fr,x,y,lt,A):
    k=prog(lt,0.3,0.6); h=heart_img().resize((300,270),Image.LANCZOS)
    if k<=0: ps(fr,h,x,y,A); return
    l=h.crop((0,0,150,270)); r=h.crop((150,0,300,270)); ps(fr,l,x-75-60*k,y+80*k*k,A,rot=20*k); ps(fr,r,x+75+60*k,y+80*k*k,A,rot=-20*k)
def glass(fr,A):
    L_=Image.new('RGBA',(W,H),(180,210,230,int(70*A))); d=ImageDraw.Draw(L_)
    for i in range(3): d.line([(200+i*320,0),(-200+i*320,H)],fill=(255,255,255,int(60*A)),width=40)
    d.rectangle([0,0,W,40],fill=(60,70,80,255)); d.rectangle([0,H-60,W,H],fill=(60,70,80,255)); fr.paste(L_,(0,0),L_)
def car(fr,x,lt,A,v=0):
    im=PH('CAR',900); im=mouthify(im,'CAR',v) if v else im; ps(fr,im,x,1450,A,dy=20)
KSIGN=lambda: sign2('Chez Bakary','Thé · Café · Petit détail')

def phone7(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE if kind in('deliv',) else (40,40,50)); 
    if kind=='fail':
        d.text((300,130),'Paiement mobile',font=font(FB,44),fill=(255,255,255),anchor='mm'); d.ellipse([220,300,380,460],fill=(220,50,40)); d.line([(260,340),(340,420)],fill=(255,255,255),width=16); d.line([(340,340),(260,420)],fill=(255,255,255),width=16)
        d.text((300,540),'Échec',font=font(FB,64),fill=(220,50,40),anchor='mm'); d.text((300,630),'Réseau indisponible',font=font(FM,38),fill=ENCRE,anchor='mm'); d.text((300,720),'Montant : 60 000 F',font=font(FB,36),fill=ENCRE,anchor='mm')
    elif kind=='call':
        d.text((300,130),'Appel en cours',font=font(FM,40),fill=(255,255,255),anchor='mm'); d.ellipse([200,280,400,480],fill=(40,60,120)); d.text((300,380),'K',font=font(FB,110),fill=(255,255,255),anchor='mm')
        d.text((300,560),'Karim',font=font(FB,60),fill=ENCRE,anchor='mm'); heart=heart_img().resize((60,54)); S.paste(heart,(420,530),heart); d.text((300,660),'Pas de réponse',font=font(FB,44),fill=(220,50,40),anchor='mm')
        d.ellipse([240,880,360,1000],fill=(220,50,40)); d.line([(270,950),(330,930)],fill=(255,255,255),width=14)
    elif kind=='deliv':
        ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
        d.text((30,230),'Awa Couture',font=font(FB,46),fill=ENCRE); d.ellipse([230,320,370,460],fill=FONCE); check(d,300,390,40,(255,255,255),12)
        d.text((300,520),'Commande livrée',font=font(FB,46),fill=FONCE,anchor='mm'); d.text((300,620),'40 m de bazin doré',font=font(FB,40),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([90,690,510,770],radius=40,fill=(222,242,200)); d.text((300,730),'Payé à la livraison',font=font(FB,34),fill=FONCE,anchor='mm')
    else:
        d.text((300,130),'Messages',font=font(FB,44),fill=(255,255,255),anchor='mm'); d.text((40,250),'Karim',font=font(FB,46),fill=ENCRE); heart=heart_img().resize((50,45)); S.paste(heart,(200,252),heart)
        d.rounded_rectangle([30,330,560,760],radius=36,fill=(230,236,245))
        for i,l in enumerate(['Désolé ma reine,','vendredi soir je suis','en voyage d\'affaires','à Dakar. Bisous.']): d.text((60,380+i*85),l,font=font(FB,40),fill=ENCRE)
    return S
@lru_cache(None)
def P7(kind): return phone_with(phone7(kind))
@lru_cache(None)
def CARNET(kind):
    p=Image.new('RGBA',(820,620),(0,0,0,0)); d=ImageDraw.Draw(p); d.rounded_rectangle([0,0,819,619],radius=20,fill=(245,232,200),outline=(150,110,60),width=8)
    for y in range(90,620,70): d.line([(40,y),(780,y)],fill=(170,190,220),width=3)
    d.line([(110,0),(110,619)],fill=(220,120,120),width=4)
    if kind=='awa' or kind=='awax': d.text((140,170),'Awa – 10 000 F',font=font(FB,64),fill=(30,40,120)); d.text((140,310),'Modibo – thés…',font=font(FM,44),fill=(90,90,110))
    if kind=='awax': d.line([(130,205),(700,195)],fill=(200,30,30),width=12)
    if kind=='van': d.text((140,170),'Awa – 10 000 F',font=font(FM,44),fill=(90,90,110)); d.text((140,300),'Van – thés impayés : 47',font=font(FB,58),fill=(30,40,120)); d.ellipse([560,280,800,380],outline=(220,40,40),width=8)
    return p.rotate(-3,expand=True)
@lru_cache(None)
def BILL():
    p=Image.new('RGBA',(330,170),(0,0,0,0)); d=ImageDraw.Draw(p); d.rounded_rectangle([0,0,329,169],radius=14,fill=(200,170,110),outline=(120,90,40),width=6)
    d.ellipse([20,30,130,140],fill=(170,140,90)); d.text((230,60),'10 000',font=font(FB,56),fill=(80,50,20),anchor='mm'); d.text((230,120),'FRANCS CFA',font=font(FB,26),fill=(80,50,20),anchor='mm'); return p
def night(fr,k=0.45):
    fr2=ImageEnhance.Brightness(fr.convert('RGB')).enhance(k); L_=Image.new('RGB',fr2.size,(20,30,80)); return Image.blend(fr2,L_,0.25)
def card(fr,text,lt,A):
    ps(fr,txt(text,90,(255,255,255)),540,960,A*eo(prog(lt,0.1,0.4)),1.0,dy=8,op=0.5)
def tearfx(fr,x,y,lt,A):
    k=(lt*0.8)%1; D=Image.new('RGBA',(40,60),(0,0,0,0)); ImageDraw.Draw(D).ellipse([5,15,35,55],fill=(150,200,255,230)); ImageDraw.Draw(D).polygon([(20,0),(6,30),(34,30)],fill=(150,200,255,230)); put(fr,D,x,y+k*160,A*(1-k))
def sparkle(fr,x,y,lt,A):
    k=prog(lt,0.4,1.0); s=int(30+60*math.sin(k*math.pi)); D=Image.new('RGBA',(s*2,s*2),(0,0,0,0)); q=ImageDraw.Draw(D); q.polygon([(s,0),(s*1.15,s*0.85),(s*2,s),(s*1.15,s*1.15),(s,s*2),(s*0.85,s*1.15),(0,s),(s*0.85,s*0.85)],fill=(255,250,200,230)); put(fr,D,x,y,A*math.sin(k*math.pi))
ATEL='D4'
SCR=(351, 727, 114, 228)
@lru_cache(None)
def BARK():
    b=Image.open('/mnt/user-data/uploads/1000439194.jpg').convert('RGB').crop((318,40,438,440)); b=b.resize((b.width*3,b.height*3),Image.LANCZOS)
    col=Image.new('RGB',(b.width,H)); y=0
    while y<H: col.paste(b,(0,y)); b=b.transpose(Image.FLIP_TOP_BOTTOM); y+=b.height
    col=col.convert('RGBA'); a=Image.new('L',col.size,255); d=ImageDraw.Draw(a)
    for x in range(30): d.line([(x,0),(x,H)],fill=int(255*x/30)); d.line([(col.width-1-x,0),(col.width-1-x,H)],fill=int(255*x/30))
    col.putalpha(a); return col
def trunk(fr,x,A,w=300):
    t=BARK().resize((w,H)); put(fr,t,x,H//2,A)

def phone8(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE if kind!='call' else (40,40,50))
    if kind!='call': ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='search':
        d.rounded_rectangle([30,240,570,320],radius=40,fill=(240,240,240)); d.text((70,280),'Recherche : fleuriste',font=font(FM,32),fill=ENCRE,anchor='lm')
        d.rounded_rectangle([24,360,576,620],radius=28,fill=(240,248,232),outline=FONCE,width=5); d.text((50,400),'1. Fanta Fleurs',font=font(FB,46),fill=(220,90,20)); starrow(d,190,490,22); d.text((330,490),'4,7 · 58 avis',font=font(FB,30),fill=FONCE,anchor='lm')
        d.text((50,560),'Bouquets · Roses · Événements',font=font(FM,26),fill=ENCRE,anchor='lm')
        for i in range(2): y=650+i*130; d.rounded_rectangle([24,y,576,y+110],radius=24,fill=(246,246,246)); d.text((50,y+55),f'{i+2}. '+('Fleurs du Fleuve' if i==0 else 'Jardin de Kati'),font=font(FM,32),fill=(120,120,120),anchor='lm')
    elif kind=='sent':
        d.ellipse([230,250,370,390],fill=FONCE); check(d,300,320,40,(255,255,255),12); d.text((300,440),'Commande envoyée',font=font(FB,44),fill=FONCE,anchor='mm')
        d.rounded_rectangle([24,500,576,1010],radius=28,fill=(255,243,226),outline=ORANGE,width=5)
        for i,l in enumerate(['Fanta Fleurs','50 bouquets','de roses blanches','Atelier Awa Couture','Aujourd\'hui, 16h']): d.text((300,565+i*85),l,font=font(FB if i<3 else FM,38),fill=ENCRE,anchor='mm')
    elif kind=='shop':
        d.text((300,260),'Ouvrir ma boutique',font=font(FB,46),fill=ENCRE,anchor='mm'); d.rounded_rectangle([120,300,480,360],radius=30,fill=(222,242,200)); d.text((300,330),'Gratuitement',font=font(FB,34),fill=FONCE,anchor='mm')
        d.text((50,420),'Nom de la boutique',font=font(FM,28),fill=(120,120,120)); d.rounded_rectangle([40,460,560,540],radius=20,fill=(245,245,245)); d.text((70,500),'Sali Délices',font=font(FB,40),fill=ENCRE,anchor='lm')
        d.text((50,580),'Produits',font=font(FM,28),fill=(120,120,120))
        for i,l in enumerate(['Beignets','Arachides','Bissap']): d.rounded_rectangle([40+i*175,620,200+i*175,690],radius=30,fill=(255,236,210)); d.text((120+i*175,655),l,font=font(FB,28),fill=(200,100,10),anchor='mm')
        d.rounded_rectangle([90,780,510,870],radius=45,fill=FONCE); d.text((300,825),'Créer ma boutique',font=font(FB,36),fill=(255,255,255),anchor='mm')
    elif kind=='neworder':
        d.text((30,230),'Sali Délices',font=font(FB,46),fill=ENCRE); d.rounded_rectangle([24,310,576,860],radius=30,fill=(255,243,226),outline=ORANGE,width=6)
        d.text((300,380),'Nouvelle commande !',font=font(FB,44),fill=(200,100,10),anchor='mm'); d.text((300,500),'10 beignets',font=font(FB,56),fill=ENCRE,anchor='mm')
        d.text((300,610),'Livraison : Badalabougou',font=font(FM,34),fill=ENCRE,anchor='mm'); d.rounded_rectangle([110,700,490,780],radius=40,fill=FONCE); d.text((300,740),'Accepter',font=font(FB,36),fill=(255,255,255),anchor='mm')
    elif kind=='done':
        d.text((30,230),'Awa Couture',font=font(FB,46),fill=ENCRE); d.ellipse([230,320,370,460],fill=FONCE); check(d,300,390,40,(255,255,255),12)
        d.text((300,520),'Commande terminée',font=font(FB,44),fill=FONCE,anchor='mm'); d.text((300,610),'Décoration showroom',font=font(FB,36),fill=ENCRE,anchor='mm'); d.text((300,660),'Konaté',font=font(FB,36),fill=ENCRE,anchor='mm')
        d.rounded_rectangle([170,720,430,800],radius=40,fill=(222,242,200)); d.text((300,760),'Payée',font=font(FB,40),fill=FONCE,anchor='mm')
    else:
        d.text((300,130),'Appel entrant',font=font(FM,40),fill=(255,255,255),anchor='mm'); d.ellipse([200,280,400,480],fill=(200,40,60)); d.text((300,380),'K',font=font(FB,110),fill=(255,255,255),anchor='mm')
        d.text((300,560),'Kadidia',font=font(FB,60),fill=ENCRE,anchor='mm'); heart=heart_img().resize((60,54)); S.paste(heart,(450,530),heart)
        d.ellipse([110,880,230,1000],fill=(220,50,40)); d.ellipse([370,880,490,1000],fill=FONCE)
    return S
@lru_cache(None)
def P8(kind): return phone_with(phone8(kind))
def phone_shot(fr,kind,lt,A): k=eo(prog(lt,0,0.35)); ps(fr,P8(kind),540,lerp(1300,1100,k),A,1.15,dy=30)

def dust(fr,x,y,lt,A):
    for i in range(9):
        k=min(1,(lt*0.7+i*0.06)); r=int(60+k*120+i*8); D=Image.new('RGBA',(r*2+40,r*2+40),(0,0,0,0)); ImageDraw.Draw(D).ellipse([20,20,r*2+19,r*2+19],fill=(205,175,135,int(210*(1-k*0.7))))
        put(fr,D.filter(ImageFilter.GaussianBlur(14)),x-380+i*95,y-k*120-(i%3)*30,A)
def pour(fr,x,by,h,lt,A,v=0):
    # cycle du thé malien : verser de haut (verre à moitié), verre plein, reverser le verre dans la théière
    ph=lt%2.4; talk_=v>0.3
    if ph<0.8: k='PT1o' if talk_ else 'PT1c'
    elif ph<1.3: k='PT1o' if talk_ else 'PT2c'
    else: k='PR1o' if talk_ else 'PR1c'
    im=Image.open(HD+k+'.png') if False else PH(k,h); put(fr,im,x,by-h//2,A)
def phone9(kind):
    S=Image.new('RGBA',(SW,SH),(255,255,255,255)); d=ImageDraw.Draw(S)
    d.rectangle([0,0,SW,200],fill=FONCE); ic=ICON.resize((76,76),Image.LANCZOS); S.paste(ic,(40,100),ic); d.text((132,110),'Sounsouni',font=font(FB,44),fill=(255,255,255))
    if kind=='add':
        d.text((30,230),'Chez Bakary',font=font(FB,46),fill=ENCRE); d.text((30,300),'Ajouter un produit',font=font(FM,34),fill=(110,130,100))
        d.rounded_rectangle([24,360,576,760],radius=28,fill=(255,243,226),outline=ORANGE,width=5)
        d.text((300,440),'Brochettes de viande',font=font(FB,42),fill=ENCRE,anchor='mm'); d.text((300,530),'500 FCFA les 3',font=font(FB,48),fill=FONCE,anchor='mm')
        d.rounded_rectangle([110,620,490,700],radius=40,fill=FONCE); d.text((300,660),'Produit ajouté ✓'.replace(' ✓',' !'),font=font(FB,34),fill=(255,255,255),anchor='mm')
    elif kind=='shop':
        d.text((30,230),'Chez Bakary',font=font(FB,50),fill=ENCRE); starrow(d,170,320,20); d.text((300,320),'4,9',font=font(FB,34),fill=FONCE,anchor='lm')
        for i,l in enumerate(['Thé','Café','Brochettes']):
            y=390+i*150; d.rounded_rectangle([30,y,570,y+120],radius=26,fill=(250,244,228) if i<2 else (255,232,200),outline=ORANGE if i==2 else (230,220,200),width=5 if i==2 else 2); d.text((70,y+60),l,font=font(FB,42),fill=ENCRE,anchor='lm')
            if i==2: d.rounded_rectangle([400,y+35,550,y+85],radius=25,fill=(220,50,40)); d.text((475,y+60),'Nouveau',font=font(FB,26),fill=(255,255,255),anchor='mm')
    else:
        d.text((30,230),'Bintou Mèches',font=font(FB,46),fill=ENCRE); d.text((30,295),'Perruques & mèches',font=font(FM,30),fill=(110,130,100))
        d.rounded_rectangle([24,360,576,820],radius=28,fill=(255,243,226),outline=ORANGE,width=5)
        d.text((300,430),'Commande à livrer',font=font(FB,42),fill=(200,100,10),anchor='mm'); d.text((300,540),'1 perruque',font=font(FB,52),fill=ENCRE,anchor='mm'); d.text((300,640),'Djélibougou',font=font(FM,38),fill=ENCRE,anchor='mm')
    return S
@lru_cache(None)
def P9(kind): return phone_with(phone9(kind))
def grillfx(fr,x,y,lt,A):
    for i in range(6):
        k=(lt*0.6+i/6)%1; r=int(30+k*90); D=Image.new('RGBA',(r*2+40,r*2+40),(0,0,0,0)); ImageDraw.Draw(D).ellipse([20,20,r*2+19,r*2+19],fill=(220,220,220,int(120*(1-k)))); put(fr,D.filter(ImageFilter.GaussianBlur(8)),x+20*math.sin(i+lt),y-k*500,A)
def clockfx(fr,x,y,lt,A,txt_):
    D=Image.new('RGBA',(260,260),(0,0,0,0)); q=ImageDraw.Draw(D); q.ellipse([10,10,250,250],fill=(255,255,255),outline=(60,60,60),width=10); a=lt*6
    q.line([(130,130),(130+80*math.sin(a),130-80*math.cos(a))],fill=(30,30,30),width=10); q.line([(130,130),(130+55*math.sin(a/12),130-55*math.cos(a/12))],fill=(30,30,30),width=12); put(fr,D,x,y,A)
    ps(fr,txt(txt_,60,(255,255,255)),x,y+190,A,dy=4,op=0.6)
def glassesfx(fr,lt,A,n):
    for i in range(n):
        g=Image.new('RGBA',(70,90),(0,0,0,0)); q=ImageDraw.Draw(g); q.polygon([(8,0),(62,0),(54,88),(16,88)],fill=(255,255,255,170),outline=(150,150,150)); put(fr,g,860,1700-i*80,A)
def fightfx(fr,lt,A):
    for i in range(9):
        a=lt*5+i*0.7; r=int(140+40*math.sin(lt*7+i)); D=Image.new('RGBA',(r*2,r*2),(0,0,0,0)); ImageDraw.Draw(D).ellipse([0,0,r*2-1,r*2-1],fill=(235,225,210,200)); put(fr,D,540+260*math.cos(a),1200+200*math.sin(a),A)
START={}
