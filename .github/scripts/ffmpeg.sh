#!/bin/bash
# Installe ffmpeg sans passer par apt : sur certaines machines GitHub, « apt-get install ffmpeg » met jusqu'à 16 minutes
# (serveur Ubuntu lent) et toute la fabrication attend la plus lente. On prend la version toute prête publiée sur GitHub (quelques secondes).
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && { echo "ffmpeg déjà là"; exit 0; }
D=$HOME/ffmpeg; mkdir -p "$D"
for U in https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz \
         https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz; do
  if curl -fsSL --retry 3 --max-time 180 "$U" | tar xJ -C "$D" --strip-components=1 2>/dev/null && [ -x "$D/bin/ffmpeg" ]; then
    sudo ln -sf "$D/bin/ffmpeg" /usr/local/bin/ffmpeg; sudo ln -sf "$D/bin/ffprobe" /usr/local/bin/ffprobe
    echo "ffmpeg prêt : $(ffmpeg -version | head -1)"; exit 0; fi
  echo "téléchargement raté : $U"
done
echo "secours : apt (au plus 10 minutes)"; timeout 600 sudo apt-get install -y -qq ffmpeg > /dev/null
