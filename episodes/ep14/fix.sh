cd /home/claude/ep14
for s in 800 1200; do f=s_$(printf %05d $s).mp4; python3 render14.py seg $s $((s+400)) $f > seg_$s.log 2>&1 && touch $f.done; done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy ep14_silent.mp4 && ../mix.sh ep14_silent.mp4 ep14_voix.wav ep14_music.wav Sounsouni_Episode14_RetourExpediteur.mp4 && echo FIX_OK > fix.log
