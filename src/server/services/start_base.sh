#!/bin/sh
python3.7 -m Pyro4.naming &
PIDN=$!
python3.7 message_bus.py &
PIDM=$!
python3.7 logger.py &
PIDL=$!
python3.7 filesystem.py &
PIDF=$!
python3.7 ws_server.py &
PIDW=$1

trap 'pkill -f python' INT TERM QUIT

wait $PIDN
