from typing import Dict

import PySimpleGUI as sg
from gui.component import Component
from gui.ipc import ZMQEvent
from gui.views.parameters import ParametersView


class LoadingView(Component):
    """Shows progress and information about system checks."""

    def __init__(self, app):
        super().__init__(app, visible=False, key="LoadingView")

        self.loading_label = sg.Text(
            "Cargando",
            justification="center",
            font=(
                app.config["FONT_FAMILY"],
                app.config["FONT_SIZE_BIG"],
                "bold",
            ),
        )
        self.expander_top = sg.Text()
        self.expander_bottom = sg.Text()

        self.layout(
            [[self.expander_top], [self.loading_label], [self.expander_bottom]]
        )

    def handle_event(self, event: str, values: Dict):
        if event == ZMQEvent.CHECK.name:
            self.app.show_view(ParametersView)

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.expander_top.expand(expand_x=True, expand_y=True)
        self.expander_bottom.expand(expand_x=True, expand_y=True)
        self.loading_label.expand(
            expand_x=True, expand_y=True, expand_row=False
        )
        super().show()
