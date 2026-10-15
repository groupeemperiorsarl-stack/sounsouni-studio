#!/bin/bash
cd /home/claude/ep11; export BURN=2.6258750000000193
lane(){ for s in $@; do e=$((s+400)); [ $e -gt 7286 ] && e=7286; f=n2_$(printf %05d $s).mp4
  [ -f $f.done ] || { python3 render.py seg $s $e $f > seg2_$s.log 2>&1 && touch $f.done; }; echo "fini $s" >> segs2.log; done; }
lane 5333 6133 6933 & lane 5733 6533 & wait; echo LANES_OK >> segs2.log
