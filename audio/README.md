Audio source: <https://youtu.be/1eC6rPOkyAQ>.

```
youtube-dl -f 140 -o dreamer-1eC6rPOkyAQ.m4a 1eC6rPOkyAQ
ffmpeg -i dreamer-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libopus -b:a 80k -y dreamer.opus
ffmpeg -i dreamer-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libfdk_aac -b:a 80k -y dreamer.m4a
ffmpeg -i dreamer-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libvorbis -b:a 112k -y dreamer.ogg
ffmpeg -i dreamer-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libmp3lame -b:a 128k -y dreamer.mp3
```
