import sys; exec(open('/home/claude/ep10/prep2.py').read().split('for k,(src,box) in B.items():')[0].replace('from boxes2 import B',''))
SRC='/root/.claude/uploads/62e3aaef-1437-5194-ac56-922a24a42de7/5e56bcdd-image.jpg'
B={'KADI':(70,15,545,735),'KADIS':(800,10,1160,450),'KADIB':(585,325,985,745),'KADIB2':(995,325,1380,745)}
for k,box in B.items():
    out=f'/home/claude/ep13/hd/{k}.png'
    if os.path.exists(out): continue
    u=up(Image.open(SRC).convert('RGB').crop(box))
    sc=min(1.0,1400/u.height); small=u.resize((int(u.width*sc),int(u.height*sc)),Image.LANCZOS)
    a=np.asarray(remove(small,session=S,only_mask=True,post_process_mask=True).resize(u.size,Image.BILINEAR))
    lab,n=ndimage.label(a>60)
    if n>1:
        sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); keep=np.argmax(sz)+1; a=np.where(ndimage.binary_dilation(lab==keep,iterations=3),a,0)
    u=u.convert('RGBA'); u.putalpha(Image.fromarray(a.astype(np.uint8))); u=u.crop(u.getbbox())
    sc=min(1.0,1600/u.height); u=u.resize((int(u.width*sc),int(u.height*sc)),Image.LANCZOS); u.save(out); print(k,u.size,flush=True)
print('FIN')
