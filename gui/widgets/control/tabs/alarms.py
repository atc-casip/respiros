from typing import Dict

import PySimpleGUI as sg
from common.ipc import Topic
from gui.widgets.sliders import NumericSlider

from .tab import ControlTab


class AlarmsTab(ControlTab):
    """Tab for alarm range control."""

    def __init__(self, app):
        super().__init__(app, "Alarmas")

        # Sliders
        self.pressure_min = NumericSlider(
            app,
            label="Min",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["ALARM_PRESSURE_MIN"],
                app.config["ALARM_PRESSURE_MAX"],
            ),
            default_value=app.config["ALARM_PRESSURE_MIN"],
        )
        self.pressure_max = NumericSlider(
            app,
            label="Max",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                app.config["ALARM_PRESSURE_MIN"],
                app.config["ALARM_PRESSURE_MAX"],
            ),
            default_value=app.config["ALARM_PRESSURE_MAX"],
        )
        self.volume_min = NumericSlider(
            app,
            label="Min",
            metric="l/min",
            values=(
                app.config["ALARM_VOLUME_MIN"],
                app.config["ALARM_VOLUME_MAX"],
            ),
            default_value=app.config["ALARM_VOLUME_MIN"],
        )
        self.volume_max = NumericSlider(
            app,
            label="Max",
            metric="l/min",
            values=(
                app.config["ALARM_VOLUME_MIN"],
                app.config["ALARM_VOLUME_MAX"],
            ),
            default_value=app.config["ALARM_VOLUME_MAX"],
        )
        self.oxygen_min = NumericSlider(
            app,
            label="Min",
            metric="%",
            values=(
                app.config["ALARM_OXYGEN_MIN"],
                app.config["ALARM_OXYGEN_MAX"],
            ),
            default_value=app.config["ALARM_OXYGEN_MIN"],
        )
        self.oxygen_max = NumericSlider(
            app,
            label="Max",
            metric="%",
            values=(
                app.config["ALARM_OXYGEN_MIN"],
                app.config["ALARM_OXYGEN_MAX"],
            ),
            default_value=app.config["ALARM_OXYGEN_MAX"],
        )
        self.freq_max = NumericSlider(
            app,
            label="Max",
            metric="rpm",
            values=(
                app.config["ALARM_FREQ_MIN"],
                app.config["ALARM_FREQ_MAX"],
            ),
            default_value=app.config["ALARM_FREQ_MAX"],
        )

        # Frames
        self.pressure_frame = sg.Frame(
            "Presión",
            [[self.pressure_min, self.pressure_max]],
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.volume_frame = sg.Frame(
            "Volumen",
            [[self.volume_min, self.volume_max]],
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.oxygen_frame = sg.Frame(
            "Oxígeno",
            [[self.oxygen_min, self.oxygen_max]],
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.freq_frame = sg.Frame(
            "Frecuencia",
            [[self.freq_max]],
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )

        # Buttons
        self.commit_btn = sg.Button(
            "Aplicar",
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )

        self.children = [
            self.pressure_min,
            self.pressure_max,
            self.volume_min,
            self.volume_max,
            self.oxygen_min,
            self.oxygen_max,
            self.freq_max,
        ]
        self.layout(
            [
                [self.commit_btn],
                [self.pressure_frame],
                [self.volume_frame],
                [self.oxygen_frame],
                [self.freq_frame],
            ]
        )

    def handle_event(self, event: str, values: Dict):
        super().handle_event(event, values)
        if event == self.commit_btn.Key:
            self.app.ipc.send(
                Topic.OPERATION_ALARMS,
                {
                    "pressure_min": self.app.ctx.pressure_min,
                    "pressure_max": self.app.ctx.pressure_max,
                    "volume_min": self.app.ctx.volume_min,
                    "volume_max": self.app.ctx.volume_max,
                    "oxygen_min": self.app.ctx.oxygen_min,
                    "oxygen_max": self.app.ctx.oxygen_max,
                    "freq_max": self.app.ctx.freq_max,
                },
            )

        self.app.ctx.pressure_min = self.pressure_min.value
        self.app.ctx.pressure_max = self.pressure_max.value
        self.app.ctx.volume_min = self.volume_min.value
        self.app.ctx.volume_max = self.volume_max.value
        self.app.ctx.oxygen_min = self.oxygen_min.value
        self.app.ctx.oxygen_max = self.oxygen_max.value
        self.app.ctx.freq_max = self.freq_max.value

        if self.pressure_max.value <= self.pressure_min.value:
            if event == self.pressure_min.slider.Key:
                self.app.ctx.pressure_max = self.pressure_max.value = (
                    self.pressure_min.value + 1
                )
            else:
                self.app.ctx.pressure_min = self.pressure_min.value = (
                    self.pressure_max.value - 1
                )
        elif self.volume_max.value <= self.volume_min.value:
            if event == self.volume_min.slider.Key:
                self.app.ctx.volume_max = self.volume_max.value = (
                    self.volume_min.value + 1
                )
            else:
                self.app.ctx.volume_min = self.volume_min.value = (
                    self.volume_max.value - 1
                )
        elif self.oxygen_max.value <= self.oxygen_min.value:
            if event == self.oxygen_min.slider.Key:
                self.app.ctx.oxygen_max = self.oxygen_max.value = (
                    self.oxygen_min.value + 1
                )
            else:
                self.app.ctx.oxygen_min = self.oxygen_min.value = (
                    self.oxygen_max.value - 1
                )

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.pressure_frame.expand(expand_x=True)
        self.volume_frame.expand(expand_x=True)
        self.oxygen_frame.expand(expand_x=True)
        self.freq_frame.expand(expand_x=True)
        self.commit_btn.expand(expand_x=True)
        super().show()

    def lock(self):
        for c in self.children:
            c.slider.update(disabled=True)
        self.commit_btn.update(disabled=True)

    def unlock(self):
        for c in self.children:
            c.slider.update(disabled=False)
        self.commit_btn.update(disabled=False)
