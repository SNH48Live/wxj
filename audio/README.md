Audio source: <https://youtu.be/1eC6rPOkyAQ>.

```
youtube-dl -f 140 -o 梦想家-1eC6rPOkyAQ.m4a 1eC6rPOkyAQ
ffmpeg -i 梦想家-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libopus -b:a 80k -y 梦想家.opus
ffmpeg -i 梦想家-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libfdk_aac -b:a 80k -y 梦想家.m4a
ffmpeg -i 梦想家-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libvorbis -b:a 112k -y 梦想家.ogg
ffmpeg -i 梦想家-1eC6rPOkyAQ.m4a -ss 4 -t 177 -c:a libmp3lame -b:a 128k -y 梦想家.mp3
```
