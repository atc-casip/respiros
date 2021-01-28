"""
Slider components for user input.
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple, Union

import PySimpleGUI as sg

FONT_FAMILY = "Helvetica"
FONT_SIZE = 15


class ParameterSlider(ABC, sg.Column):
    """Custom slider component for parameter selection."""

    title_label: sg.Text
    value_label: sg.Text
    slider: sg.Slider

    @property
    @abstractmethod
    def value(self) -> Any:
        """The slider's value.

        Returns:
            Any: The current value.
        """

    @value.setter
    @abstractmethod
    def value(self, new_value: Any):
        """Change the value of the slider.

        Args:
            new_value (Any): The new value.
        """

    def expand(self):
        """Expand the slider in the X axis."""

        super().expand(expand_x=True)
        self.title_label.expand(expand_x=True)
        self.slider.expand(expand_x=True)


class NumericSlider(ParameterSlider):
    """Slider for numerical parameters."""

    __value: int

    metric_label: sg.Text

    def __init__(
        self,
        label: str,
        metric: str,
        values: Tuple[int, int],
        default_value: int,
    ):
        self.__value = default_value

        self.title_label = sg.Text(label, font=(FONT_FAMILY, FONT_SIZE))
        self.metric_label = sg.Text(metric, font=(FONT_FAMILY, FONT_SIZE))
        self.value_label = sg.Text(
            default_value,
            size=(5, 1),
            justification="right",
            font=(FONT_FAMILY, FONT_SIZE),
        )
        self.slider = sg.Slider(
            range=values,
            default_value=self.__value,
            disable_number_display=True,
            orientation="h",
            size=(0, 50),
            enable_events=True,
        )

        super().__init__(
            [
                [self.title_label, self.value_label, self.metric_label],
                [self.slider],
            ]
        )

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, new_value: float):
        self.__value = int(new_value)

        self.value_label.update(self.__value)
        self.slider.update(self.__value)


class IESlider(ParameterSlider):
    """Special slider for the inhale-exhale relation."""

    __value: int

    def __init__(
        self,
        inhale_max: int,
        exhale_max: int,
        default_value: Tuple[int, int],
    ):
        self.__value = self.__tuple_to_int(default_value)

        self.title_label = sg.Text("Relación I:E", font=(FONT_FAMILY, FONT_SIZE))
        self.value_label = sg.Text(
            f"{default_value[0]}:{default_value[1]}",
            size=(5, 1),
            justification="right",
            font=(FONT_FAMILY, FONT_SIZE),
        )
        self.slider = sg.Slider(
            range=((inhale_max - 1) * -1, exhale_max - 1),
            default_value=self.__value,
            disable_number_display=True,
            orientation="h",
            size=(0, 50),
            enable_events=True,
        )

        super().__init__([[self.title_label, self.value_label], [self.slider]])

    @property
    def value(self) -> Tuple[int, int]:
        inhale = exhale = 1
        if self.__value > 0:
            exhale = self.__value + 1
        elif self.__value < 0:
            inhale = abs(self.__value) + 1
        return inhale, exhale

    @value.setter
    def value(self, new_value: Union[Tuple[int, int], float]):
        if isinstance(new_value, float):
            self.__value = int(new_value)

            str_value = "1:1"
            if self.__value > 0:
                str_value = f"1:{self.__value+1}"
            elif self.__value < 0:
                str_value = f"{abs(self.__value)+1}:1"

            self.value_label.update(str_value)
            self.slider.update(self.__value)
        else:
            self.__value = self.__tuple_to_int(new_value)

            self.value_label.update(f"{new_value[0]}:{new_value[1]}")
            self.slider.update(self.__value)

    def __tuple_to_int(self, values: Tuple[int, int]) -> int:
        """Obtain the single integer version of the inhale-exhale relation.

        Args:
            values (Tuple[int, int]): Values as a tuple.

        Returns:
            int: The single integer representation.
        """

        int_value = 0
        if values[0] > 1:
            int_value = (values[0] - 1) * -1
        elif values[1] > 1:
            int_value = values[1] - 1
        return int_value
