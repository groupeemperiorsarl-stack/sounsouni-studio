cd /home/claude/jv/src
run(){ [ -f ../ep/$1.done ] && return; JV_STEP=${JV_STEP:-1} JV_OV=1 JV_FRAMES=../ep/$1 python3 inference.py -r $2 -a $3 --animation_mode human --cfg_scale 2.0 --flag-force-cpu --no-flag-use-half-precision --flag-pasteback --flag-do-crop --flag-stitching -o ../ep/vid > ../ep/$1.log 2>&1 && touch ../ep/$1.done; echo "$1 $(date +%T)" >> ../ep/progress; }
A=/home/claude/tts/ep12t; S=/home/claude/lp/jsrc
run L0 $S/mod_taq.png $A/L0.wav
run L1 $S/bak_gene.png $A/L1.wav
run L2 $S/mod_taq.png $A/L2.wav
run L3 $S/bak_idee.png $A/L3.wav
run L4 $S/awa_froide.png $A/L4.wav
run L5 $S/bak_pan.png $A/L5.wav
run L6 $S/mod_rire.png $A/L6.wav
echo ALL >> ../ep/progress
