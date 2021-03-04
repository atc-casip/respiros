"""
Emit events to clients using WebSockets.
"""

import logging

import socketio

sio = socketio.Server(async_mode="gevent", cors_allowed_origins="*")
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, environ):
    """Handler for the connection event."""

    logging.info("New client connected with ID %s", sid)


@sio.event
def disconnect(sid):
    """Handler for the disconnection event."""

    logging.info("Client with ID %s disconnected", sid)


def handle_messages():
    """Main events' controller.

    This function listens for events on the internal ZeroMQ sockets and emits
    the corresponding events through WebSockets.

    Args:
        messenger (Messenger): ZeroMQ messenger.
    """
    """
    while True:
        [topic, body] = msg.recv(block=False)
        if topic == "operation":
            logging.info("emitting params")
            sio.emit(
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
        elif topic == "reading":
            sio.emit(
                "readings",
                {
                    "pressure": body["pressure"],
                    "flow": body["airflow"],
                    "volume": body["volume"],
                    "timestamp": body["timestamp"],
                },
            )
        elif topic == "cycle":
            # TODO: Send cycle event.
            pass
        elif topic == "alarm":
            # TODO: Send alarm event.
            pass

        gevent.sleep(0.01)
        """
