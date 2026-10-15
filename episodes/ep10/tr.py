import librosa,glob
from faster_whisper import WhisperModel
f=glob.glob('rec/*3_05PM*.wav')[0]
a,_=librosa.load(f,sr=16000)
m=WhisperModel('small',device='cpu',compute_type='int8')
s,_=m.transcribe(a,language='fr',word_timestamps=True)
for x in s: print(f"{x.start:.2f}-{x.end:.2f} {x.text}")
