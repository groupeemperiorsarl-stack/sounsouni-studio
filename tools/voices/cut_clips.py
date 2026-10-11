import librosa,numpy as np,wave,sys,json
def cut(name,f,a,b):
    y,sr=librosa.load(f'rec/{f}.wav',sr=None,offset=a,duration=b-a)
    iv=[r for r in librosa.effects.split(y,top_db=32,frame_length=1024,hop_length=256) if (r[1]-r[0])/sr>0.05]
    y=y[max(0,iv[0][0]-int(0.04*sr)):iv[-1][1]+int(0.12*sr)]; y=y/np.abs(y).max()*0.9
    w=wave.open(f'cuts/{name}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y*32767).astype(np.int16).tobytes()); w.close()
    print(name,round(len(y)/sr,2))
J=[('d_secret','A',0,5.6),('d_rigolez','A',6.5,8.5),('d_ettoi','A',8.6,15.2),('d_parie','A',15.7,17.9),('d_perds','A',18.4,21.4),
('d_pari','A',21.7,24.35),('d_tel','A',24.36,27.3),('d_passe','A',27.5,28.8),('d_madame','A',28.9,34.45),('d_bobo','A',34.5,37.8),('d_brule','A',37.8,40.3),
('f_1','B',0,5.8),('f_2','B',5.9,8.4),('v_tom','B',8.5,12.3),('vo_1','B',15.3,23.7),('vo_2','B',23.8,28.7),('vo_3','B',28.8,37.3),
('a_vdb','C',2.3,4.3),('a_loser','C',4.4,6.75),('a_fatim','C',6.8,9.1)]
for j in J: cut(*j)
