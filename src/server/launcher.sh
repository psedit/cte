#!/bin/bash

START_DIR=`pwd`

function sitrap () {
    kill $PIDN $PIDM $PIDL $PIDF $PIDW
    cd $START_DIR
}

function launch () {
    export PYRO_SERIALIZERS_ACCEPTED=pickle
    export PYRO_SERIALIZER=pickle
    python3 -m Pyro4.naming &
    PIDN=$!
    python3 -m services message_bus &
    PIDM=$!
    python3 -m services logger &
    PIDL=$!
    python3 -m services filesystem &
    PIDF=$!
    python3 -m services ws_server &
    PIDW=$!

    trap 'kill $PIDN $PIDM $PIDL $PIDF $PIDW' INT TERM QUIT

    wait $PIDN
}

case $1 in
    "start")
        launch
        ;;
    "test")
        python3 -m pytest --cov-report term-missing --cov=services test/
        ;;
    *)
        echo "Usage: $0 (start|test)"
        ;;
esac
