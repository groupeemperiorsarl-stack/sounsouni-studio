# Bouche ouverte : on recale la version « ouverte » sur la version « fermée » et on ne garde que la zone de la bouche
import numpy as np, cv2, json
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import binary_fill_holes, label, binary_dilation
def fill(im):
    a=np.asarray(im).copy(); a[...,3][binary_fill_holes(a[...,3]>100)]=255; return Image.fromarray(a)
def flat(im): return np.asarray(Image.alpha_composite(Image.new('RGBA',im.size,(255,255,255,255)),im).convert('L'))
# clé : (zone où chercher la bouche en fractions x0,y0,x1,y1)
P={'TA':(0.3,0.15,0.75,0.33),'GR':(0.3,0.15,0.75,0.33),'CR':(0.3,0.08,0.75,0.22),'ME':(0.25,0.08,0.75,0.22),'FT1':(0.25,0.1,0.75,0.24),'FT2':(0.25,0.1,0.75,0.24),'FT3':(0.25,0.1,0.75,0.24),'FT4':(0.25,0.08,0.75,0.2),'FT5':(0.25,0.08,0.75,0.2),'BW':(0.3,0.06,0.7,0.16),'BQ':(0.3,0.06,0.7,0.16)}
RW={'TA':0.035,'GR':0.035,'CR':0.03,'ME':0.03,'FT4':0.025,'FT5':0.025}
C={}
res={}
for k,(x0,y0,x1,y1) in P.items():
    O=fill(Image.open(f'hd/{k}c.png').convert('RGBA')); N=fill(Image.open(f'hd/{k}o.png').convert('RGBA')); W,H=O.size
    s=1000/max(W,H); og=cv2.resize(flat(O),None,fx=s,fy=s); ng=cv2.resize(flat(N),None,fx=s,fy=s)
    sift=cv2.SIFT_create(); k1,d1=sift.detectAndCompute(ng,None); k2,d2=sift.detectAndCompute(og,None)
    good=[a for a,b in cv2.BFMatcher().knnMatch(d1,d2,k=2) if a.distance<0.75*b.distance]
    A,inl=cv2.estimateAffinePartial2D(np.float32([k1[g.queryIdx].pt for g in good]),np.float32([k2[g.trainIdx].pt for g in good]),method=cv2.RANSAC,ransacReprojThreshold=3)
    A[:,2]/=s; Nw=Image.fromarray(cv2.warpAffine(np.asarray(N),A,(W,H),flags=cv2.INTER_CUBIC))
    d=np.abs(flat(O).astype(float)-flat(Nw).astype(float)); zone=np.zeros_like(d,bool); zone[int(y0*H):int(y1*H),int(x0*W):int(x1*W)]=True
    m=(d>45)&zone; lab,n=label(binary_dilation(m,iterations=6))
    if n==0: print(k,'pas de différence'); continue
    big=np.argmax(np.bincount(lab.ravel())[1:])+1; ys,xs=np.nonzero(lab==big); cx,cy=xs.mean(),ys.mean(); rw=RW.get(k,0.024)*H; rh=rw*0.8
    if k in C: cx,cy=C[k][0]*W,C[k][1]*H
    # recalage fin autour de la bouche (corrélation de phase)
    b=int(rw*3.5); y_0,y_1,x_0,x_1=int(cy-b),int(cy+b),int(cx-b),int(cx+b)
    (dx,dy),_=cv2.phaseCorrelate(np.float32(flat(Nw)[y_0:y_1,x_0:x_1]),np.float32(flat(O)[y_0:y_1,x_0:x_1]))
    if abs(dx)<b*0.5 and abs(dy)<b*0.5: Nw=Image.fromarray(cv2.warpAffine(np.asarray(Nw),np.float32([[1,0,dx],[0,1,dy]]),(W,H),flags=cv2.INTER_CUBIC))
    mk=Image.new('L',(W,H),0); ImageDraw.Draw(mk).ellipse([cx-rw,cy-rh,cx+rw,cy+rh],fill=255); mk=mk.filter(ImageFilter.GaussianBlur(max(6,rw*0.25)))
    p=Nw.copy(); p.putalpha(Image.fromarray(np.minimum(np.minimum(np.asarray(mk),np.asarray(O.getchannel('A'))),np.asarray(Nw.getchannel('A'))))); out=O.copy(); out.alpha_composite(p)
    O.save(f'hd/{k}.png'); out.save(f'hd/{k}~alt.png'); res[k]=[round(float(cx/W),4),round(float(cy/H),4),round(float(rw/W),4)]; print(k,int(inl.sum()),res[k],flush=True)
import json as _j; G=_j.load(open('mouth_good.json')); G.update(res); _j.dump(G,open('mouth.json','w'))
