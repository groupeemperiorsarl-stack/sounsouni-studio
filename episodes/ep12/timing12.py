
# ---- ép.11 « Le haut-parleur » : plans
IX=json.load(open(EP+'ix.json'))
def S_(n,d=None,ln=None): return (n,d,IX[ln] if ln else None)
import os
BURN=float(os.environ.get('BURN','2.6'))
SHOTS=[S_('titre',1.6),S_('atel',3.0),
 S_('aw',None,'a01'),S_('mp1',None,'i01'),S_('aw',None,'a02'),S_('app',3.4),S_('mp3',None,'i02'),S_('aw',None,'a03'),
 S_('cut',2.4),S_('a14d',None,'a04'),S_('mp2d',None,'i03'),S_('a5d',None,'a05'),S_('mp1d',None,'i04'),S_('a5d',None,'a06'),S_('mp1d',None,'i05'),S_('a20d',None,'a07'),
 S_('kcard',1.8),S_('kwide',3.4),S_('dsg',None,'d01'),S_('mbat',None,'m01'),S_('bv',None,'b01'),S_('mdk',None,'m02'),
 S_('mrun',2.2),S_('me',None,'i06'),S_('br',None,'b02'),S_('me',None,'i07'),S_('me',None,'i08'),S_('mdk',None,'m03'),S_('ba',None,'b03'),S_('dic',None,'d02'),
 S_('awalk',2.6),S_('a5',None,'a08'),S_('me',None,'i09'),S_('a20',None,'a09'),S_('bj',None,'b04'),S_('a5',None,'a10'),S_('meclock',None,'i10'),S_('teeth',2.4),S_('a20',None,'a11'),
 S_('d10',None,'d03'),S_('bonk',1.8),S_('die',None,'d04'),S_('mr',None,'m04'),
 S_('sewwide',3.2),S_('awm',None,'a12'),S_('awm',None,'a13'),S_('blow',None,'b05'),S_('awm',None,'a14'),S_('br',None,'b06'),S_('touch',2.6),S_('think',None,'a15'),S_('mbw',None,'m05'),S_('diw',None,'d05'),
 S_('buzz',2.0),S_('grpcall',None,'d06'),S_('bp',None,'b07'),S_('stare',2.4),S_('think2',None,'a16'),S_('ironrest',2.2),
 S_('ms',None,'m06'),S_('me',None,'i11'),S_('lift',2.2),S_('hole',3.0),S_('bj',None,'b08'),S_('notif',2.8),S_('me',None,'i12'),S_('steps',2.6),S_('die',None,'d07'),S_('final',3.0),S_('suite',2.6),
 S_('fin',None,'vo1'),S_('finb',None,'vo2'),S_('finc',None,'vo3'),S_('fin2',3.0)]
SFX={'atel':[(0.0,'sew')],'app':[(0.0,'ding')],'cut':[(0.25,'clac'),(0.3,'boum')],'kwide':[(0.0,'sizzle')],'mrun':[(0.0,'whoosh'),(0.2,'steps')],'awalk':[(0.0,'heels')],
 'teeth':[(0.3,'cricket')],'bonk':[(0.35,'boum'),(0.4,'pop')],'sewwide':[(0.0,'sew')],'touch':[(0.9,'heart')],'buzz':[(0.0,'buzz'),(1.0,'buzz')],'stare':[(0.2,'thunder')],
 'ironrest':[(0.4,'sizzle')],'lift':[(0.2,'whoosh')],'hole':[(0.2,'cricket')],'notif':[(0.2,'ding')],'steps':[(0.0,'bigsteps')],'final':[(0.3,'thunder')]}
PAD=0.18; PAUSE=0.3
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
