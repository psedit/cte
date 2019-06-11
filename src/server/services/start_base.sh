#!/bin/sh
python3 -m Pyro4.naming &
PIDN=$!
sleep .5
python3 message_bus.py &
PIDM=$!
sleep .5
python3 filesystem.py &
PIDF=$!
sleep .5
python3 -m cProfile -o out.prof websocket_server.py &
PIDW=$1

trap 'pkill python3' INT TERM QUIT

wait $PIDW
wait $PIDF
wait $PIDM
wait $PIDN
