cd /home/claude/ep13; I=Sounsouni_Episode13_LaFaute.mp4; O=Sounsouni_Episode13_LaFaute_leger.mp4
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 600k -preset fast -tune animation -pass 1 -passlogfile p13 -an -f mp4 /dev/null && \
ffmpeg -nostdin -y -loglevel error -i $I -c:v libx264 -b:v 600k -preset fast -tune animation -pass 2 -passlogfile p13 -c:a aac -b:a 96k -movflags +faststart $O && echo ENC_OK > enc.log
