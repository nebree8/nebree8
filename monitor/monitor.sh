#!/usr/bin/bash

# Turn off monitor sleep
xset s 0 0
xset s off

setfont /usr/share/consolefonts/Lat3-TerminusBold32x16.psf.gz

watch 'cat data/queue.txt'
