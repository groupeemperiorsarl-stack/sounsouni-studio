from faster_whisper import WhisperModel; import librosa,json,soundfile as sf
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2); IX=json.load(open('ix.json'))
for n,cut in (('m07','quoi'),('a16','moi')):
    i=IX[n]; y,sr=librosa.load(f'vo/L{i:02d}.wav',sr=24000)
    s,_=m.transcribe(librosa.resample(y,orig_sr=24000,target_sr=16000),language='fr',word_timestamps=True); ws=[w for x in s for w in x.words]
    e=[w.end for w in ws if cut in w.word.lower()]
    if e: sf.write(f'vo/L{i:02d}.wav',y[:int((e[0]+0.12)*sr)],sr,subtype='PCM_16'); print(n,'coupé',round(e[0],2))
