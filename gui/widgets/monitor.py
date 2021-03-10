from typing import Dict

import PySimpleGUI as sg
from common.alarms import Alarm, Criticality, Type
from gui.component import Component
from gui.ipc import ZMQEvent


class DisplayUnit(sg.Column):
    def __init__(
        self,
        title: str,
        metric: str,
        size: int,
        font_family: str,
        font_size: int,
    ):
        self.__value = 0.0
        self.__metric = metric

        self.title_label = sg.Text(
            f"{title}:", font=(font_family, font_size, "bold")
        )
        self.value_label = sg.Text(
            f"-   {self.__metric}",
            font=(font_family, font_size, "bold"),
            size=(size, 1),
            justification="right",
        )

        super().__init__([[self.title_label, self.value_label]])

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, new_value: float):
        self.__value = round(new_value, 1)
        self.value_label.update(f"{self.__value} {self.__metric}")

    def show_alarm(self, criticality: Criticality):
        """Change the color of the unit to reflect an alarm.

        Args:
            criticality (str): Level of criticality.
        """

        if criticality == Criticality.NONE:
            self.title_label.update(text_color="white")
            self.value_label.update(text_color="white")
        elif criticality == Criticality.MEDIUM:
            self.title_label.update(text_color="orange")
            self.value_label.update(text_color="orange")
        elif criticality == Criticality.HIGH:
            self.title_label.update(text_color="IndianRed1")
            self.value_label.update(text_color="IndianRed1")


class MonitorBar(Component):
    """System bar for parameter monitoring."""

    def __init__(self, app):
        super().__init__(app)

        # Displays
        self.ipap = DisplayUnit(
            title="IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            size=10,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_BIG"],
        )
        self.epap = DisplayUnit(
            title="EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            size=10,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_BIG"],
        )
        self.freq = DisplayUnit(
            title="Frecuencia",
            metric="rpm",
            size=8,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_BIG"],
        )
        self.vc_in = DisplayUnit(
            title="V (in)",
            metric="ml",
            size=5,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_SMALL"],
        )
        self.vc_out = DisplayUnit(
            title="V (out)",
            metric="ml",
            size=5,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_SMALL"],
        )
        self.oxygen = DisplayUnit(
            title="O\N{SUBSCRIPT TWO}",
            metric="%",
            size=4,
            font_family=app.config["FONT_FAMILY"],
            font_size=app.config["FONT_SIZE_SMALL"],
        )

        # Buttons
        self.lock_btn = sg.Button(
            "Bloquear",
            size=(9, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )

        # Misc
        self.expander = sg.Text()

        self.layout(
            [
                [
                    self.ipap,
                    self.epap,
                    self.freq,
                    self.vc_in,
                    self.vc_out,
                    self.oxygen,
                    self.expander,
                    self.lock_btn,
                ]
            ]
        )

    def handle_event(self, event: str, values: Dict):
        if event == self.lock_btn.Key:
            if not self.app.ctx.locked:
                self.app.ctx.locked = True
                self.lock_btn.update("Desbloquear")
            else:
                self.app.ctx.locked = False
                self.lock_btn.update("Bloquear")
        elif event == ZMQEvent.CYCLE.name:
            self.ipap.value = values[event]["ipap"]
            self.epap.value = values[event]["epap"]
            self.freq.value = values[event]["freq"]
            self.vc_in.value = values[event]["vc_in"]
            self.vc_out.value = values[event]["vc_out"]
            self.oxygen.value = values[event]["oxygen"]
        elif event == ZMQEvent.ALARM.name:
            alarm = Alarm(
                Type[values[event]["type"]],
                Criticality[values[event]["criticality"]],
                float(values[event]["timestamp"]),
            )

            if alarm.type == Type.PRESSURE_MIN:
                self.epap.show_alarm(alarm.criticality)
            elif alarm.type == Type.PRESSURE_MAX:
                self.ipap.show_alarm(alarm.criticality)
            elif alarm.type == Type.VOLUME_MIN:
                pass
            elif alarm.type == Type.VOLUME_MAX:
                pass
            elif alarm.type in {Type.OXYGEN_MIN, Type.OXYGEN_MAX}:
                self.oxygen.show_alarm(alarm.criticality)
            elif alarm.type == Type.FREQ_MAX:
                self.freq.show_alarm(alarm.criticality)

    def show(self):
        self.expand(expand_x=True, expand_row=False)
        self.expander.expand(expand_x=True)
