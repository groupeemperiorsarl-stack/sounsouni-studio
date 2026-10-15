import sys; sys.argv=['x','none']
exec(open('/home/claude/ep13/render13.py').read().split("if __name__=='__main__':")[0])
names=sys.stdin.read().split() if False else None
import os
seen=[];ims=[]
for n,t0,dd,li in T:
    if n in seen: continue
    seen.append(n); fr=frame_at(t0+dd*0.7).convert('RGB'); fr.thumbnail((216,384)); ims.append((n,fr))
from PIL import ImageDraw
cols=10; c=Image.new('RGB',(cols*216,((len(ims)+cols-1)//cols)*404),'white'); d=ImageDraw.Draw(c)
for i,(n,im) in enumerate(ims): c.paste(im,((i%cols)*216,(i//cols)*404)); d.text(((i%cols)*216+4,(i//cols)*404+386),n,fill='black')
c.save('/tmp/claude-0/pv13.png'); print(len(ims))
