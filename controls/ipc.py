import zmq
from common.ipc import Publisher, Subscriber, Topic

PUB_ADDR = "ipc:///tmp/monitor"
SUB_ADDR = "ipc:///tmp/operation"

SYNC_CONTROLS = "ipc:///tmp/sync-controls"
SYNC_GUI = "ipc:///tmp/sync-gui"
SYNC_WEBSOCKETS = "ipc:///tmp/sync-websockets"

ctx = zmq.Context()
pub = Publisher(ctx, PUB_ADDR, {SYNC_GUI, SYNC_WEBSOCKETS})
sub = Subscriber(
    ctx,
    SUB_ADDR,
    {Topic.OPERATION_PARAMS, Topic.OPERATION_ALARMS, Topic.REQUEST_READING},
    SYNC_CONTROLS,
)
