#!/bin/bash

START_DIR=`pwd`

function sitrap () {
    kill $PIDN $PIDM $PIDL $PIDF $PIDW
    cd $START_DIR
}

function launch () {
    export PYRO_SERIALIZERS_ACCEPTED=pickle
    export PYRO_SERIALIZER=pickle
    cd services
    python3 -m Pyro4.naming &
    PIDN=$!
    python3 message_bus.py &
    PIDM=$!
    python3 logger.py &
    PIDL=$!
    python3 filesystem.py &
    PIDF=$!
    python3 ws_server.py &
    PIDW=$!

    trap 'kill $PIDN $PIDM $PIDL $PIDF $PIDW' INT TERM QUIT

    wait $PIDN
}

case $1 in
    "start")
        launch
        ;;
    "test")
        coverage run run_tests.py
        coverage report
        cd services
        python3 -m pytest test
        cd $START_DIR
        ;;
    *)
        echo "Usage: $0 (start|test)"
        ;;
esac
