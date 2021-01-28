"""
View for system checks.
"""

from typing import Dict, Optional

import PySimpleGUI as sg
from gui.context import Context
from gui.sockets import Messenger

from .view import View


class ChecksView(View):
    """
    Shows progress and information about system checks.
    """

    __counter = 0

    def __init__(self):
        super().__init__([[sg.Text("Cargando")]])

    def set_up(self, ctx: Context):
        pass

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ) -> Optional[str]:
        [topic, msg] = msg.recv()
        if topic == "check":
            for component in msg:
                if not msg[component]:
                    # TODO: Handle component failure
                    pass
            return "/parameters"
        return None
