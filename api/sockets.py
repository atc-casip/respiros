import logging

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
