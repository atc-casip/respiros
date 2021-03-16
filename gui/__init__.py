import logging
import os

from gui.app import GUIApplication
from gui.config import Config, DevelopmentConfig
from gui.context import ctx
from gui.ipc import ipc
from gui.views.director import vd


def create_app() -> GUIApplication:
    """Create the app and initialize all its extensions.

    The appropiate config is loaded depending on the selected environment.

    Returns:
        GUIApplication: The app.
    """

    app = GUIApplication()

    if os.environ.get("ENV") == "development":
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(Config)

    if app.config["DEBUG"]:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(
        filename="logs/gui.log", filemode="w", level=logging_level
    )

    ctx.init_app(app)
    vd.init_app(app)
    ipc.init_app(app)

    return app
