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

python3 test/response_test_a.py &
python3 test/response_test_b.py &

trap 'pkill python3' INT

wait $PIDL
wait $PIDW
wait $PIDF
wait $PIDM
wait $PIDN
