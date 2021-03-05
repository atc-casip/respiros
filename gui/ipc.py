import zmq
from common.ipc import Publisher, Subscriber, Topic

PUB_ADDR = "ipc:///tmp/operation"
SUB_ADDR = "ipc:///tmp/monitor"

SYNC_CONTROLS = "ipc:///tmp/sync-controls"
SYNC_GUI = "ipc:///tmp/sync-gui"
SYNC_WEBSOCKETS = "ipc:///tmp/sync-api"

ctx = zmq.Context()
sub = Subscriber(
    ctx,
    SUB_ADDR,
    {
        Topic.CHECK,
        Topic.READING,
        Topic.CYCLE,
        Topic.ALARM,
        Topic.OPERATION_MODE,
    },
    SYNC_GUI,
)
pub = Publisher(ctx, PUB_ADDR, {SYNC_CONTROLS, SYNC_WEBSOCKETS})
