
# ---- ép.11 « Le haut-parleur » : plans
IX=json.load(open(EP+'ix.json'))
def S_(n,d=None,ln=None): return (n,d,IX[ln] if ln else None)
import os
BURN=float(os.environ.get('BURN','2.6'))
SHOTS=[S_('titre',1.6),S_('robe',2.6),S_('grp',2.8),
 S_('miw',None,'i01'),S_('ah2',None,'a01'),S_('dic',None,'d01'),S_('mbw',None,'m01'),
 S_('toc',2.6),S_('miw',None,'i02'),S_('a5',None,'a02'),S_('panic',2.2),S_('toc2',1.6),
 S_('kadi',None,'k01'),S_('grp',None,'g'),S_('kadi',None,'k02'),S_('sweatA',2.0),S_('kadi',None,'k03'),S_('miw',None,'i03'),S_('give',2.6),
 S_('kadis',None,'k04'),S_('ah1',None,'a03'),S_('bstep',None,'b01'),S_('bj',None,'b02'),S_('shockA',1.8),
 S_('dic',None,'d02'),S_('mute',None,'d03'),S_('md',None,'m02'),S_('kadis',None,'k05'),S_('bjsad',None,'b03'),S_('kadis',None,'k06'),
 S_('a20',None,'a04'),S_('kadi',None,'k07'),S_('a20',None,'a05'),S_('kadib',None,'k08'),S_('kadib',None,'k09'),S_('ba',None,'b04'),S_('c60',1.8),
 S_('atel',2.4),S_('aw',None,'a06'),S_('awbulb',None,'a07'),S_('mim',None,'i04'),S_('aw',None,'a08'),S_('mim',None,'i05'),S_('c52',1.4),S_('a5at',None,'a09'),
 S_('app1',3.0),S_('af7',None,'a10'),S_('app2',2.6),S_('aw',None,'a11'),S_('cutp',2.4),
 S_('pour',2.4),S_('ba',None,'b05'),S_('kadib',None,'k10'),S_('diw',None,'d04'),S_('kadib',None,'k11'),S_('dic',None,'d05'),S_('mr',None,'m03'),
 S_('sip',1.6),S_('kadib',None,'k12'),S_('freeze',1.0),S_('kadib',None,'k13'),S_('cough',None,'b06'),S_('die',None,'d06'),S_('whistle',2.0),S_('dic',None,'d07'),S_('md',None,'m04'),S_('ksmile',1.8),S_('c31',1.4),
 S_('beep',1.6),S_('mim',None,'i06'),S_('batt',1.8),S_('a5at',None,'a12'),
 S_('mirun',2.0),S_('mik',None,'i08'),S_('mrun',None,'m05'),S_('moto',2.2),S_('sey',None,'s01'),
 S_('aw',None,'a13'),S_('sey',None,'s02'),S_('app3',2.6),S_('plug',1.4),S_('md',None,'m06'),S_('aw',None,'a14'),S_('montage',4.5),
 S_('kadib',None,'k14'),S_('door',1.4),S_('reveal',3.2),S_('kadi',None,'k15'),S_('miwyes',None,'i07'),S_('dic',None,'d08'),S_('mr',None,'m07'),S_('dic',None,'d09'),
 S_('app4',3.4),S_('kadi',None,'k16'),S_('kadi',None,'k17'),S_('blush',1.8),S_('leave',2.6),
 S_('awalk',2.4),S_('bj',None,'b07'),S_('abk',None,'a15'),S_('abk2',None,'a16'),S_('grin',1.8),S_('brh',None,'b08'),S_('md',None,'m08'),S_('ba',None,'b09'),
 S_('heels',1.4),S_('ft2',None,'f01'),S_('ft4',None,'f02'),S_('stop',2.2),S_('look',2.6),S_('dic',None,'d10'),S_('facepalm',1.6),S_('suite',2.6),
 S_('finb',None,'vo2'),S_('finc',None,'vo3'),S_('fin2',3.0)]
SFX={'robe':[(0.0,'sizzle')],'toc':[(0.2,'cane')],'toc2':[(0.0,'cane')],'give':[(0.9,'thunder')],'shockA':[(0.0,'pop')],'c60':[(0.2,'tick')],'atel':[(0.0,'sew')],'c52':[(0.0,'tick')],
 'app1':[(0.0,'click')],'app2':[(0.0,'ding')],'cutp':[(0.0,'snip')],'pour':[(0.0,'pourw')],'sip':[(0.3,'sip')],'cough':[(0.0,'whoosh')],'whistle':[(0.0,'whistlew')],'c31':[(0.0,'tick')],
 'beep':[(0.0,'beeps')],'batt':[(0.0,'beeps')],'mirun':[(0.0,'whoosh'),(0.3,'steps')],'moto':[(0.0,'klaxon'),(0.3,'whoosh')],'app3':[(0.0,'ding')],'plug':[(0.2,'click'),(0.4,'sew')],'montage':[(0.0,'sew'),(2.5,'sew')],
 'door':[(0.1,'door')],'reveal':[(0.2,'sparkle')],'app4':[(0.0,'ding')],'leave':[(0.2,'cane')],'heels':[(0.0,'heels')],'stop':[(0.3,'thunder')],'facepalm':[(0.3,'pop')],'blush':[(0.2,'heart')],'grin':[(0.2,'heart')]}
PAD=0.12; PAUSE=0.22
T=[];t=0;prev=None;LEAD={}
for n,d,li in SHOTS:
    if d: dd=d
    else:
        lead=PAD+(PAUSE if prev and L[li][0]!=prev else 0); LEAD[li]=lead; prev=L[li][0]; dd=DUR[li]+lead+PAD
    T.append((n,t,dd,li)); t+=dd
TOT=t
for _i in range(len(L)):
    _w=wave.open(EP+f'vo/L{_i:02d}.wav'); _sr=_w.getframerate(); _a=np.frombuffer(_w.readframes(_w.getnframes()),np.int16).astype(np.float32)/32768
    _ix=np.nonzero(np.abs(_a)>0.015)[0]; OFF[_i]=(max(0,_ix[0]-300)/_sr) if len(_ix) else 0
MED=dict(by=3050,h=2550); BL=3
