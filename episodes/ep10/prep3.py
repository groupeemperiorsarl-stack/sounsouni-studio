import sys, os, torch, numpy as np
sys.path.insert(0,'/home/claude/ep10')
from boxes3 import B
from PIL import Image, ImageFilter
from scipy import ndimage
from spandrel import ModelLoader
from rembg import remove, new_session
torch.set_num_threads(2)
M=ModelLoader().load_from_file('/home/claude/models/RealESRGAN_x4plus_anime_6B.pth').eval()
S=new_session('isnet-general-use')
def up(im,T=160,P=16):
    # agrandissement par tuiles pour limiter la mémoire
    a=np.array(im.convert('RGB')).astype(np.float32)/255; h,w,_=a.shape; out=np.zeros((h*4,w*4,3),np.float32)
    for y0 in range(0,h,T):
        for x0 in range(0,w,T):
            ya,yb=max(0,y0-P),min(h,y0+T+P); xa,xb=max(0,x0-P),min(w,x0+T+P)
            x=torch.from_numpy(a[ya:yb,xa:xb]).permute(2,0,1)[None]
            with torch.no_grad(): r=M(x)[0].clamp(0,1).permute(1,2,0).numpy()
            cy,cx=(y0-ya)*4,(x0-xa)*4; th,tw=min(T,h-y0)*4,min(T,w-x0)*4
            out[y0*4:y0*4+th,x0*4:x0*4+tw]=r[cy:cy+th,cx:cx+tw]
    out=Image.fromarray((out*255).round().astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(radius=2,percent=60,threshold=2))
for k,(src,box) in B.items():
    if os.path.exists(f'/home/claude/ep10/hd/{k}.png'): continue
    out=f'/home/claude/ep10/hd/{k}.png'
    if os.path.exists(out): continue
    u=up(Image.open(src).convert('RGB').crop(box))
    if k[0]!='D':
        sc=min(1.0,1400/u.height); small=u.resize((int(u.width*sc),int(u.height*sc)),Image.LANCZOS)
        a=remove(small,session=S,only_mask=True,post_process_mask=True).resize(u.size,Image.BILINEAR)
        a=np.asarray(a)
        lab,n=ndimage.label(a>60)
        if n>1:
            sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); keep=np.argmax(sz)+1
            a=np.where(ndimage.binary_dilation(lab==keep,iterations=3),a,0)
        u=u.convert('RGBA'); u.putalpha(Image.fromarray(a.astype(np.uint8))); u=u.crop(u.getbbox())
    u.save(out); print(k,u.size,flush=True)
print('FIN')
