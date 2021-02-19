import datetime
import PySimpleGUI as sg


class AlarmCard(sg.Column):
    def __init__(self, last: bool = False):
        self.timestamp_label = sg.Text(
            "", size=(13, 1), font=("Helvetica", 18)
        )
        self.type_label = sg.Text("", size=(15, 1), font=("Helvetica", 18))
        self.priority_label = sg.Text(
            "",
            size=(10, 1),
            font=("Helvetica", 18, "bold"),
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
        if type == "pressure_min":
            text = "Presión baja"
        elif type == "pressure_max":
            text = "Presión alta"
        elif type == "volume_min":
            text = "Volumen bajo"
        elif type == "volume_max":
            text = "Volumen alto"
        elif type == "oxygen_min":
            text = "Oxígeno bajo"
        elif type == "oxygen_max":
            text = "Oxígeno alto"
        elif type == "freq_max":
            text = "Frecuencia alta"

        self.timestamp_label.update(timestamp.strftime("%d/%m %H:%M:%S"))
        self.type_label.update(text)
        self.priority_label.update(
            "Crítico" if criticality == "high" else "Normal",
            text_color="IndianRed1" if criticality == "high" else "orange",
        )
