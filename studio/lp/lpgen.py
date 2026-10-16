import sys,time,os,functools
HERE=os.path.dirname(os.path.abspath(__file__)); LPH=os.environ.get('LP_HOME') or (os.path.join(HERE,'home') if os.path.isdir(os.path.join(HERE,'home','src')) else '/home/claude/lp')
sys.path.insert(0,os.path.join(HERE,'stub')); sys.path.insert(0,os.path.join(LPH,'src')); os.chdir(os.path.join(LPH,'src'))
import torch; torch.set_num_threads(2)
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.gradio_pipeline import GradioPipeline
import cv2, numpy as np
def pf(c,kw): return c(**{k:v for k,v in kw.items() if k in c.__dataclass_fields__})
args=ArgumentConfig(); args.flag_force_cpu=True; args.flag_use_half_precision=False
P=GradioPipeline(inference_cfg=pf(InferenceConfig,args.__dict__),crop_cfg=pf(CropConfig,args.__dict__),args=args)
SP=os.path.join(LPH,'spade.xml')
if os.path.exists(SP):   # version accélérée (OpenVINO) si disponible, sinon PyTorch
    import openvino as ov
    core=ov.Core(); core.set_property('CPU',{'INFERENCE_NUM_THREADS':2}); CM=core.compile_model(SP,'CPU')
    class OVSpade(torch.nn.Module):
        def forward(self,feature): return torch.from_numpy(CM(feature.numpy())[0])
    P.live_portrait_wrapper.spade_generator=OVSpade()
_prep=P.prepare_retargeting_image; CACHE={}
def prep(img,p,y,r,s,flag_do_crop=True):
    k=(img,p,y,r,s)
    if k not in CACHE: CACHE[k]=_prep(img,p,y,r,s,flag_do_crop=flag_do_crop)
    return CACHE[k]
P.prepare_retargeting_image=prep
SRC=None
# jobs: out|src|eye|lip|pitch|yaw|roll|smile|eyebrow|eee|woo   (eye/lip = 'x' => source value)
for line in open(sys.argv[1]):
    if not line.strip(): continue
    f=line.strip().split('|')
    if len(f)==11: f=f[:9]+['0']+f[9:11]+['0','0','0']
    out,src,e,l,p,y,r,sm,eb,l0,l1,l2,l3,ex,ey=f
    try:
        if src!=SRC: er,lr=P.init_retargeting_image(2.3,0,0,src); SRC=src
        e2=er if e=='x' else float(e); l2_=lr if l=='x' else float(l)
        if os.path.exists(out): continue
        t=time.time(); o,blend=P.execute_image_retargeting(e2,l2_,float(p),float(y),float(r),0,0,1,float(l0),float(l1),float(l2),float(l3),float(sm),0,float(eb),float(ex),float(ey),src,2.3)
    except Exception as err:
        print('ECHEC',out,repr(err)[:120],flush=True); SRC=None; continue
    os.makedirs(os.path.dirname(out),exist_ok=True); cv2.imwrite(out,cv2.cvtColor(blend,cv2.COLOR_RGB2BGR)); print(out,round(time.time()-t,1),flush=True)
