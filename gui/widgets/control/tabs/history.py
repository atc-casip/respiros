from typing import Dict

import PySimpleGUI as sg
from common.alarms import Alarm, Criticality, Type
from common.ipc import Topic
from gui.ipc import ZMQEvent

from .tab import ControlTab


class AlarmCard(sg.Column):
    """Simple card that shows information about an alarm."""

    def __init__(self, font_family: str, font_size: int, last: bool = False):
        self.timestamp_label = sg.Text(
            "",
            size=(13, 1),
            font=(font_family, font_size),
        )
        self.type_label = sg.Text(
            "",
            size=(15, 1),
            font=(font_family, font_size),
        )
        self.priority_label = sg.Text(
            "",
            size=(10, 1),
            font=(font_family, font_size, "bold"),
            justification="right",
        )

        layout = [[self.timestamp_label, self.type_label, self.priority_label]]
        if not last:
            layout += [[sg.HorizontalSeparator()]]

        super().__init__(
            layout,
            visible=False,
            vertical_alignment="center",
        )

    def expand(self):
        super().expand(expand_x=True)
        self.type_label.expand(expand_x=True)

    def show_alarm(self, alarm: Alarm):
        """Update the card to show information about the given alarm.

        Args:
            alarm (Alarm): The alarm to show.
        """

        # Update type
        if alarm.type == Type.PRESSURE_MIN:
            self.type_label.update("Presión baja")
        elif alarm.type == Type.PRESSURE_MAX:
            self.type_label.update("Presión alta")
        elif alarm.type == Type.VOLUME_MIN:
            self.type_label.update("Volumen bajo")
        elif alarm.type == Type.VOLUME_MAX:
            self.type_label.update("Volumen alto")
        elif alarm.type == Type.OXYGEN_MIN:
            self.type_label.update("Oxígeno bajo")
        elif alarm.type == Type.OXYGEN_MAX:
            self.type_label.update("Oxígeno alto")
        elif alarm.type == Type.FREQ_MAX:
            self.type_label.update("Frecuencia alta")
        elif alarm.type == Type.APNEA:
            self.type_label.update("Apnea")
        elif alarm.type == Type.DISCONNECTION:
            self.type_label.update("Desconexión")

        # Update criticality
        if alarm.criticality == Criticality.HIGH:
            self.priority_label.update("Crítico", text_color="IndianRed1")
        else:
            self.priority_label.update("Normal", text_color="orange")

        # Update timestamp
        self.timestamp_label.update(alarm.timestamp.strftime("%d/%m %H:%M:%S"))


class HistoryTab(ControlTab):
    """Tab that shows the history of triggered alarms."""

    def __init__(self, app):
        super().__init__(app, "Histórico")

        # Buttons
        self.silence_btn = sg.Button(
            "Silenciar alarmas",
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )

        # Alarm cards
        self.alarm_cards = []
        for i in range(10):
            self.alarm_cards.append(
                AlarmCard(
                    font_family=app.config["FONT_FAMILY"],
                    font_size=app.config["FONT_SIZE_MEDIUM"],
                    last=True if i == 9 else False,
                )
            )

        self.layout(
            [[self.silence_btn]] + [[card] for card in self.alarm_cards]
        )

    def handle_event(self, event: str, values: Dict):
        if event == self.silence_btn.Key:
            self.app.ipc.send(Topic.SILENCE_ALARMS, {})
        elif event == ZMQEvent.ALARM.name:
            alarm = Alarm(
                Type[values[event]["type"]],
                Criticality[values[event]["criticality"]],
                float(values[event]["timestamp"]),
            )

            if alarm.criticality != Criticality.NONE:
                if len(self.app.ctx.alarms) == 10:
                    self.app.ctx.alarms = self.app.ctx.alarms[1:]
                self.app.ctx.alarms.append(alarm)
                for a, c in zip(self.app.ctx.alarms, self.alarm_cards):
                    c.show_alarm(a)

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.silence_btn.expand(expand_x=True)
        for card in self.alarm_cards:
            card.expand()
        super().show()

    def lock(self):
        self.silence_btn.update(disabled=True)

    def unlock(self):
        self.silence_btn.update(disabled=False)
