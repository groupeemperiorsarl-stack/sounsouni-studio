cd /home/claude/ep11; V=Sounsouni_Episode11_LeHautParleur.mp4
E="-c:v libx264 -pix_fmt yuv420p -crf 17 -preset medium -tune animation -r 30 -an"
ffmpeg -y -loglevel error -i $V -vf "trim=start_frame=0:end_frame=5333,setpts=PTS-STARTPTS" $E head2.mp4 && echo H >> ht.log
ffmpeg -y -loglevel error -i $V -vf "trim=start_frame=6923,setpts=PTS-STARTPTS" $E tail2.mp4 && echo T >> ht.log
