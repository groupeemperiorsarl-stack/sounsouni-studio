cd /home/claude/ep14; I=Sounsouni_Episode14_RetourExpediteur.mp4; O=Sounsouni_Episode14_RetourExpediteur_leger.mp4
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 560k -preset fast -tune animation -pass 1 -passlogfile p14 -an -f mp4 /dev/null && \
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 560k -preset fast -tune animation -pass 2 -passlogfile p14 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK > enc.log
