#!/bin/sh
python3 -m Pyro4.naming &
PIDN=$!
python3 message_bus.py &
PIDM=$!
python3 logger.py &
PIDL=$!
python3 filesystem.py &
PIDF=$!
python3 websocket_server.py &
PIDW=$1

trap 'pkill python3' INT TERM QUIT

wait $PIDN
