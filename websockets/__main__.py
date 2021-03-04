"""
Entrypoint for the WebSockets process.
"""

import logging

import gevent
from geventwebsocket.handler import WebSocketHandler

from .ipc import monitor_sub, operation_sub
from .sockets import app, handle_messages

logging.basicConfig(
    filename="websockets.log", filemode="w", level=logging.INFO
)


server = gevent.pywsgi.WSGIServer(
    ("", 8000), app, handler_class=WebSocketHandler
)

server_thread = gevent.spawn(server.serve_forever)
ipc_thread = gevent.spawn(handle_messages)
gevent.joinall([server_thread, ipc_thread])
