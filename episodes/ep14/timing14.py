
# ---- ép.11 « Le haut-parleur » : plans
IX=json.load(open(EP+'ix.json'))
def S_(n,d=None,ln=None): return (n,d,IX[ln] if ln else None)
import os
BURN=float(os.environ.get('BURN','2.6'))
SHOTS=[S_('titre',1.6),S_('open',3.0),
 S_('dic',None,'d01'),S_('facepalm',1.4),S_('ft4',None,'f01'),S_('dic',None,'d02'),S_('bp',None,'b01'),S_('laughF',1.8),S_('ft2',None,'f02'),S_('bq',1.3),
 S_('ft3',None,'f03'),S_('bj',None,'b02'),S_('awaeyes',2.0),S_('ft2',None,'f04'),S_('a20',None,'a01'),S_('ft4',None,'f05'),S_('a20',None,'a02'),S_('ft4',None,'f06'),S_('shakeA',1.4),S_('a20',None,'a03'),
 S_('ft1',None,'f07'),S_('ft2',None,'f08'),S_('fleave',2.0),S_('slam',1.8),S_('diw',None,'d03'),S_('md',None,'m01'),
 S_('atel',1.6),S_('a5at',None,'a04'),S_('mim',None,'i01'),S_('aw',None,'a05'),S_('mim',None,'i02'),S_('a20at',None,'a06'),S_('a20at',None,'a07'),S_('mim',None,'i03'),S_('aw',None,'a08'),
 S_('app1',3.0),S_('mim',None,'i04'),S_('af7',None,'a09'),S_('app2',3.2),S_('app3',2.4),S_('af7',None,'a10'),S_('mim',None,'i05'),S_('glare',1.4),
 S_('bonk',1.8),S_('dic',None,'d04'),S_('moto',2.2),S_('sey',None,'s01'),S_('ba',None,'b03'),S_('sey',None,'s02'),S_('boxopen',2.4),S_('bbox',None,'b04'),S_('md',None,'m02'),S_('dsf',None,'d05'),
 S_('eat',1.6),S_('note',None,'b05'),S_('brh',None,'b06'),S_('eat2',1.4),S_('md',None,'m03'),S_('ba',None,'b07'),S_('md',None,'m04'),S_('md',None,'m05'),S_('pop',1.8),S_('eat3',2.0),S_('think',1.8),
 S_('ba',None,'b08'),S_('sey',None,'s03'),S_('ba',None,'b09'),S_('app4',2.6),S_('sey',None,'s04'),S_('bj',None,'b10'),S_('app5',3.0),S_('md',None,'m06'),
 S_('turn',1.4),S_('onecake',2.4),S_('mshout',None,'m10'),S_('bp',None,'b14'),S_('dsf',None,'d06'),S_('mshout',None,'m07'),S_('dic',None,'d07'),S_('sey',None,'s05'),S_('dic',None,'d08'),S_('headhands',1.6),S_('motoleave',1.8),
 S_('vib',1.8),S_('app6',3.2),S_('ah1at',None,'a11'),S_('mim',None,'i06'),S_('seyin',1.4),S_('sey',None,'s06'),S_('onecake2',2.2),S_('a20at',None,'a12'),S_('red',1.6),S_('a5at',None,'a13'),S_('sey',None,'s07'),S_('slam2',1.4),
 S_('hover',2.4),S_('mou',None,'o01'),S_('jump',1.4),S_('ba',None,'b11'),S_('tactac',1.4),S_('awafast',2.0),S_('a5',None,'a14'),S_('diw',None,'d09'),S_('a5',None,'a15'),
 S_('step',2.0),S_('slip',2.4),S_('leap',1.2),S_('catch',3.4),S_('heart',2.4),S_('catchc',None,'b12'),S_('catchc',None,'a16'),S_('awaleave',2.2),S_('look',1.6),
 S_('mou',None,'o02'),S_('die',None,'d10'),S_('bj',None,'b13'),S_('md',None,'m08'),S_('md',None,'m09'),
 S_('car',2.6),S_('window',2.0),S_('karim',None,'k01'),S_('karim',None,'k02'),S_('flash',1.6),S_('suite',2.6),
 S_('finb',None,'vo2'),S_('finc',None,'vo3'),S_('fin2',3.0)]
SFX={'open':[(0.0,'crowd')],'facepalm':[(0.3,'pop')],'laughF':[(0.1,'pop')],'awaeyes':[(0.3,'thunder')],'shakeA':[(0.2,'boum')],'fleave':[(0.0,'heels')],'slam':[(0.1,'door'),(0.15,'boum')],
 'atel':[(0.0,'sew')],'app1':[(0.0,'click')],'app2':[(0.0,'click')],'app3':[(0.0,'ding')],'bonk':[(0.3,'boum'),(0.35,'pop')],'moto':[(0.0,'klaxon'),(0.3,'whoosh')],'boxopen':[(0.3,'sparkle')],
 'eat':[(0.2,'pop')],'eat2':[(0.2,'pop')],'pop':[(0.2,'pop'),(0.6,'pop'),(1.0,'pop')],'eat3':[(0.0,'whoosh')],'app4':[(0.0,'click')],'app5':[(0.0,'click')],'onecake':[(0.2,'cricket')],
 'headhands':[(0.2,'boum')],'motoleave':[(0.0,'klaxon')],'vib':[(0.0,'buzz'),(0.8,'buzz')],'app6':[(0.0,'ding')],'seyin':[(0.0,'klaxon')],'onecake2':[(0.2,'cricket')],'red':[(0.0,'sizzle')],'slam2':[(0.1,'door')],
 'hover':[(0.0,'whoosh')],'jump':[(0.2,'pop')],'tactac':[(0.0,'heels')],'awafast':[(0.0,'heels')],'step':[(0.0,'heels'),(1.5,'whoosh')],'slip':[(0.0,'whoosh')],'leap':[(0.0,'whoosh')],'catch':[(0.2,'heart'),(1.0,'heart')],'heart':[(0.0,'heart'),(1.0,'heart')],
 'awaleave':[(0.0,'heels'),(1.8,'door')],'car':[(0.0,'motor')],'window':[(0.0,'motor')],'flash':[(0.1,'click'),(0.4,'thunder')]}
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
