from typing import Dict, Tuple, Union

import PySimpleGUI as sg
from gui.component import Component


class NumericSlider(Component):
    """Slider for numerical parameters."""

    def __init__(
        self,
        app,
        label: str,
        metric: str,
        values: Tuple[int, int],
        default_value: int,
    ):
        super().__init__(app)
        self.__value = default_value

        self.title_label = sg.Text(
            label,
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.metric_label = sg.Text(
            metric,
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.value_label = sg.Text(
            default_value,
            size=(5, 1),
            justification="right",
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.slider = sg.Slider(
            range=values,
            default_value=self.__value,
            disable_number_display=True,
            orientation="h",
            size=(0, 50),
            enable_events=True,
        )

        self.layout(
            [
                [self.title_label, self.value_label, self.metric_label],
                [self.slider],
            ]
        )

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int):
        self.__value = value
        self.value_label.update(value)
        self.slider.update(value)

    def handle_event(self, event: str, values: Dict):
        if event == self.slider.Key:
            self.value = int(values[event])

    def show(self):
        self.expand(expand_x=True)
        self.title_label.expand(expand_x=True)
        self.slider.expand(expand_x=True)
        super().show()


class IESlider(Component):
    """Special slider for the inhale-exhale relation."""

    def __init__(
        self,
        app,
        inhale_max: int,
        exhale_max: int,
        default_value: Tuple[int, int],
    ):
        super().__init__(app)
        self.__value = self.__ie_to_int(default_value)

        self.title_label = sg.Text(
            "Relación I:E",
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.value_label = sg.Text(
            f"{default_value[0]}:{default_value[1]}",
            size=(5, 1),
            justification="right",
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_MEDIUM"]),
        )
        self.slider = sg.Slider(
            range=((inhale_max - 1) * -1, exhale_max - 1),
            default_value=self.__value,
            disable_number_display=True,
            orientation="h",
            size=(0, 50),
            enable_events=True,
        )

        self.layout([[self.title_label, self.value_label], [self.slider]])

    @property
    def value(self) -> Tuple[int, int]:
        inhale = exhale = 1
        if self.__value > 0:
            exhale = self.__value + 1
        elif self.__value < 0:
            inhale = abs(self.__value) + 1
        return inhale, exhale

    @value.setter
    def value(self, value: Union[Tuple[int, int], float]):
        if not isinstance(value, tuple):
            self.__value = value

            self.value_label.update(
                ":".join(str(i) for i in self.__int_to_ie(self.__value))
            )
            self.slider.update(self.__value)
        else:
            self.__value = self.__ie_to_int(value)

            self.value_label.update(f"{value[0]}:{value[1]}")
            self.slider.update(self.__value)

    def handle_event(self, event: str, values: Dict):
        if event == self.slider.Key:
            self.value = int(values[event])

    def show(self):
        self.expand(expand_x=True)
        self.title_label.expand(expand_x=True)
        self.slider.expand(expand_x=True)
        super().show()

    def __ie_to_int(self, values: Tuple[int, int]) -> int:
        """Obtain the single integer version of the inhale-exhale relation.

        Args:
            values (Tuple[int, int]): Value as a tuple.

        Returns:
            int: The single integer representation.
        """

        int_value = 0
        if values[0] > 1:
            int_value = (values[0] - 1) * -1
        elif values[1] > 1:
            int_value = values[1] - 1
        return int_value

    def __int_to_ie(self, value: int) -> Tuple[int, int]:
        """Obtain the tuple representation of the inhale-exhale relation.

        Args:
            value (int): Single integer representation.

        Returns:
            Tuple[int, int]: Value as a tuple.
        """

        if value > 0:
            return 1, value + 1
        elif value < 0:
            return abs(value) + 1, 1
        else:
            return 1, 1
