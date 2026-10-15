cd /home/claude/ep12; I=Sounsouni_Episode12_LaCoupure.mp4; O=Sounsouni_Episode12_LaCoupure_leger.mp4
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 700k -preset fast -tune animation -pass 1 -passlogfile p12 -an -f mp4 /dev/null && \
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 700k -preset fast -tune animation -pass 2 -passlogfile p12 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK > enc.log
