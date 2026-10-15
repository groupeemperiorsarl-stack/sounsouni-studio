import librosa,glob,sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for n in sys.argv[1:]:
    a,_=librosa.load(f'cuts/{n}.wav',sr=16000); s,_=m.transcribe(a,language='fr'); print(n,'|',' '.join(x.text for x in s),flush=True)
