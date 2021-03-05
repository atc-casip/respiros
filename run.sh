taskset -c 0 python -m controls & CONTROLS_PID=$!
taskset -c 1 python -m gui & GUI_PID=$!
taskset -c 2 python -m api & API_PID=$!

trap finish SIGINT
finish() {
    kill -9 $CONTROLS_PID
    kill -9 $GUI_PID
    kill -9 $API_PID
    exit
}

sleep infinity
