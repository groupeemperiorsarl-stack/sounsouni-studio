set -e
git clone -q --depth 1 https://github.com/jdh-algo/JoyVASA.git jv
cd jv && git apply ../patches/joyvasa.patch && cd ..
W=~/jv-weights
if [ ! -f $W/ok ]; then
python - <<'PY'
import os
from huggingface_hub import snapshot_download as dl
W=os.path.expanduser('~/jv-weights')
dl('KlingTeam/LivePortrait', local_dir=W, ignore_patterns=['*animal*','docs/*','*.md'])
dl('jdh-algo/JoyVASA', local_dir=W+'/JoyVASA')
dl('TencentGameMate/chinese-hubert-base', local_dir=W+'/chinese-hubert-base', allow_patterns=['*.json','*.bin','*.txt'])
PY
touch $W/ok
fi
ln -sfn $W jv/pretrained_weights
ln -sfn chinese-hubert-base "$W/TencentGameMate:chinese-hubert-base"
