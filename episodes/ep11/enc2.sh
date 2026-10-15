cd /home/claude/ep11; I=Sounsouni_Episode11_LeHautParleur_v2.mp4; O=Sounsouni_Episode11_LeHautParleur_v2_leger.mp4
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 680k -preset medium -tune animation -pass 1 -passlogfile p12 -an -f mp4 /dev/null && \
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 680k -preset medium -tune animation -pass 2 -passlogfile p12 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK >> enc2.log
