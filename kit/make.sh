#!/bin/sh
# Builds one video. Run from its build folder (each video's own make.sh
# does): narration.py there names the video (NAME, TITLE), and the MP4,
# its .srt and its script land one folder up.
set -e
kit=$(cd "$(dirname "$0")" && pwd)
out=out
name=$(python3 -c "from narration import NAME; print(NAME)")
title=$(python3 -c "from narration import TITLE; print(TITLE)")
mp4=../$name.mp4

node "$kit/render-slides.cjs"
python3 "$kit/build.py"

pre="highpass=f=60,alimiter=limit=0.6:attack=3:release=60:level=disabled,aresample=48000"
ffmpeg -hide_banner -i $out/narration-raw.wav -af "$pre,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>$out/loudnorm.log
m() { sed -n "s/.*\"$1\" : \"\([^\"]*\)\".*/\1/p" $out/loudnorm.log; }
ffmpeg -hide_banner -loglevel error -y -i $out/narration-raw.wav \
  -af "$pre,loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:measured_I=$(m input_i):measured_TP=$(m input_tp):measured_LRA=$(m input_lra):measured_thresh=$(m input_thresh):offset=$(m target_offset),aresample=48000" \
  -ar 48000 $out/narration.wav

ffmpeg -hide_banner -loglevel error -y -i $out/video.mkv -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -tune stillimage -an $out/video.mp4
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $out/video.mkv)
ffmpeg -hide_banner -loglevel error -y -i $out/video.mp4 -i $out/narration.wav -i $out/captions.srt \
  -map 0:v -map 1:a -map 2:s -c:v copy -c:a aac -b:a 128k -c:s mov_text \
  -metadata:s:a:0 language=eng -metadata:s:s:0 language=eng -metadata:s:s:0 title=English \
  -metadata title="$title" -t "$dur" -movflags +faststart $mp4
cp $out/captions.srt ../$name.srt
python3 -c "
from narration import SECTIONS
print('\n\n'.join(s['title'] + '\n' + ' '.join(x[0] for x in s['sentences']) for s in SECTIONS))" > ../$name-script.txt
ffmpeg -hide_banner -i $mp4 -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E '^ +(I|Peak):'
ls -l $mp4
