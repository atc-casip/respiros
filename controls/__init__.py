import logging
import os

from controls.app import ControlApplication
from controls.config import Config, DevelopmentConfig, TestingConfig
from controls.context import ctx
from controls.ipc import ipc
from controls.pcb.controller import pcb
from controls.states.director import sd


def create_app() -> ControlApplication:
    """Create the app and initialize all its extensions.

    The appropiate config is loaded depending on the selected environment.

    Returns:
        ControlApplication: The app.
    """

    app = ControlApplication()

    if os.environ.get("ENV") == "development":
        app.config.from_object(DevelopmentConfig)
    elif os.environ.get("ENV") == "test":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)

    if app.config["DEBUG"]:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(
        filename="logs/controls.log", filemode="w", level=logging_level
    )

    ctx.init_app(app)
    pcb.init_app(app)
    sd.init_app(app)
    ipc.init_app(app)

    return app
