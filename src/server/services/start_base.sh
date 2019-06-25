#!/bin/sh

# determine how to start the services
python=python3

type python3.7 >/dev/null 2>&1
if [ $? -eq 0 ]; then
	python=python3.7
fi

# start services
trap "pkill -f $python" INT TERM QUIT

$python -m Pyro4.naming &
PIDN=$!
$python message_bus.py &
$python logger.py &
$python filesystem.py &
$python ws_server.py &

wait $PIDN
