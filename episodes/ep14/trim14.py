from faster_whisper import WhisperModel; import librosa,json,soundfile as sf
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2); IX=json.load(open('ix.json'))
for n,cut in (('f04',None),('a08','quittes'),('i05','awa'),('b06','moi'),('b08','gâteaux'),('m07',None),('a16',None),('s01','cadeau'),('a06','merci')):
    i=IX[n]; y,sr=librosa.load(f'vo/L{i:02d}.wav',sr=24000)
    s,_=m.transcribe(librosa.resample(y,orig_sr=24000,target_sr=16000),language='fr',word_timestamps=True); ws=[w for x in s for w in x.words]
    print(n,'|',' '.join(w.word for w in ws),flush=True)
    if cut:
        e=[w.end for w in ws if cut in w.word.lower()]
        if e: sf.write(f'vo/L{i:02d}.wav',y[:int((e[0]+0.15)*sr)],sr,subtype='PCM_16'); print('  coupé',round(e[0],2))
