from typing import Dict

import gui.events as events
import PySimpleGUI as sg

from .parameters import ParametersView
from .view import View


class LoadingView(View):
    """Shows progress and information about system checks."""

    def __init__(self, app):
        super().__init__(app, [[sg.Text("Cargando")]])

    def handle_event(self, event: str, values: Dict):
        if event == events.ZMQ_CHECK:
            self.app.show_view(ParametersView)
