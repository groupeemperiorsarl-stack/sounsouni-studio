SHOTS=[('titre',1.2,None),('open',2.4,None),('pause',1.6,None),('mphone',1.0,None),('app1',4.0,None),('knock',1.4,None),
 ('s0',None,0),('s1',None,1),('s2',None,2),('s3',None,3),('back',1.0,None),('s4',None,4),('s5',None,5),
 ('cab',2.0,None),('s6',None,6),('s7',None,7),('s8',None,8),('take',1.0,None),('app2',5.0,None),('hide',1.8,None),
 ('s9',None,9),('s10',None,10),('s11',None,11),('s12',None,12),('s13',None,13),('bgo',1.2,None),('s14',None,14),('s15',None,15),('s16',None,16),
 ('s17',None,17),('ghost',2.0,None),('s18',None,18),('s19',None,19),('swal',1.0,None),('s20',None,20),('s21',None,21),('s22',None,22),('s23',None,23),('s24',None,24),('s25',None,25),('zap',1.4,None),
 ('s26',None,26),('give',1.2,None),('s27',None,27),('s28',None,28),('cricket',2.2,None),('gather',1.2,None),('s29',None,29),('leave',1.6,None),
 ('s30',None,30),('s31',None,31),('s32',None,32),('s33',None,33),('s34',None,34),('bleave',1.6,None),('s35',None,35),('suite',1.8,None),('fin',None,36)]
SFX={'app1':[(0.0,'ding')],'knock':[(0.2,'knock')],'s3':[(0.0,'pop')],'app2':[(0.0,'ding')],'s11':[(0.0,'pop')],'ghost':[(0.2,'crack')],'swal':[(0.0,'pop')],
 'zap':[(0.1,'thunder')],'cricket':[(0.2,'cricket')],'gather':[(0.1,'whoosh')],'s29':[(0.0,'whoosh')],'leave':[(0.0,'heels')],'bleave':[(0.0,'pop')]}
PAD=0.15; PAUSE=0.4
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
