import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.segmentation import watershed
from rembg import remove, new_session
S=new_session('isnet-general-use'); U='/root/.claude/uploads/62e3aaef-1437-5194-ac56-922a24a42de7/'
for f,pre in (('38032284-image.jpg','AWW'),('5b81bc31-image.jpg','AWB')):
    im=Image.open(U+f).convert('RGB'); a=np.asarray(remove(im,session=S,only_mask=True,post_process_mask=True)); m=a>60
    col=m[300:1000].sum(0); xs=[]
    for lo,hi in ((60,260),(330,520),(600,800)): xs.append(lo+int(np.argmax(col[lo:hi])))
    mk=np.zeros(m.shape,int)
    for j,x in enumerate(xs): mk[200:1000,x-15:x+15]=j+1
    mk[~m]=0
    lab=watershed(-ndimage.distance_transform_edt(m),mk,mask=m)
    for j in range(3):
        mm=ndimage.binary_opening(lab==j+1,iterations=1); u=im.convert('RGBA'); u.putalpha(Image.fromarray(np.where(mm,a,0).astype(np.uint8))); u.crop(u.getbbox()).save(f'hd/{pre}{j+1}.png')
    print(pre,xs)
