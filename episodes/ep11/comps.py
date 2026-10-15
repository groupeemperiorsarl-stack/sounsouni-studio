import sys,numpy as np
from PIL import Image
from scipy import ndimage
for f in sys.argv[1:]:
    im=np.asarray(Image.open(f).convert('L')); m=im<235
    m=ndimage.binary_dilation(m,iterations=6)
    lab,n=ndimage.label(m); sl=ndimage.find_objects(lab)
    bx=[(s[1].start,s[0].start,s[1].stop,s[0].stop) for s in sl if (s[0].stop-s[0].start)*(s[1].stop-s[1].start)>15000]
    bx.sort(key=lambda b:(b[1]//150,b[0]))
    print(f.split('/')[-1][:8],im.shape,bx)
