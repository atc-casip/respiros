from typing import Dict

import PySimpleGUI as sg
from common.ipc import Topic
from gui.widgets.sliders import IESlider, NumericSlider

from .tab import ControlTab


class ParametersTab(ControlTab):
    """Tab for operation control."""

    def __init__(self, app):
        super().__init__(app, "Parámetros")

        # VCP
        self.ipap_vcp = NumericSlider(
            app,
            label="Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["IPAP_MIN"],
                app.config["IPAP_MAX"],
            ),
            default_value=app.config["IPAP_DEFAULT"],
        )
        self.epap_vcp = NumericSlider(
            app,
            label="Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["EPAP_MIN"],
                app.config["EPAP_MAX"],
            ),
            default_value=app.config["EPAP_DEFAULT"],
        )
        self.freq_vcp = NumericSlider(
            app,
            label="Frecuencia",
            metric="rpm",
            values=(
                app.config["FREQ_MIN"],
                app.config["FREQ_MAX"],
            ),
            default_value=app.config["FREQ_DEFAULT"],
        )
        self.trigger_vcp = NumericSlider(
            app,
            label="Trigger de flujo",
            metric="ml",
            values=(
                app.config["TRIGGER_MIN"],
                app.config["TRIGGER_MAX"],
            ),
            default_value=app.config["TRIGGER_DEFAULT"],
        )
        self.ie_vcp = IESlider(
            app,
            inhale_max=app.config["INHALE_MAX"],
            exhale_max=app.config["EXHALE_MAX"],
            default_value=(
                app.config["INHALE_DEFAULT"],
                app.config["EXHALE_DEFAULT"],
            ),
        )

        # VPS
        self.ipap_vps = NumericSlider(
            app,
            label="Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["IPAP_MIN"],
                app.config["IPAP_MAX"],
            ),
            default_value=app.config["IPAP_DEFAULT"],
        )
        self.epap_vps = NumericSlider(
            app,
            label="Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["EPAP_MIN"],
                app.config["EPAP_MAX"],
            ),
            default_value=app.config["EPAP_DEFAULT"],
        )
        self.trigger_vps = NumericSlider(
            app,
            label="Trigger de flujo",
            metric="ml",
            values=(
                app.config["TRIGGER_MIN"],
                app.config["TRIGGER_MAX"],
            ),
            default_value=app.config["TRIGGER_DEFAULT"],
        )

        # Tabs
        self.vcp_tab = sg.Column(
            [
                [self.ipap_vcp],
                [self.epap_vcp],
                [self.freq_vcp],
                [self.trigger_vcp],
                [self.ie_vcp],
            ],
            visible=False,
        )
        self.vps_tab = sg.Column(
            [
                [self.ipap_vps],
                [self.epap_vps],
                [self.trigger_vps],
            ],
            visible=False,
        )

        self.children = [
            self.ipap_vcp,
            self.epap_vcp,
            self.freq_vcp,
            self.trigger_vcp,
            self.ie_vcp,
            self.ipap_vps,
            self.epap_vps,
            self.trigger_vps,
        ]
        self.layout([[self.vcp_tab, self.vps_tab]])

    def handle_event(self, event: str, values: Dict):
        super().handle_event(event, values)

        if self.app.ctx.mode.upper() == "VCP":
            self.app.ctx.ipap = self.ipap_vps.value = self.ipap_vcp.value
            self.app.ctx.epap = self.epap_vps.value = self.epap_vcp.value
            self.app.ctx.trigger = (
                self.trigger_vps.value
            ) = self.trigger_vcp.value
            self.app.ctx.freq = self.freq_vcp.value
            self.app.ctx.inhale = self.ie_vcp.value[0]
            self.app.ctx.exhale = self.ie_vcp.value[1]
        else:
            self.app.ctx.ipap = self.ipap_vcp.value = self.ipap_vps.value
            self.app.ctx.epap = self.epap_vcp.value = self.epap_vps.value
            self.app.ctx.trigger = (
                self.trigger_vcp.value
            ) = self.trigger_vps.value

        if self.app.ctx.ipap <= self.app.ctx.epap and event in {
            self.ipap_vcp.slider.Key,
            self.ipap_vps.slider.Key,
        }:
            self.app.ctx.epap = self.epap_vcp.value = self.epap_vps.value = (
                self.app.ctx.ipap - 1
            )
        elif self.app.ctx.epap >= self.app.ctx.ipap and event in {
            self.epap_vcp.slider.Key,
            self.epap_vps.slider.Key,
        }:
            self.app.ctx.ipap = self.ipap_vcp.value = self.ipap_vps.value = (
                self.app.ctx.epap + 1
            )

        for c in self.children:
            if event == c.slider.Key:
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
                break

    def switch_mode(self):
        if self.app.ctx.mode.upper() == "VCP":
            self.vps_tab.update(visible=False)
            self.vcp_tab.expand(expand_x=True, expand_y=True)
            self.ipap_vcp.expand()
            self.epap_vcp.expand()
            self.freq_vcp.expand()
            self.trigger_vcp.expand()
            self.ie_vcp.expand()
        else:
            self.vcp_tab.update(visible=False)
            self.vps_tab.expand(expand_x=True, expand_y=True)
            self.ipap_vps.expand()
            self.epap_vps.expand()
            self.trigger_vps.expand()

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.switch_mode()
        super().show()

    def lock(self):
        for c in self.children:
            c.slider.update(disabled=True)

    def unlock(self):
        for c in self.children:
            c.slider.update(disabled=False)
