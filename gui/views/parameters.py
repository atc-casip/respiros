from typing import Dict

import PySimpleGUI as sg
from common.ipc import Topic
from gui.component import Component
from gui.views.operation import OperationView
from gui.widgets.sliders import IESlider, NumericSlider


class ParametersView(Component):
    """Parameter selection for operation start."""

    def __init__(self, app):
        super().__init__(
            app, pad=(373, 0), visible=False, key="ParametersView"
        )

        # Sliders
        self.ipap = NumericSlider(
            app,
            label="Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(app.config["IPAP_MIN"], app.config["IPAP_MAX"]),
            default_value=app.config["IPAP_DEFAULT"],
        )
        self.epap = NumericSlider(
            app,
            label="Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(app.config["EPAP_MIN"], app.config["EPAP_MAX"]),
            default_value=app.config["EPAP_DEFAULT"],
        )
        self.freq = NumericSlider(
            app,
            label="Frecuencia",
            metric="rpm",
            values=(app.config["FREQ_MIN"], app.config["FREQ_MAX"]),
            default_value=app.config["FREQ_DEFAULT"],
        )
        self.trigger = NumericSlider(
            app,
            label="Trigger de flujo",
            metric="ml",
            values=(app.config["TRIGGER_MIN"], app.config["TRIGGER_MAX"]),
            default_value=app.config["TRIGGER_DEFAULT"],
        )
        self.ie = IESlider(
            app,
            inhale_max=app.config["INHALE_MAX"],
            exhale_max=app.config["EXHALE_MAX"],
            default_value=(
                app.config["INHALE_DEFAULT"],
                app.config["EXHALE_DEFAULT"],
            ),
        )

        # Buttons
        self.start_btn = sg.Button(
            "Comenzar",
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )

        self.children = [
            self.ipap,
            self.epap,
            self.freq,
            self.trigger,
            self.ie,
        ]
        self.layout(
            [
                [
                    sg.Text(
                        "Seleccione los parámetros de operación",
                        font=(
                            app.config["FONT_FAMILY"],
                            app.config["FONT_SIZE_BIG"],
                            "bold",
                        ),
                    )
                ],
                [self.ipap],
                [self.epap],
                [self.freq],
                [self.trigger],
                [self.ie],
                [self.start_btn],
            ]
        )

    def handle_event(self, event: str, values: Dict):
        super().handle_event(event, values)
        if event == self.start_btn.Key:
            self.app.ipc.send(
                Topic.OPERATION_PARAMS,
                {
                    "ipap": self.app.ctx.ipap,
                    "epap": self.app.ctx.epap,
                    "freq": self.app.ctx.freq,
                    "trigger": self.app.ctx.trigger,
                    "inhale": self.app.ctx.inhale,
                    "exhale": self.app.ctx.exhale,
                },
            )
            self.app.show_view(OperationView)

        self.app.ctx.ipap = self.ipap.value
        self.app.ctx.epap = self.epap.value
        self.app.ctx.freq = self.freq.value
        self.app.ctx.trigger = self.trigger.value
        self.app.ctx.inhale = self.ie.value[0]
        self.app.ctx.exhale = self.ie.value[1]

        if self.ipap.value <= self.epap.value:
            if event == self.ipap.slider.Key:
                self.app.ctx.epap = self.epap.value = self.ipap.value - 1
            else:
                self.app.ctx.ipap = self.ipap.value = self.epap.value + 1

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        super().show()
