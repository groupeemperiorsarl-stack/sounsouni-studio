#!/bin/bash
# mixage : musique baissée automatiquement sous les voix (sidechain), puis normalisation -14 LUFS
ffmpeg -y -loglevel error -i "$1" -i "$2" -i "$3" -filter_complex "[1:a]aresample=44100,asplit=2[v1][v2];[2:a]aresample=44100,volume=0.55[m];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart "$4"
