#!/bin/bash
cd /home/claude/ep14; N=10719
lane(){ for s in $@; do e=$((s+400)); [ $e -gt $N ] && e=$N; f=s_$(printf %05d $s).mp4
  [ -f $f.done ] || { python3 render14.py seg $s $e $f > seg_$s.log 2>&1 && touch $f.done; }; echo "fini $s" >> segs.log; done; }
A=""; B=""; i=0; for s in $(seq 0 400 $((N-1))); do if [ $((i%2)) -eq 0 ]; then A="$A $s"; else B="$B $s"; fi; i=$((i+1)); done
lane $A & lane $B & wait
rm -f list.txt; for s in $(seq 0 400 $((N-1))); do echo "file 's_$(printf %05d $s).mp4'" >> list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy ep14_silent.mp4 && ../mix.sh ep14_silent.mp4 ep14_voix.wav ep14_music.wav Sounsouni_Episode11_LeHautParleur.mp4 && echo ALL_OK >> segs.log
