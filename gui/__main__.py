import logging

logging.basicConfig(filename="gui.log", filemode="w", level=logging.INFO)

from .app import App

App().run()
