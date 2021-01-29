"""
Emit events to clients using WebSockets.
"""

import logging

import socketio

from .context import Context
from .messenger import Messenger

sio = socketio.Server(async_mode="eventlet")
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, data):
    """Handler for the connection event."""

    logging.info("New client connected with ID %s", sid)


@sio.event()
def disconnect(sid, data):
    """Handler for the disconnection event."""

    logging.info("Client with ID %s disconnected", sid)


def emit_parameters(ctx: Context):
    logging.info("emitting params")
    sio.emit(
        "parameters",
        {
            "mode": "VPS",
            "ipap": ctx.ipap,
            "epap": ctx.epap,
            "breathing_freq": ctx.freq,
            "trigger": ctx.trigger,
            "ie_relation": f"{ctx.inhale}:{ctx.exhale}",
        },
    )


def emit_cycle(ctx: Context):
    pass


def emit_readings(ctx: Context):
    logging.info("emitting readings")
    sio.emit("readings", ctx.readings)
    ctx.readings = []


def emit_alarm(ctx: Context):
    pass


def handle_messages(messenger: Messenger, ctx: Context):
    while True:
        [topic, msg] = messenger.recv()
        if topic == "operation":
            ctx.ipap = msg["ipap"]
            ctx.epap = msg["epap"]
            ctx.freq = msg["freq"]
            ctx.trigger = msg["trigger"]
            ctx.inhale = msg["inhale"]
            ctx.exhale = msg["exhale"]

            emit_parameters(ctx)
        elif topic == "reading":
            ctx.readings.append(
                {
                    "pressure": msg["pressure"],
                    "flow": msg["airflow"],
                    "volume": msg["volume"],
                    "timestamp": msg["timestamp"],
                }
            )

            if len(ctx.readings) == 10:
                emit_readings(ctx)
