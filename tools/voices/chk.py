import librosa,sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for f in sys.argv[1:]:
    a,_=librosa.load(f,sr=16000); s,_=m.transcribe(a,language='fr'); print(f,'|',' '.join(x.text for x in s),flush=True)
