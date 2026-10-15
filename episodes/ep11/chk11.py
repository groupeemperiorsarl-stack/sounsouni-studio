import json,sys
from PIL import Image, ImageDraw
M=json.load(open('mouth.json')); ks=sys.argv[1].split(',')
S=Image.new('RGB',(len(ks)*125,270),'white'); d=ImageDraw.Draw(S)
for i,k in enumerate(ks):
    x,y,w=M[k]
    for j,f in enumerate([f'hd/{k}.png',f'hd/{k}~alt.png']):
        im=Image.open(f).convert('RGBA'); W,H=im.size; r=int(max(W,H)*0.045); cx,cy=int(x*W),int(y*H)
        b=Image.new('RGBA',im.size,(0,200,0,255)); b.alpha_composite(im); S.paste(b.crop((cx-r,cy-r,cx+r,cy+r)).convert('RGB').resize((120,120)),(i*125,15+j*125))
    d.text((i*125+40,1),k,fill=(255,0,0))
S.save('chk.png')
