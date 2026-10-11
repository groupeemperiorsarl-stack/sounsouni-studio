import sys,time,os
sys.path.insert(0,'/home/claude/lp/stub'); sys.path.insert(0,'/home/claude/lp/src')
import torch; torch.set_num_threads(2)
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.gradio_pipeline import GradioPipeline
import cv2, numpy as np
def pf(c,kw): return c(**{k:v for k,v in kw.items() if k in c.__dataclass_fields__})
args=ArgumentConfig(); args.flag_force_cpu=True; args.flag_use_half_precision=False
P=GradioPipeline(inference_cfg=pf(InferenceConfig,args.__dict__),crop_cfg=pf(CropConfig,args.__dict__),args=args)
src=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
er,lr=P.init_retargeting_image(2.3,0,0,src); print('ratios',er,lr,flush=True)
# name: (eye, lip, pitch,yaw,roll, l0,l1,l2,l3, smile,wink,eyebrow)
E0={'neutre':(er,lr,0,0,0,0,0,0,0,0,0,0),'cligne':(0.0,lr,0,0,0,0,0,0,0,0,0,0),'parle':(er,0.45,0,0,0,0,0,0,0,0,0,0),
   'sourire':(er,lr,0,0,0,0,0,0,0,1.0,0,0),'rire':(er,0.5,-6,0,0,0,0,0,0,1.3,0,4),'surpris':(0.5,0.4,0,0,0,0,0,0,0,0,0,12),
   'colere':(er*0.8,lr,4,0,0,0,0,0,0,-0.6,0,-12),'tete_gauche':(er,lr,0,-12,4,0,0,0,0,0.3,0,0),'oui':(er,lr,8,0,0,0,0,0,0,0.2,0,0)}
for k,(e,l,p,y,r,l0,l1,l2,l3,sm,wk,eb) in E.items():
    t=time.time()
    o,blend=P.execute_image_retargeting(e,l,p,y,r,0,0,1,l0,l1,l2,l3,sm,wk,eb,0,0,src,2.3)
    cv2.imwrite(f'{out}/{k}.png',cv2.cvtColor(blend,cv2.COLOR_RGB2BGR)); print(k,round(time.time()-t,1),flush=True)

