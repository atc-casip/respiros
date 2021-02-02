"""
Input initial parameters for operation.
"""

from typing import Dict, Optional

import PySimpleGUI as sg
from gui.components import IESlider, NumericSlider
from gui.config import cfg
from gui.context import Context
from gui.messenger import Messenger

from .view import View


class ParametersView(View):
    """
    Parameter selection for operation start.
    """

    # Sliders
    ipap: NumericSlider
    epap: NumericSlider
    freq: NumericSlider
    trigger: NumericSlider
    ie: IESlider

    # Buttons
    start_btn: sg.Button

    def __init__(self):
        self.ipap = NumericSlider(
            "Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["ipap"]["min"],
                cfg["params"]["ipap"]["max"],
            ),
            default_value=cfg["params"]["ipap"]["default"],
        )
        self.epap = NumericSlider(
            "Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["epap"]["min"],
                cfg["params"]["epap"]["max"],
            ),
            default_value=cfg["params"]["epap"]["default"],
        )
        self.freq = NumericSlider(
            "Frecuencia",
            metric="rpm",
            values=(
                cfg["params"]["freq"]["min"],
                cfg["params"]["freq"]["max"],
            ),
            default_value=cfg["params"]["freq"]["default"],
        )
        self.trigger = NumericSlider(
            "Trigger de flujo",
            metric="ml",
            values=(
                cfg["params"]["trigger"]["min"],
                cfg["params"]["trigger"]["max"],
            ),
            default_value=cfg["params"]["trigger"]["default"],
        )
        self.ie = IESlider(
            inhale_max=cfg["params"]["inhale"]["max"],
            exhale_max=cfg["params"]["exhale"]["max"],
            default_value=(
                cfg["params"]["inhale"]["default"],
                cfg["params"]["exhale"]["default"],
            ),
        )

        self.start_btn = sg.Button("Comenzar", size=(10, 2))

        super().__init__(
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

    def set_up(self, ctx: Context):
        super().expand(expand_x=True, expand_y=True)
        self.ipap.expand()
        self.epap.expand()
        self.freq.expand()
        self.trigger.expand()
        self.ie.expand()

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ) -> Optional[str]:
        if event == self.ipap.slider.Key:
            self.ipap.value = ctx.ipap = values[event]
            if self.ipap.value <= self.epap.value:
                self.epap.value = ctx.epap = self.ipap.value - 1
        elif event == self.epap.slider.Key:
            self.epap.value = ctx.epap = values[event]
            if self.epap.value >= self.ipap.value:
                self.ipap.value = ctx.ipap = self.epap.value + 1
        elif event == self.freq.slider.Key:
            self.freq.value = ctx.freq = values[event]
        elif event == self.trigger.slider.Key:
            self.trigger.value = ctx.trigger = values[event]
        elif event == self.ie.slider.Key:
            self.ie.value = values[event]
            ctx.inhale = self.ie.value[0]
            ctx.exhale = self.ie.value[1]
        elif event == self.start_btn.Key:
            msg.send(
                "operation",
                {
                    "ipap": ctx.ipap,
                    "epap": ctx.epap,
                    "freq": ctx.freq,
                    "trigger": ctx.trigger,
                    "inhale": ctx.inhale,
                    "exhale": ctx.exhale,
                },
            )
            return "/operation"
        return None
