import logging

from gui.app import GUIApplication
from gui.config import DevelopmentConfig
from gui.ipc import ipc
from gui.views.director import vd
from gui.context import ctx


def create_app() -> GUIApplication:
    app = GUIApplication()

    app.config.from_object(DevelopmentConfig)

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
