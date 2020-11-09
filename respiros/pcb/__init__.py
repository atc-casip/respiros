import atexit

import pigpio


pi = pigpio.pi()

atexit.register(pi.stop)

if not pi.connected:
    exit()
