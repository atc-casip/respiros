"""
Entrypoint for the WebSockets process.
"""

import atexit
import logging

import eventlet

from .context import Context
from .messenger import Messenger
from .sockets import app, handle_messages

logging.basicConfig(filename="websockets.log", filemode="w", level=logging.INFO)

messenger = Messenger()
context = Context()

ipc_thread = eventlet.spawn(handle_messages, messenger, context)
atexit.register(eventlet.kill, ipc_thread)

eventlet.wsgi.server(eventlet.listen(("", 8000)), app)
