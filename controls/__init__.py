import logging

from controls.app import ControlApplication
from controls.config import DevelopmentConfig
from controls.context import ctx
from controls.ipc import ipc
from controls.pcb.controller import pcb
from controls.states.director import sd


def create_app() -> ControlApplication:
    app = ControlApplication()

    app.config.from_object(DevelopmentConfig)

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
