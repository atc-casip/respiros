import zmq
from common.ipc import Subscriber, Topic

OPERATION_ADDR = "ipc:///tmp/operation"
MONITOR_ADDR = "ipc:///tmp/monitor"

SYNC = "ipc:///tmp/sync-websockets"

ctx = zmq.Context()
monitor_sub = Subscriber(
    ctx, MONITOR_ADDR, {Topic.READING, Topic.CYCLE, Topic.ALARM}, SYNC
)
operation_sub = Subscriber(ctx, OPERATION_ADDR, {Topic.OPERATION_PARAMS}, SYNC)
