cd /home/claude/ep10; I=Sounsouni_Episode10_LePari_v3.mp4; O=Sounsouni_Episode10_LePari_v3_leger.mp4
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 760k -preset medium -tune animation -pass 1 -an -f mp4 /dev/null && \
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 760k -preset medium -tune animation -pass 2 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK >> enc3.log
