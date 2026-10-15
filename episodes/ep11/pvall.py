import sys
exec(open('render.py').read().split("if __name__=='__main__':")[0])
from PIL import Image, ImageDraw
items=[x.split(':') for x in open('shots_t.txt').read().split()]
a,b=int(sys.argv[1]),int(sys.argv[2]); items=items[a:b]
ims=[]
for n,t in items:
    try: im=frame_at(float(t)).convert('RGB').resize((216,384))
    except Exception as e: im=Image.new('RGB',(216,384),(255,0,0)); print(n,e)
    ImageDraw.Draw(im).text((4,370),n,fill=(255,255,0)); ims.append(im)
S=Image.new('RGB',(216*11,384*((len(ims)+10)//11)))
for i,im in enumerate(ims): S.paste(im,((i%11)*216,(i//11)*384))
S.save(f'pvall_{a}.png')
