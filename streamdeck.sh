#!/bin/bash

streamdeckstart() {
    cd ~/GitRepos/.StreamDeckController || exit
    python main.py
}

reset() {
    usbreset-device 0fd9:006d
}

case "$1" in
   -r) reset;;
    *) streamdeckstart;;
esac
