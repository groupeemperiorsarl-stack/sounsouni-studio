# Installation (machine Linux, sans carte graphique)

Testé sur : Python 3.13, 2 CPU Intel Xeon (AVX-512), 8 Go de RAM.

## 1. Outils de base
```bash
pip install --break-system-packages rembg[cpu] spandrel torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
pip install --break-system-packages faster-whisper librosa soundfile onnxruntime onnx openvino tyro pykalman \
    imageio-ffmpeg ffmpeg-python lmdb rich pyyaml huggingface_hub "transformers<5" scipy opencv-python
```
Modèles d'images : `RealESRGAN_x4plus_anime_6B.pth` (agrandissement) et `isnet-general-use.onnx` (détourage, `U2NET_HOME`).

## 2. LivePortrait (expressions du visage)
```bash
git clone --depth 1 https://github.com/KwaiVGI/LivePortrait.git lp/src
cd lp/src && git apply ../../patches/liveportrait.patch
python3 -c "from huggingface_hub import snapshot_download as s; s('KlingTeam/LivePortrait', local_dir='pretrained_weights', ignore_patterns=['*animal*','docs/*'])"
```
Sur CPU : `flag_force_cpu=True` et **`flag_use_half_precision=False`** (sinon extrêmement lent).
Accélération : le décodeur (`spade_generator`) est converti en OpenVINO (`spade.xml`, voir `tools/faces/lpgen.py`).

## 3. JoyVASA (synchronisation des lèvres et mouvements de tête à partir de la voix)
```bash
git clone --depth 1 https://github.com/jdh-algo/JoyVASA.git jv/src
cd jv/src && git apply ../../patches/joyvasa.patch
mkdir -p pretrained_weights
ln -s <chemin>/lp/src/pretrained_weights/liveportrait pretrained_weights/liveportrait
ln -s <chemin>/lp/src/pretrained_weights/insightface pretrained_weights/insightface
python3 -c "from huggingface_hub import snapshot_download as s; s('jdh-algo/JoyVASA', local_dir='pretrained_weights/JoyVASA'); s('TencentGameMate/chinese-hubert-base', local_dir='pretrained_weights/chinese-hubert-base', allow_patterns=['*.json','*.bin','*.txt'])"
ln -s chinese-hubert-base "pretrained_weights/TencentGameMate:chinese-hubert-base"
```
Lancement (voir `tools/faces/joyvasa_runall.sh`) :
```bash
JV_STEP=12 JV_OV=1 JV_FRAMES=sortie/L0 python3 inference.py -r image.png -a voix.wav --animation_mode human \
  --cfg_scale 2.0 --flag-force-cpu --no-flag-use-half-precision --flag-pasteback --flag-do-crop --flag-stitching -o sortie/vid
```
- `JV_STEP=12` : calcule 1 image sur 12 (≈ 2 images/s) ; `JV_STEP=1` : 25 images/s.
- `JV_OV=1` : décodeur OpenVINO ; `JV_FRAMES` : enregistre chaque image en PNG.

## 4. Chatterbox (voix)
Dans un environnement séparé (il impose torch 2.6) :
```bash
python3 -m venv tts/venv
tts/venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu chatterbox-tts "setuptools<81"
tts/venv/bin/python tools/voices/gen5.py lignes.txt
```
Format de `lignes.txt` : `sortie.wav|voix_reference.wav|exaggeration|cfg|Texte de la réplique`
