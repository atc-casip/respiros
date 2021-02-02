"""
Emit events to clients using WebSockets.
"""

import logging

import gevent
import socketio

from .messenger import Messenger

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


def handle_messages(messenger: Messenger):
    """Controller that produces Socket.IO events according to the internal ZeroMQ messages it
    receives.

    Args:
        messenger (Messenger): ZeroMQ messenger.
    """

    while True:
        [topic, msg] = messenger.recv(block=False)
        if topic == "operation":
            logging.info("emitting params")
            sio.emit(
                "parameters",
                {
                    "mode": "VPS",
                    "ipap": msg["ipap"],
                    "epap": msg["epap"],
                    "breathing_freq": msg["freq"],
                    "trigger": msg["trigger"],
                    "ie_relation": f"{msg['inhale']}:{msg['exhale']}",
                },
            )
        elif topic == "reading":
            sio.emit(
                "readings",
                {
                    "pressure": msg["pressure"],
                    "flow": msg["airflow"],
                    "volume": msg["volume"],
                    "timestamp": msg["timestamp"],
                },
            )

        gevent.sleep(0.01)
