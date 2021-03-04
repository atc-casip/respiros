import gui.events as events
import gui.style as style
import PySimpleGUI as sg
from common.alarms import Criticality


class DisplayUnit(sg.Column):
    def __init__(self, title: str, metric: str, size: int, font_size: int):
        self.__value = 0.0
        self.__metric = metric

        self.title_label = sg.Text(
            f"{title}:", font=(style.FONT_FAMILY, font_size, "bold")
        )
        self.value_label = sg.Text(
            f"-   {self.__metric}",
            font=(style.FONT_FAMILY, font_size, "bold"),
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


class MonitorBar(sg.Column):
    """System bar for parameter monitoring."""

    def __init__(self):
        # Displays
        self.ipap = DisplayUnit(
            "IPAP", "cmH\N{SUBSCRIPT TWO}O", 10, style.FONT_SIZE_BIG
        )
        self.epap = DisplayUnit(
            "EPAP", "cmH\N{SUBSCRIPT TWO}O", 10, style.FONT_SIZE_BIG
        )
        self.freq = DisplayUnit("Frecuencia", "rpm", 8, style.FONT_SIZE_BIG)
        self.vc_in = DisplayUnit("V (in)", "ml", 5, style.FONT_SIZE_SMALL)
        self.vc_out = DisplayUnit("V (out)", "ml", 5, style.FONT_SIZE_SMALL)
        self.oxygen = DisplayUnit(
            "O\N{SUBSCRIPT TWO}", "%", 4, style.FONT_SIZE_SMALL
        )

        # Buttons
        self.lock_btn = sg.Button(
            "Bloquear",
            size=(9, 2),
            font=(style.FONT_FAMILY, style.FONT_SIZE_SMALL),
            key=events.LOCK_SCREEN_BUTTON_OPER,
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
