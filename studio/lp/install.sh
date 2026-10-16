#!/bin/bash
# Installe LivePortrait (outil libre de KwaiVGI) pour que l'application tourne les têtes / ouvre les bouches toute seule.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); LPH=${LP_HOME:-$HERE/home}; mkdir -p "$LPH"
[ -d "$LPH/src" ] || git clone --depth 1 https://github.com/KwaiVGI/LivePortrait.git "$LPH/src"
pip install -q onnxruntime opencv-python-headless imageio imageio-ffmpeg pyyaml tyro scikit-image lmdb rich ffmpeg-python pykalman huggingface_hub
[ -d "$LPH/src/pretrained_weights/liveportrait" ] || python -c "from huggingface_hub import snapshot_download; snapshot_download('KwaiVGI/LivePortrait', local_dir='$LPH/src/pretrained_weights', allow_patterns=['insightface/*','liveportrait/*'])"
echo "LivePortrait prêt dans $LPH"
