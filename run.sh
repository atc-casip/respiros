taskset -c 0 python -m controls & echo $!
taskset -c 1 python -m gui & echo $!
taskset -c 2 python -m websockets & echo $!
