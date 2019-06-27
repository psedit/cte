#!/bin/bash

START_DIR=`pwd`
START_CMD=python3


function sitrap () {
    kill $PIDN $PIDM $PIDL $PIDF $PIDW
    cd $START_DIR
}

function launch () {
    export PYRO_SERIALIZERS_ACCEPTED=pickle
    export PYRO_SERIALIZER=pickle
    python3 -m Pyro4.naming &
    PIDN=$!
    eval $START_CMD -m services message_bus &
    PIDM=$!
    eval $START_CMD -m services logger &
    PIDL=$!
    eval $START_CMD -m services filesystem &
    PIDF=$!
    eval $START_CMD -m services ws_server &
    PIDW=$!
    sleep 5
}

case $1 in
    "start")
        launch
        trap 'kill $PIDN $PIDM $PIDL $PIDF $PIDW' INT TERM QUIT

        wait $PIDN
        ;;
    "test")
        python3 -m pytest --cov-report= --cov=services test/
        START_CMD='coverage run -p'
        launch
        pushd test
        ./run_tests || echo 'TESTS FAILED TO RUN' 1>&2
        popd
        pkill -USR1 coverage
        wait $PIDM $PIDL $PIDF $PIDW
        coverage combine --append
        coverage report -m
        ;;
    *)
        echo "Usage: $0 (start|test)"
        ;;
esac
