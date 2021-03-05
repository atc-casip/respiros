import logging

import gevent

from common.ipc import IPCManager, Topic
from flask_socketio import SocketIO

socketio = SocketIO()


@socketio.on("connect")
def connect():
    """Callback executed when a new client connects."""

    logging.info("New client connected")


@socketio.on("disconnect")
def disconnect():
    """Callback executed when a client disconnects."""

    logging.info("Client disconnected")


def ipc_watchdog(ipc: IPCManager):
    while True:
        topic, body = ipc.recv(block=False)
        if topic == Topic.OPERATION_PARAMS:
            logging.info("emitting params")
            socketio.emit(
                "parameters",
                {
                    "mode": "VPS",
                    "ipap": body["ipap"],
                    "epap": body["epap"],
                    "breathing_freq": body["freq"],
                    "trigger": body["trigger"],
                    "ie_relation": f"{body['inhale']}:{body['exhale']}",
                },
            )
        elif topic == Topic.READING:
            socketio.emit(
                "readings",
                {
                    "pressure": body["pressure"],
                    "flow": body["airflow"],
                    "volume": body["volume"],
                    "timestamp": body["timestamp"],
                },
            )
        elif topic == Topic.CYCLE:
            # TODO: Send cycle event.
            pass
        elif topic == Topic.ALARM:
            # TODO: Send alarm event.
            pass

        gevent.sleep(0.1)
