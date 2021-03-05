import logging

logging.basicConfig(filename="logs/gui.log", filemode="w", level=logging.INFO)

from .app import App

App().run()
