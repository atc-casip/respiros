from typing import Dict

import common.ipc.topics as topics
import gui.events as events
import PySimpleGUI as sg
from gui.components import IESlider, NumericSlider
from gui.config import cfg
from gui.context import ctx
from gui.messenger import msg

from .operation import OperationView
from .view import View


class ParametersView(View):
    """Parameter selection for operation start."""

    def __init__(self, app):
        # Sliders
        self.ipap = NumericSlider(
            "Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["ipap"]["min"],
                cfg["params"]["ipap"]["max"],
            ),
            default_value=cfg["params"]["ipap"]["default"],
            key=events.IPAP_SLIDER_PARAMS,
        )
        self.epap = NumericSlider(
            "Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["epap"]["min"],
                cfg["params"]["epap"]["max"],
            ),
            default_value=cfg["params"]["epap"]["default"],
            key=events.EPAP_SLIDER_PARAMS,
        )
        self.freq = NumericSlider(
            "Frecuencia",
            metric="rpm",
            values=(
                cfg["params"]["freq"]["min"],
                cfg["params"]["freq"]["max"],
            ),
            default_value=cfg["params"]["freq"]["default"],
            key=events.FREQ_SLIDER_PARAMS,
        )
        self.trigger = NumericSlider(
            "Trigger de flujo",
            metric="ml",
            values=(
                cfg["params"]["trigger"]["min"],
                cfg["params"]["trigger"]["max"],
            ),
            default_value=cfg["params"]["trigger"]["default"],
            key=events.TRIGGER_SLIDER_PARAMS,
        )
        self.ie = IESlider(
            inhale_max=cfg["params"]["inhale"]["max"],
            exhale_max=cfg["params"]["exhale"]["max"],
            default_value=(
                cfg["params"]["inhale"]["default"],
                cfg["params"]["exhale"]["default"],
            ),
            key=events.IE_SLIDER_PARAMS,
        )

        # Buttons
        self.start_btn = sg.Button(
            "Comenzar",
            size=(10, 2),
            font=("Helvetica", 12),
            key=events.START_BUTTON_PARAMS,
        )

        super().__init__(
            app,
            [
                [
                    sg.Text(
                        "Seleccione los parámetros de operación",
                        font=("Helvetica", 20, "bold"),
                    )
                ],
                [self.ipap],
                [self.epap],
                [self.freq],
                [self.trigger],
                [self.ie],
                [self.start_btn],
            ],
            pad=(373, 0),
        )

    def show(self):
        super().expand(expand_x=True, expand_y=True)
        self.ipap.expand()
        self.epap.expand()
        self.freq.expand()
        self.trigger.expand()
        self.ie.expand()

        super().show()

    def handle_event(self, event: str, values: Dict):
        if event == events.IPAP_SLIDER_PARAMS:
            self.ipap.value = ctx.ipap = int(values[event])
            if self.ipap.value <= self.epap.value:
                self.epap.value = ctx.epap = self.ipap.value - 1
        elif event == events.EPAP_SLIDER_PARAMS:
            self.epap.value = ctx.epap = int(values[event])
            if self.epap.value >= self.ipap.value:
                self.ipap.value = ctx.ipap = self.epap.value + 1
        elif event == events.FREQ_SLIDER_PARAMS:
            self.freq.value = ctx.freq = int(values[event])
        elif event == events.TRIGGER_SLIDER_PARAMS:
            self.trigger.value = ctx.trigger = int(values[event])
        elif event == events.IE_SLIDER_PARAMS:
            self.ie.value = int(values[event])
            ctx.inhale = self.ie.value[0]
            ctx.exhale = self.ie.value[1]
        elif event == events.START_BUTTON_PARAMS:
            msg.send(
                topics.OPERATION_PARAMS,
                {
                    "ipap": ctx.ipap,
                    "epap": ctx.epap,
                    "freq": ctx.freq,
                    "trigger": ctx.trigger,
                    "inhale": ctx.inhale,
                    "exhale": ctx.exhale,
                },
            )
            self.app.show_view(OperationView)
