from faster_whisper import WhisperModel
import re,unicodedata,difflib,sys
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2)
def norm(s): s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn'); return re.sub(r'[^a-z ]',' ',s).split()
K=0
for l in open('lines.txt'):
    out,_,_,_,t=l.rstrip('\n').split('|'); out='vo/L%02d.wav'%K; K+=1
    import librosa; aud=librosa.load(out,sr=16000)[0]; segs,_=m.transcribe(aud,language='fr',beam_size=1); h=' '.join(s.text for s in segs)
    r=difflib.SequenceMatcher(None,norm(t),norm(h)).ratio()
    print(f'{r:.2f}',out,'|',h.strip(),flush=True)
