import logging
import os

from flask import Flask

from api.config import Config, DevelopmentConfig
from api.ipc import ipc
from api.sockets import socketio


def create_app() -> Flask:
    """Create the app and initialize all its extensions.

    The appropiate config is loaded depending on the selected environment.

    Returns:
        Flask: The app.
    """

    app = Flask(__name__)

    if os.environ.get("ENV") == "development":
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(Config)

    if app.config["DEBUG"]:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(
        filename="logs/api.log", filemode="w", level=logging_level
    )

    socketio.init_app(app)
    ipc.init_app(app)

    return app
