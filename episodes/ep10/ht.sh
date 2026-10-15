cd /home/claude/ep10
E="-c:v libx264 -pix_fmt yuv420p -crf 17 -preset medium -tune animation -r 30 -an"
ffmpeg -y -loglevel error -i Sounsouni_Episode10_LePari_v2.mp4 -vf "trim=start_frame=0:end_frame=1788,setpts=PTS-STARTPTS" $E head3.mp4 && echo H >> ht.log &
ffmpeg -y -loglevel error -i Sounsouni_Episode10_LePari_v2.mp4 -vf "trim=start_frame=3672,setpts=PTS-STARTPTS" $E tail3.mp4 && echo T >> ht.log &
wait; echo DONE >> ht.log
