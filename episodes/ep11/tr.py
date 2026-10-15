import librosa,sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for f in sys.argv[1:]:
    a,_=librosa.load(f'rec/{f}.wav',sr=16000)
    s,_=m.transcribe(a,language='fr',word_timestamps=True)
    with open(f'rec/{f}.txt','w') as o:
        for x in s:
            o.write(f"## {x.start:.2f}-{x.end:.2f} {x.text}\n")
            for w in x.words: o.write(f"{w.start:.2f}-{w.end:.2f}{w.word}\n")
    print('done',f,flush=True)
