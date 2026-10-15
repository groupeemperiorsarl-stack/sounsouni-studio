from faster_whisper import WhisperModel; import librosa,json,re,unicodedata,difflib
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2); L=json.load(open('dialogue.json'))
def norm(s): s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn'); return re.sub(r'[^a-z ]',' ',s).split()
for i,x in enumerate(L[:73]):
    s,_=m.transcribe(librosa.load(f'vo/L{i:02d}.wav',sr=16000)[0],language='fr',beam_size=1); h=' '.join(t.text for t in s)
    print(f'{difflib.SequenceMatcher(None,norm(x[2]),norm(h)).ratio():.2f}',i,x[2][:50],'|',h.strip(),flush=True)
