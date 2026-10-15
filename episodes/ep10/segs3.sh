#!/bin/bash
cd /home/claude/ep10; export RUNDUR=1.8034166666666502
lane(){ for s in $@; do e=$((s+400)); [ $e -gt 4645 ] && e=4645; f=n3_$(printf %05d $s).mp4
  [ -f $f.done ] || { python3 render.py seg $s $e $f > seg3_$s.log 2>&1 && touch $f.done; }; echo "fini $s" >> segs3.log; done; }
lane 1788 2588 3388 4188 &
lane 2188 2988 3788 &
wait; echo LANES_OK >> segs3.log
