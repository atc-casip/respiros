import logging

from .app import App

logging.basicConfig(filename="gui.log", filemode="w", level=logging.INFO)
App().run()
