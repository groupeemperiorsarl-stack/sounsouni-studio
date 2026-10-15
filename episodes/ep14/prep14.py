import numpy as np
from PIL import Image
from scipy import ndimage
from rembg import remove, new_session
S=new_session('isnet-general-use'); U='/root/.claude/uploads/62e3aaef-1437-5194-ac56-922a24a42de7/'
for f,k in (('e15ce6e1-image.jpg','BBOX'),('afb79702-image.jpg','SLIP'),('75de2fc4-image.jpg','CATCH'),('96c5f94d-image.jpg','DEAT')):
    im=Image.open(U+f).convert('RGB'); a=np.asarray(remove(im,session=S,only_mask=True,post_process_mask=True))
    lab,n=ndimage.label(a>60)
    if n>1:
        sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); big=[i+1 for i,s in enumerate(sz) if s>0.02*sz.max()]; a=np.where(ndimage.binary_dilation(np.isin(lab,big),iterations=3),a,0)
    u=im.convert('RGBA'); u.putalpha(Image.fromarray(a.astype(np.uint8))); u=u.crop(u.getbbox()); u.save(f'hd/{k}.png'); print(k,u.size,flush=True)
