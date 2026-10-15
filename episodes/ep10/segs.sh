#!/bin/bash
cd /home/claude/ep10; N=6771; rm -f list.txt

s=0
while [ $s -lt $N ]; do
  e=$((s+400)); f=s4_$(printf %05d $s).mp4
  [ -f $f.done ] || { python3 render.py seg $s $e $f > seg.log 2>&1 && touch $f.done; }
  [ -f $f.done ] && echo "file '$f'" >> list.txt || echo "ECHEC $s" >> segs.log
  echo "morceau $s fini" >> segs.log; s=$e
done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy ep10_silent.mp4 && ../mix.sh ep10_silent.mp4 ep10_voix.wav ep10_music.wav Sounsouni_Episode10_LePari_v2.mp4 && echo ALL_OK >> segs.log
