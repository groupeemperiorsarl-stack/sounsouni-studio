from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np, math
def flower(R=180):
    S=R*2+40; c=S//2; L=Image.new('RGBA',(S,S),(0,0,0,0))
    for ring,(n,rad,ln,col) in enumerate([(12,0.62,0.42,(214,165,55)),(10,0.38,0.32,(236,192,80))]):
        for i in range(n):
            a=i/n*2*math.pi+ring*0.3; P=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(P)
            w=R*ln*0.55; h=R*ln
            for k in range(10):  # dégradé
                f=1-k/10; cc=tuple(int(col[j]*(0.8+0.35*(1-f))) for j in range(3))
                d.ellipse([c-w*f,c-R*rad-h*f,c+w*f,c-R*rad+h*f],fill=cc+(255,))
            d.ellipse([c-w,c-R*rad-h,c+w,c-R*rad+h],outline=(150,105,25,255),width=max(2,R//45))
            d.line([(c,c-R*rad-h*0.8),(c,c-R*rad+h*0.8)],fill=(170,120,35,255),width=max(2,R//60))
            L.alpha_composite(P.rotate(math.degrees(a),center=(c,c),resample=Image.BICUBIC))
    d=ImageDraw.Draw(L); r=R*0.2; d.ellipse([c-r,c-r,c+r,c+r],fill=(250,225,140,255),outline=(150,105,25,255),width=max(2,R//40))
    for i in range(16):
        a=i/16*2*math.pi; x=c+r*0.62*math.cos(a); y=c+r*0.62*math.sin(a); d.ellipse([x-R*0.03,y-R*0.03,x+R*0.03,y+R*0.03],fill=(255,248,215,255))
    # relief brodé
    g=L.convert('L').filter(ImageFilter.EMBOSS); g=ImageChops.blend(g,Image.new('L',g.size,128),0.4)
    rgb=np.array(L).astype(float); e=(np.array(g).astype(float)-128)/128; rgb[...,:3]=np.clip(rgb[...,:3]*(1+0.35*e[...,None]),0,255)
    out=Image.fromarray(rgb.astype(np.uint8)); sh=Image.new('RGBA',out.size,(0,0,0,0)); sh.putalpha(out.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda p:p*0.45))
    base=Image.new('RGBA',(S+8,S+8),(0,0,0,0)); base.alpha_composite(Image.merge('RGBA',[Image.new('L',sh.size,40)]*3+[sh.getchannel('A')]),(6,8)); base.alpha_composite(out,(0,0)); return base
if __name__=='__main__':
    from scipy import ndimage
    d=Image.open('hd/ROBEH.png'); x=np.array(d); m=x[...,3]>0
    hole=ndimage.binary_dilation(ndimage.binary_fill_holes(m)&~m,iterations=14); y=x.copy(); y[hole,:3]=x[m&~hole][:,:3].mean(0); y[hole,3]=255
    im=Image.fromarray(y); im.paste(im.filter(ImageFilter.GaussianBlur(10)),(0,0),Image.fromarray((hole*255).astype(np.uint8)))
    f=flower(150); im.alpha_composite(f,(233-f.width//2,756-f.height//2)); im.save('hd/ROBEF.png')
    b=Image.new('RGBA',im.size,(120,160,120,255)); b.alpha_composite(im); b.thumbnail((300,600)); b.save('/tmp/claude-0/robef.png')
