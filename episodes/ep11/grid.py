import sys
from PIL import Image,ImageDraw
ks=sys.argv[1].split(','); H=420
ims=[]
for k in ks:
    im=Image.open(f'hd/{k}c.png' if __import__('os').path.exists(f'hd/{k}c.png') else f'hd/{k}.png').convert('RGBA')
    b=Image.new('RGBA',im.size,(0,150,0,255)); b.alpha_composite(im); b=b.convert('RGB'); w=int(b.width*H/b.height); b=b.resize((w,H)); d=ImageDraw.Draw(b)
    for i in range(1,10):
        d.line([(0,H*i/10),(w,H*i/10)],fill=(255,255,0)); d.line([(w*i/10,0),(w*i/10,H)],fill=(255,255,0))
    d.text((3,3),k,fill=(255,0,0)); ims.append(b)
S=Image.new('RGB',(sum(i.width for i in ims)+5*len(ims),H),(0,0,0)); x=0
for i in ims: S.paste(i,(x,0)); x+=i.width+5
S.save('grid.png')
