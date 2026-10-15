import librosa,glob
from faster_whisper import WhisperModel
f=glob.glob('rec/*3_03PM*.wav')[0]
a,_=librosa.load(f,sr=16000)
m=WhisperModel('small',device='cpu',compute_type='int8')
s,_=m.transcribe(a,language='fr',word_timestamps=True)
for x in s:
  for w in x.words: print(f"{w.start:.2f}-{w.end:.2f}{w.word}")
