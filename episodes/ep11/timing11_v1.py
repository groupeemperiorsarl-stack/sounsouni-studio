
# ---- ép.11 « Le haut-parleur » : plans
IX=json.load(open(EP+'ix.json'))
def S_(n,d=None,ln=None): return (n,d,IX[ln] if ln else None)
SHOTS=[S_('titre',1.4),S_('open',3.2),
 S_('mdC',None,'m_1'),S_('brC',None,'b_1'),S_('ds4',None,'d_secret'),S_('mdC',None,'m_2'),
 S_('laugh',None,'m_laugh'),S_('di6',None,'d_rigolez'),S_('di6',None,'d_ettoi'),S_('dic',None,'d_parie'),S_('mdC',None,'m_3'),S_('mdC',None,'m_4'),S_('did',None,'d_perds'),S_('baC',None,'b_arb'),
 S_('midi',1.8),S_('mwide',2.8),S_('mdM',None,'m_5'),S_('sa2',None,'s_1'),S_('mdM',None,'m_6'),S_('sa2',None,'s_2'),S_('mdM',None,'m_7'),S_('slaugh',None,'s_laugh'),S_('sa2',None,'s_3'),
 S_('spy',3.0),S_('sa5',None,'s_4'),S_('mt',None,'m_8'),S_('click',0.9),S_('app',3.6),S_('sa2y',None,'s_5'),S_('sa5',None,'s_6'),S_('mdM',None,'m_9'),S_('sa6b',None,'s_7'),S_('sa6',None,'s_8'),
 S_('mdM',None,'m_10'),S_('sa2',None,'s_9'),S_('mdH',None,'m_11'),S_('sleave',2.4),
 S_('tback',2.0),S_('crash',2.2),S_('to',None,'v_tom'),S_('di10',None,'d_pari'),
 S_('soir',1.6),S_('kw2',2.4),S_('mj',None,'m_12'),S_('die',None,'d_tel'),S_('mdK',None,'m_13'),S_('bl',None,'b_laugh2'),S_('baC',None,'b_verdict'),
 S_('awalk',3.0),S_('ring',2.0),S_('callscr',2.6),S_('di7',None,'d_passe'),S_('hp',1.6),S_('spk',None,'f_1'),S_('spk',None,'f_2'),S_('react',3.0),S_('bp',None,'b_panic'),S_('endcall',0.9),
 S_('silence',3.8),
 S_('diw',None,'d_madame'),S_('taistoi',2.2),S_('flyshot',2.0),S_('a5',None,'a_vdb'),S_('a5',None,'a_loser'),S_('loserhit',1.6),S_('dic',None,'d_bobo'),S_('mrun',None,'m_14'),S_('run',2.0),
 S_('mef',1.6),S_('bj',None,'b_whisp'),S_('a20',None,'a_tchip'),S_('aleave',2.4),
 S_('db',None,'d_brule'),S_('brC2',None,'b_last'),S_('door',2.0),S_('a21',None,'a_fatim'),S_('zoomA',1.8),S_('suite',2.6),
 S_('fin',None,'vo_1'),S_('finb',None,'vo_2'),S_('finc',None,'vo_3'),S_('fin2',3.0)]
SFX={'open':[(0.3,'heart')],'laugh':[],'midi':[(0.0,'crowd')],'mwide':[(0.0,'crowd')],'spy':[(1.6,'pop')],'click':[(0.2,'click')],'app':[(0.0,'ding'),(0.5,'coin')],
 'sleave':[(0.0,'steps')],'tback':[(0.6,'boum')],'crash':[(0.0,'clac'),(0.15,'boum')],'di10':[(0.0,'whoosh')],'kw2':[(1.0,'whoosh')],
 'awalk':[(0.0,'heels'),(1.2,'heart')],'ring':[(0.0,'call')],'callscr':[(0.0,'call')],'hp':[(0.3,'bip')],'endcall':[(0.1,'bip')],'silence':[(0.3,'cricket'),(2.2,'whoosh')],
 'taistoi':[(0.2,'pop')],'loserhit':[(0.15,'boum')],'run':[(0.0,'whoosh'),(0.4,'sizzle')],'aleave':[(0.0,'heels')],'door':[(0.15,'door'),(0.2,'boum')],'a21':['end0.1'],'zoomA':[(0.1,'thunder')],'mrun':[(0.3,'sizzle')]}
SFX['a21']=[]
PAD=0.18; PAUSE=0.45
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
