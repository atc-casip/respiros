import logging

from flask import Flask

from api.config import DevelopmentConfig
from api.ipc import ipc
from api.sockets import socketio, ipc_watchdog


def create_app() -> Flask:
    """Create the app and initialize all its extensions.

    The appropiate config is loaded depending on the selected environment.

    Returns:
        Flask: The app.
    """

    app = Flask(__name__)

    app.config.from_object(DevelopmentConfig)

    if app.config["DEBUG"]:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(
        filename="logs/api.log", filemode="w", level=logging_level
    )

    ipc.init_app(app)
    socketio.init_app(app)

    socketio.start_background_task(ipc_watchdog, app.ipc)

    return app
