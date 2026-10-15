import numpy as np
from PIL import Image
from scipy import ndimage
from rembg import remove, new_session
S=new_session('isnet-general-use'); U='/root/.claude/uploads/62e3aaef-1437-5194-ac56-922a24a42de7/'
for f,pre in (('38032284-image.jpg','AWW'),('5b81bc31-image.jpg','AWB')):
    im=Image.open(U+f).convert('RGB'); a=np.asarray(remove(im,session=S,only_mask=True,post_process_mask=True))
    lab,n=ndimage.label(a>60); sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); top=np.argsort(sz)[::-1][:3]+1
    print(pre,n,sorted(sz)[-4:])
    cx=[ndimage.center_of_mass(lab==t)[1] for t in top]
    for j,t in enumerate([t for _,t in sorted(zip(cx,top))]):
        m=ndimage.binary_dilation(lab==t,iterations=2); u=im.convert('RGBA'); u.putalpha(Image.fromarray(np.where(m,a,0).astype(np.uint8))); u.crop(u.getbbox()).save(f'hd/{pre}{j+1}.png')
