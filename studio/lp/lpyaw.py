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
import json
res = {}
for line in open(sys.argv[1]):
    if not line.strip(): continue
    key, src = line.strip().split('|')
    try:
        r = _prep(src, 0, 0, 0, 2.3, flag_do_crop=True); info = r[4]
        res[key] = [float(info['yaw']), float(info['pitch'])]
    except Exception as e: res[key] = None
    print(key, res[key], flush=True)
json.dump(res, open(sys.argv[2], 'w'))
