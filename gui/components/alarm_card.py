import datetime

import common.alarms as alarms
import gui.style as style
import PySimpleGUI as sg


class AlarmCard(sg.Column):
    def __init__(self, last: bool = False):
        self.timestamp_label = sg.Text(
            "",
            size=(13, 1),
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )
        self.type_label = sg.Text(
            "",
            size=(15, 1),
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )
        self.priority_label = sg.Text(
            "",
            size=(10, 1),
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM, "bold"),
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

    def update(
        self, type: str, criticality: str, timestamp: datetime.datetime
    ):
        text = ""
        if type == alarms.PRESSURE_MIN:
            text = "Presión baja"
        elif type == alarms.PRESSURE_MAX:
            text = "Presión alta"
        elif type == alarms.VOLUME_MIN:
            text = "Volumen bajo"
        elif type == alarms.VOLUME_MAX:
            text = "Volumen alto"
        elif type == alarms.OXYGEN_MIN:
            text = "Oxígeno bajo"
        elif type == alarms.OXYGEN_MAX:
            text = "Oxígeno alto"
        elif type == alarms.FREQ_MAX:
            text = "Frecuencia alta"
        elif type == alarms.APNEA:
            text = "Apnea"
        elif type == alarms.DISCONNECTION:
            text = "Desconexión"

        self.timestamp_label.update(timestamp.strftime("%d/%m %H:%M:%S"))
        self.type_label.update(text)
        self.priority_label.update(
            "Crítico" if criticality == "high" else "Normal",
            text_color="IndianRed1" if criticality == "high" else "orange",
        )
