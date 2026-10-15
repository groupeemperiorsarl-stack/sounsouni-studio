cd /home/claude/ep11; I=Sounsouni_Episode11_LeHautParleur.mp4; O=Sounsouni_Episode11_LeHautParleur_leger.mp4
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 700k -preset medium -tune animation -pass 1 -passlogfile p11 -an -f mp4 /dev/null && \
ffmpeg -y -loglevel error -i $I -c:v libx264 -b:v 700k -preset medium -tune animation -pass 2 -passlogfile p11 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK >> enc.log
