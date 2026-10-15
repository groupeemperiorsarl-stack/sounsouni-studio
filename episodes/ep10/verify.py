from faster_whisper import WhisperModel
import librosa,glob
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=1)
with open('verify.txt','w') as fh:
    for f in sorted(glob.glob('vo/L*.wav')):
        y,_=librosa.load(f,sr=16000); s,_=m.transcribe(y,language='fr',beam_size=1); fh.write(f'{f[-6:-4]} {len(y)/16000:.1f} | '+' '.join(x.text.strip() for x in s)[:80]+'\n'); fh.flush()
