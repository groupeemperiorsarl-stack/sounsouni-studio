# Travail envoyé sur Kaggle (carte graphique gratuite) par studio/poses_ia.py — ne pas lancer à la main.
# Modèle : Qwen-Image-Edit-2509 (licence Apache 2.0, usage commercial permis), version allégée GGUF + accélérateur Lightning 8 étapes.
# Deux cartes T4 : le lecteur d'image et de texte (compressé 4 bits) sur la 2e, le dessinateur sur la 1re.
import os, sys, io, json, time, base64, subprocess, traceback
T0 = time.time(); LOG = {'etapes': [], 'images': [], 'erreurs': []}
OUT = '/kaggle/working'
def log(m):
    LOG['etapes'].append(f'{time.time() - T0:7.1f}s {m}'); print(m, flush=True)
    json.dump(LOG, open(f'{OUT}/journal.json', 'w'), ensure_ascii=False, indent=1)
JOB = json.loads(base64.b64decode('__JOB__').decode())
try:
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', '-q', 'torchao'])   # version de Kaggle incompatible avec diffusers (inutile ici)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'diffusers==0.41.0', 'gguf', 'bitsandbytes', 'peft', 'accelerate'], check=True)
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline, QwenImageTransformer2DModel, GGUFQuantizationConfig
    from diffusers.pipelines.qwenimage.pipeline_qwenimage_edit_plus import calculate_dimensions, CONDITION_IMAGE_SIZE
    from transformers import Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig
    log(f'outils prêts, {torch.cuda.device_count()} cartes : ' + ', '.join(torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())))
    REPO = 'Qwen/Qwen-Image-Edit-2509'; F16 = torch.float16
    te = Qwen2_5_VLForConditionalGeneration.from_pretrained(REPO, subfolder='text_encoder', torch_dtype=F16, device_map={'': 1},
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=F16))
    log('lecteur texte/image chargé')
    tr = None
    for q in JOB.get('quants', ['Q4_0', 'Q3_K_M']):
        try:
            tr = QwenImageTransformer2DModel.from_single_file(f'https://huggingface.co/QuantStack/Qwen-Image-Edit-2509-GGUF/blob/main/Qwen-Image-Edit-2509-{q}.gguf',
                quantization_config=GGUFQuantizationConfig(compute_dtype=F16), torch_dtype=F16, config=REPO, subfolder='transformer')
            LOG['quant'] = q; break
        except Exception as e: LOG['erreurs'].append(f'{q}: {e}'); log(f'{q} impossible')
    pipe = QwenImageEditPlusPipeline.from_pretrained(REPO, transformer=tr, text_encoder=te, torch_dtype=F16)
    steps, cfg = 30, 4.0
    if JOB.get('lightning', True):
        try:
            pipe.load_lora_weights('lightx2v/Qwen-Image-Lightning', weight_name='Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors')
            steps, cfg = 8, 1.0; LOG['lightning'] = True
        except Exception as e: LOG['erreurs'].append(f'lightning: {e}'); LOG['lightning'] = False
    pipe.transformer.to('cuda:0'); pipe.vae.to('cuda:0')
    log(f'dessinateur chargé ({LOG.get("quant")}, {steps} étapes)')
    NEG = JOB.get('negatif', ' ')
    for t in JOB['taches']:
        refs = [Image.open(io.BytesIO(base64.b64decode(b))).convert('RGB') for b in t['refs']]
        cond = []
        for im in refs:
            w, h = calculate_dimensions(CONDITION_IMAGE_SIZE, im.width / im.height); cond.append(pipe.image_processor.resize(im, h, w))
        with torch.no_grad():
            pe, pm = pipe.encode_prompt(prompt=t['prompt'], image=cond, device=torch.device('cuda:1'))
            extra = {}
            if cfg > 1:
                ne, nm = pipe.encode_prompt(prompt=NEG, image=cond, device=torch.device('cuda:1'))
                extra = dict(negative_prompt_embeds=ne.to('cuda:0'), negative_prompt_embeds_mask=None if nm is None else nm.to('cuda:0'))
        for seed in t['seeds']:
            t1 = time.time()
            try:
                im = pipe(image=refs, prompt_embeds=pe.to('cuda:0'), prompt_embeds_mask=None if pm is None else pm.to('cuda:0'), true_cfg_scale=cfg,
                          num_inference_steps=steps, height=t.get('h', 1344), width=t.get('w', 768),
                          generator=torch.Generator('cuda:0').manual_seed(seed), **extra).images[0]
                import numpy as np
                a = np.asarray(im); bad = bool(a.std() < 3)   # image noire ou unie = calcul raté
                f = f"{t['nom']}__{seed}.png"; im.save(f'{OUT}/{f}')
                LOG['images'].append({'fichier': f, 'tache': t['nom'], 'graine': seed, 'secondes': round(time.time() - t1, 1), 'ratee': bad})
                log(f"{f} en {time.time() - t1:.0f} s{' (RATÉE)' if bad else ''}")
            except Exception as e:
                LOG['erreurs'].append(f"{t['nom']} {seed}: {e}"); log(f"{t['nom']} {seed} : erreur {e}"); torch.cuda.empty_cache()
    log('fini')
except Exception:
    LOG['erreurs'].append(traceback.format_exc()); log('arrêt sur erreur')
