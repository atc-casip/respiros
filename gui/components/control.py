"""
System control pane during operation.
"""

from typing import Dict, Optional

import PySimpleGUI as sg
from gui.config import cfg
from gui.context import Context
from gui.messenger import Messenger

from .sliders import IESlider, NumericSlider

FONT_FAMILY = "Helvetica"
FONT_SIZE = 20


class ParametersTab(sg.Tab):
    """Tab for parameter input."""

    # Sliders
    ipap: NumericSlider
    epap: NumericSlider
    freq: NumericSlider
    trigger: NumericSlider
    ie: IESlider

    def __init__(self):
        self.ipap = NumericSlider(
            "Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["ipap"]["min"],
                cfg["params"]["ipap"]["max"],
            ),
            default_value=cfg["params"]["ipap"]["default"],
        )
        self.epap = NumericSlider(
            "Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["epap"]["min"],
                cfg["params"]["epap"]["max"],
            ),
            default_value=cfg["params"]["epap"]["default"],
        )
        self.freq = NumericSlider(
            "Frecuencia",
            metric="rpm",
            values=(
                cfg["params"]["freq"]["min"],
                cfg["params"]["freq"]["max"],
            ),
            default_value=cfg["params"]["freq"]["default"],
        )
        self.trigger = NumericSlider(
            "Trigger de flujo",
            metric="ml",
            values=(
                cfg["params"]["trigger"]["min"],
                cfg["params"]["trigger"]["max"],
            ),
            default_value=cfg["params"]["trigger"]["default"],
        )
        self.ie = IESlider(
            inhale_max=cfg["params"]["inhale"]["max"],
            exhale_max=cfg["params"]["exhale"]["max"],
            default_value=(
                cfg["params"]["inhale"]["default"],
                cfg["params"]["exhale"]["default"],
            ),
        )

        super().__init__(
            "Parámetros",
            [
                [self.ipap],
                [self.epap],
                [self.freq],
                [self.trigger],
                [self.ie],
            ],
            border_width=10,
        )

    def expand(self):
        self.ipap.expand()
        self.epap.expand()
        self.freq.expand()
        self.trigger.expand()
        self.ie.expand()

    def update_values(
        self,
        ipap: int,
        epap: int,
        freq: int,
        trigger: int,
        inhale: int,
        exhale: int,
    ):
        """Update the tab's sliders with new values.

        Args:
            ipap (int): The value for IPAP.
            epap (int): The value for EPAP.
            freq (int): The value for respiratory frequency.
            trigger (int): The value for the airflow trigger.
            inhale (int): The value for inhale relative duration.
            exhale (int): The value for exhale relative duration.
        """

        self.ipap.value = ipap
        self.epap.value = epap
        self.freq.value = freq
        self.trigger.value = trigger
        self.ie.value = (inhale, exhale)

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ):
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
            ctx (Context): Application context.
            msg (Messenger): Messaging utility for inter-process communication.
        """

        change = False
        if event == self.ipap.slider.Key:
            self.ipap.value = ctx.ipap = values[event]
            change = True
            if self.ipap.value <= self.epap.value:
                self.epap.value = ctx.epap = self.ipap.value - 1
        elif event == self.epap.slider.Key:
            self.epap.value = ctx.epap = values[event]
            change = True
            if self.epap.value >= self.ipap.value:
                self.ipap.value = ctx.ipap = self.epap.value + 1
        elif event == self.freq.slider.Key:
            self.freq.value = ctx.freq = values[event]
            change = True
        elif event == self.trigger.slider.Key:
            self.trigger.value = ctx.trigger = values[event]
            change = True
        elif event == self.ie.slider.Key:
            self.ie.value = values[event]
            ctx.inhale = self.ie.value[0]
            ctx.exhale = self.ie.value[1]
            change = True

        if change:
            msg.send(
                "operation",
                {
                    "ipap": ctx.ipap,
                    "epap": ctx.epap,
                    "freq": ctx.freq,
                    "trigger": ctx.trigger,
                    "inhale": ctx.inhale,
                    "exhale": ctx.exhale,
                },
            )


class AlarmsTab(sg.Tab):
    """Tab for alarms' settings."""

    # Frames
    pressure_frame: sg.Frame
    volume_frame: sg.Frame
    oxygen_frame: sg.Frame
    freq_frame: sg.Frame

    # Sliders
    pressure_min: NumericSlider
    pressure_max: NumericSlider
    volume_min: NumericSlider
    volume_max: NumericSlider
    oxygen_min: NumericSlider
    oxygen_max: NumericSlider
    freq_max: NumericSlider

    # Buttons
    commit_btn: sg.Button

    def __init__(self):
        self.pressure_min = NumericSlider(
            "Min",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["alarms"]["pressure"]["min"],
                cfg["alarms"]["pressure"]["max"],
            ),
            default_value=cfg["alarms"]["pressure"]["min"],
        )
        self.pressure_max = NumericSlider(
            "Max",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["alarms"]["pressure"]["min"],
                cfg["alarms"]["pressure"]["max"],
            ),
            default_value=cfg["alarms"]["pressure"]["max"],
        )
        self.volume_min = NumericSlider(
            "Min",
            metric="l/min",
            values=(
                cfg["alarms"]["volume"]["min"],
                cfg["alarms"]["volume"]["max"],
            ),
            default_value=cfg["alarms"]["volume"]["min"],
        )
        self.volume_max = NumericSlider(
            "Max",
            metric="l/min",
            values=(
                cfg["alarms"]["volume"]["min"],
                cfg["alarms"]["volume"]["max"],
            ),
            default_value=cfg["alarms"]["volume"]["max"],
        )
        self.oxygen_min = NumericSlider(
            "Min",
            metric="%",
            values=(
                cfg["alarms"]["oxygen"]["min"],
                cfg["alarms"]["oxygen"]["max"],
            ),
            default_value=cfg["alarms"]["oxygen"]["min"],
        )
        self.oxygen_max = NumericSlider(
            "Max",
            metric="%",
            values=(
                cfg["alarms"]["oxygen"]["min"],
                cfg["alarms"]["oxygen"]["max"],
            ),
            default_value=cfg["alarms"]["oxygen"]["max"],
        )
        self.freq_max = NumericSlider(
            "Max",
            metric="rpm",
            values=(
                cfg["alarms"]["freq"]["min"],
                cfg["alarms"]["freq"]["max"],
            ),
            default_value=cfg["alarms"]["freq"]["max"],
        )

        self.pressure_frame = sg.Frame(
            "Presión",
            [[self.pressure_min, self.pressure_max]],
            font=("Helvetica", 15),
        )
        self.volume_frame = sg.Frame(
            "Volumen",
            [[self.volume_min, self.volume_max]],
            font=("Helvetica", 15),
        )
        self.oxygen_frame = sg.Frame(
            "Oxígeno",
            [[self.oxygen_min, self.oxygen_max]],
            font=("Helvetica", 15),
        )
        self.freq_frame = sg.Frame(
            "Frecuencia", [[self.freq_max]], font=("Helvetica", 15)
        )

        self.commit_btn = sg.Button("Aplicar", size=(10, 2))

        super().__init__(
            "Alarmas",
            [
                [self.commit_btn],
                [self.pressure_frame],
                [self.volume_frame],
                [self.oxygen_frame],
                [self.freq_frame],
            ],
            border_width=10,
            visible=False,
        )

    def expand(self):
        self.pressure_frame.expand(expand_x=True)
        self.volume_frame.expand(expand_x=True)
        self.oxygen_frame.expand(expand_x=True)
        self.freq_frame.expand(expand_x=True)

        self.pressure_min.expand()
        self.pressure_max.expand()
        self.volume_min.expand()
        self.volume_max.expand()
        self.oxygen_min.expand()
        self.oxygen_max.expand()
        self.freq_max.expand()

        self.commit_btn.expand(expand_x=True)

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ):
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
            ctx (Context): Application context.
            msg (Messenger): Messaging utility for inter-process communication.
        """

        if event == self.pressure_min.slider.Key:
            self.pressure_min.value = ctx.pressure_min = values[event]
            if self.pressure_min.value >= self.pressure_max.value:
                self.pressure_max.value = self.pressure_min.value + 1
        elif event == self.pressure_max.slider.Key:
            self.pressure_max.value = ctx.pressure_max = values[event]
            if self.pressure_max.value <= self.pressure_min.value:
                self.pressure_min.value = self.pressure_max.value - 1
        elif event == self.volume_min.slider.Key:
            self.volume_min.value = ctx.volume_min = values[event]
            if self.volume_min.value >= self.volume_max.value:
                self.volume_max.value = self.volume_min.value + 1
        elif event == self.volume_max.slider.Key:
            self.volume_max.value = ctx.volume_max = values[event]
            if self.volume_max.value <= self.volume_min.value:
                self.volume_min.value = self.volume_max.value - 1
        elif event == self.oxygen_min.slider.Key:
            self.oxygen_min.value = ctx.oxygen_min = values[event]
            if self.oxygen_min.value >= self.oxygen_max.value:
                self.oxygen_max.value = self.oxygen_min.value + 1
        elif event == self.oxygen_max.slider.Key:
            self.oxygen_max.value = ctx.oxygen_max = values[event]
            if self.oxygen_max.value <= self.oxygen_min.value:
                self.oxygen_min.value = self.oxygen_max.value - 1
        elif event == self.freq_max.slider.Key:
            self.freq_max.value = ctx.freq_max = values[event]
        elif event == self.commit_btn.Key:
            msg.send(
                "change-alarms",
                {
                    "pressure_min": ctx.pressure_min,
                    "pressure_max": ctx.pressure_max,
                    "volume_min": ctx.volume_min,
                    "volume_max": ctx.volume_max,
                    "oxygen_min": ctx.oxygen_min,
                    "oxygen_max": ctx.oxygen_max,
                    "freq_max": ctx.freq_max,
                },
            )


class HistoryTab(sg.Tab):
    """Tab for alarms' settings."""

    # Buttons
    silence_btn: sg.Button

    def __init__(self):
        self.silence_btn = sg.Button("Silenciar alarmas", size=(10, 2))

        super().__init__(
            "Histórico",
            [[self.silence_btn], [sg.Text("hist")]],
            border_width=10,
            visible=False,
        )

    def expand(self):
        self.silence_btn.expand(expand_x=True)

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ) -> Optional[str]:
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
            ctx (Context): Application context.
            msg (Messenger): Messaging utility for inter-process communication.

        Returns:
            Optional[str]: The route of the next view, or None.
        """

        return None


class ControlPane(sg.Column):
    """Pane with tabs for system control."""

    parameters: ParametersTab
    alarms: AlarmsTab
    history: HistoryTab

    tabs: sg.TabGroup

    parameters_btn: sg.Button
    alarms_btn: sg.Button
    history_btn: sg.Button

    __current_tab: sg.Tab

    def __init__(self):
        self.parameters = ParametersTab()
        self.alarms = AlarmsTab()
        self.history = HistoryTab()

        self.tabs = sg.TabGroup(
            [[self.parameters, self.alarms, self.history]],
            font=(FONT_FAMILY, FONT_SIZE),
            border_width=0,
        )

        self.parameters_btn = sg.Button("Parámetros", size=(10, 2))
        self.alarms_btn = sg.Button("Alarmas", size=(10, 2))
        self.history_btn = sg.Button("Histórico", size=(10, 2))

        self.__current_tab = self.parameters

        super().__init__(
            [
                [self.tabs],
                [self.parameters_btn, self.alarms_btn, self.history_btn],
            ]
        )

    def expand(self):
        super().expand(expand_x=True, expand_y=True)

        self.tabs.expand(expand_x=True, expand_y=True)

        self.parameters.expand()
        self.alarms.expand()
        self.history.expand()

        self.parameters_btn.expand(expand_x=True)
        self.alarms_btn.expand(expand_x=True)
        self.history_btn.expand(expand_x=True)

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ) -> Optional[str]:
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
            ctx (Context): Application context.
            msg (Messenger): Messaging utility for inter-process communication.

        Returns:
            Optional[str]: The route of the next view, or None.
        """

        if (
            event == self.parameters_btn.Key
            and self.__current_tab is not self.parameters
        ):
            self.__current_tab.update(visible=False)
            self.__current_tab = self.parameters
            self.__current_tab.select()
        elif (
            event == self.alarms_btn.Key
            and self.__current_tab is not self.alarms
        ):
            self.__current_tab.update(visible=False)
            self.__current_tab = self.alarms
            self.__current_tab.select()
        elif (
            event == self.history_btn.Key
            and self.__current_tab is not self.history
        ):
            self.__current_tab.update(visible=False)
            self.__current_tab = self.history
            self.__current_tab.select()

        return self.__current_tab.handle_event(event, values, ctx, msg)
