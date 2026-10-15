from faster_whisper import WhisperModel
import librosa,glob
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=1)
with open('rec/tr2.txt','w') as fh:
    for f in sorted(glob.glob('rec/*2_1*PM.wav')):
        y,_=librosa.load(f,sr=16000); s,_=m.transcribe(y,language='fr',beam_size=2,word_timestamps=True)
        fh.write('== '+f+f' {len(y)/16000:.2f}\n'+' '.join(f'{w.word.strip()}[{w.start:.2f}-{w.end:.2f}]' for x in s for w in x.words)+'\n'); fh.flush()
