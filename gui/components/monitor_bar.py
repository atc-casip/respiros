import PySimpleGUI as sg

import gui.events as events

FONT_FAMILY = "Helvetica"
FONT_SIZE_BIG = 20
FONT_SIZE_SMALL = 12
FONT_STYLE = "bold"


class DisplayUnit(sg.Column):
    def __init__(self, title: str, metric: str, size: int, font_size: int):
        self.__value = 0.0
        self.__metric = metric

        self.title_label = sg.Text(
            f"{title}:", font=(FONT_FAMILY, font_size, FONT_STYLE)
        )
        self.value_label = sg.Text(
            f"-   {self.__metric}",
            font=(FONT_FAMILY, font_size, FONT_STYLE),
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

    def show_alarm(self, criticality: str):
        """Change the color of the unit to reflect an alarm.

        Args:
            criticality (str): Level of criticality.
        """

        if criticality == "none":
            self.title_label.update(text_color="white")
            self.value_label.update(text_color="white")
        elif criticality == "medium":
            self.title_label.update(text_color="orange")
            self.value_label.update(text_color="orange")
        elif criticality == "high":
            self.title_label.update(text_color="red")
            self.value_label.update(text_color="red")


class MonitorBar(sg.Column):
    """System bar for parameter monitoring."""

    def __init__(self):
        # Displays
        self.ipap = DisplayUnit(
            "IPAP", "cmH\N{SUBSCRIPT TWO}O", 10, FONT_SIZE_BIG
        )
        self.epap = DisplayUnit(
            "EPAP", "cmH\N{SUBSCRIPT TWO}O", 10, FONT_SIZE_BIG
        )
        self.freq = DisplayUnit("Frecuencia", "rpm", 7, FONT_SIZE_BIG)
        self.vc_in = DisplayUnit("V (in)", "ml", 5, FONT_SIZE_SMALL)
        self.vc_out = DisplayUnit("V (out)", "ml", 5, FONT_SIZE_SMALL)
        self.oxygen = DisplayUnit(
            "O\N{SUBSCRIPT TWO}", "%", 4, FONT_SIZE_SMALL
        )

        # Buttons
        self.lock_btn = sg.RealtimeButton(
            "Bloquear", size=(9, 2), key=events.LOCK_SCREEN_BUTTON_OPER
        )

        # Misc
        self.expander = sg.Text()

        super().__init__(
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

    def expand(self):
        super().expand(expand_x=True)
        self.expander.expand(expand_x=True)
