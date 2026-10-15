import numpy as np
from PIL import Image
from scipy import ndimage
from rembg import remove, new_session
S=new_session('isnet-general-use')
U='/root/.claude/uploads/62e3aaef-1437-5194-ac56-922a24a42de7/'
def cut(im):
    a=np.asarray(remove(im,session=S,only_mask=True,post_process_mask=True))
    lab,n=ndimage.label(a>60)
    if n>1:
        sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); keep=np.argmax(sz)+1; a=np.where(ndimage.binary_dilation(lab==keep,iterations=3),a,0)
    u=im.convert('RGBA'); u.putalpha(Image.fromarray(a.astype(np.uint8))); return u.crop(u.getbbox())
F=Image.open(U+'38032284-image.jpg').convert('RGB'); B=Image.open(U+'5b81bc31-image.jpg').convert('RGB'); print(F.size,B.size)
xs=[(0,300),(285,575),(555,848)]
for i,(a,b) in enumerate(xs):
    cut(F.crop((a,0,b,F.height))).save(f'hd/AWW{i+1}.png'); cut(B.crop((a,0,b,B.height))).save(f'hd/AWB{i+1}.png')
m=cut(Image.open(U+'fc96dd34-image.jpg').convert('RGB')); m.save('hd/MUTE.png'); print('ok',m.size)
