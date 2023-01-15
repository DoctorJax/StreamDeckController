#!/bin/bash

streamdeckstart() {
    kill $(cat /tmp/.streamdeck.sh.pid)
    reset
    cd ~/GitRepos/.StreamDeckController || exit
    python main.py &
    echo $! > /tmp/.streamdeck.sh.pid
}

reset() {
    usbreset-device 0fd9:006d
}

case "$1" in
   -r) reset;;
    *) streamdeckstart;;
esac
