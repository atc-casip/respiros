from abc import ABCMeta, abstractmethod
from typing import Dict

import common.ipc.topics as topics
import gui.events as events
import gui.style as style
import PySimpleGUI as sg
from gui.components.alarm_card import AlarmCard
from gui.config import cfg
from gui.context import ctx
from gui.messenger import msg

from .sliders import IESlider, NumericSlider


class ControlTab(sg.Column, metaclass=ABCMeta):
    """Base class for tabs in the control pane."""

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(visible=False, *args, **kwargs)
        self.__title = title

    @property
    def title(self) -> str:
        return self.__title

    def show(self):
        super().update(visible=True)

    def hide(self):
        super().update(visible=False)

    @abstractmethod
    def lock(self):
        return

    @abstractmethod
    def unlock(self):
        return

    @abstractmethod
    def handle_event(self, event: str, values: Dict):
        """Perform the appropiate logic in response to an event.

        Args:
            event (str): The event itself.
            values (Dict): This dict holds all the values of the views'
            components.
        """


class ParametersTab(ControlTab):
    """Tab for operation control."""

    def __init__(self):
        # Sliders
        self.ipap = NumericSlider(
            "Presión IPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["ipap"]["min"],
                cfg["params"]["ipap"]["max"],
            ),
            default_value=cfg["params"]["ipap"]["default"],
            key=events.IPAP_SLIDER_OPER,
        )
        self.epap = NumericSlider(
            "Presión EPAP",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["params"]["epap"]["min"],
                cfg["params"]["epap"]["max"],
            ),
            default_value=cfg["params"]["epap"]["default"],
            key=events.EPAP_SLIDER_OPER,
        )
        self.freq = NumericSlider(
            "Frecuencia",
            metric="rpm",
            values=(
                cfg["params"]["freq"]["min"],
                cfg["params"]["freq"]["max"],
            ),
            default_value=cfg["params"]["freq"]["default"],
            key=events.FREQ_SLIDER_OPER,
        )
        self.trigger = NumericSlider(
            "Trigger de flujo",
            metric="ml",
            values=(
                cfg["params"]["trigger"]["min"],
                cfg["params"]["trigger"]["max"],
            ),
            default_value=cfg["params"]["trigger"]["default"],
            key=events.TRIGGER_SLIDER_OPER,
        )
        self.ie = IESlider(
            inhale_max=cfg["params"]["inhale"]["max"],
            exhale_max=cfg["params"]["exhale"]["max"],
            default_value=(
                cfg["params"]["inhale"]["default"],
                cfg["params"]["exhale"]["default"],
            ),
            key=events.IE_SLIDER_OPER,
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
        )

    def show(self):
        super().expand(expand_x=True, expand_y=True)
        self.ipap.expand()
        self.epap.expand()
        self.freq.expand()
        self.trigger.expand()
        self.ie.expand()

        super().show()

    def lock(self):
        self.ipap.slider.update(disabled=True)
        self.epap.slider.update(disabled=True)
        self.freq.slider.update(disabled=True)
        self.trigger.slider.update(disabled=True)
        self.ie.slider.update(disabled=True)

    def unlock(self):
        self.ipap.slider.update(disabled=False)
        self.epap.slider.update(disabled=False)
        self.freq.slider.update(disabled=False)
        self.trigger.slider.update(disabled=False)
        self.ie.slider.update(disabled=False)

    def handle_event(self, event: str, values: Dict):
        change = False
        if event == events.IPAP_SLIDER_OPER:
            self.ipap.value = ctx.ipap = int(values[event])
            change = True
            if self.ipap.value <= self.epap.value:
                self.epap.value = ctx.epap = self.ipap.value - 1
        elif event == events.EPAP_SLIDER_OPER:
            self.epap.value = ctx.epap = int(values[event])
            change = True
            if self.epap.value >= self.ipap.value:
                self.ipap.value = ctx.ipap = self.epap.value + 1
        elif event == events.FREQ_SLIDER_OPER:
            self.freq.value = ctx.freq = int(values[event])
            change = True
        elif event == events.TRIGGER_SLIDER_OPER:
            self.trigger.value = ctx.trigger = int(values[event])
            change = True
        elif event == events.IE_SLIDER_OPER:
            self.ie.value = int(values[event])
            ctx.inhale = self.ie.value[0]
            ctx.exhale = self.ie.value[1]
            change = True

        if change:
            msg.send(
                topics.OPERATION_PARAMS,
                {
                    "ipap": ctx.ipap,
                    "epap": ctx.epap,
                    "freq": ctx.freq,
                    "trigger": ctx.trigger,
                    "inhale": ctx.inhale,
                    "exhale": ctx.exhale,
                },
            )


class AlarmsTab(ControlTab):
    """Tab for alarm range control."""

    def __init__(self):
        # Sliders
        self.pressure_min = NumericSlider(
            "Min",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["alarms"]["pressure"]["min"],
                cfg["alarms"]["pressure"]["max"],
            ),
            default_value=cfg["alarms"]["pressure"]["min"],
            key=events.PRESSURE_MIN_SLIDER_OPER,
        )
        self.pressure_max = NumericSlider(
            "Max",
            metric="cmH\N{SUBSCRIPT TWO}O",
            values=(
                cfg["alarms"]["pressure"]["min"],
                cfg["alarms"]["pressure"]["max"],
            ),
            default_value=cfg["alarms"]["pressure"]["max"],
            key=events.PRESSURE_MAX_SLIDER_OPER,
        )
        self.volume_min = NumericSlider(
            "Min",
            metric="l/min",
            values=(
                cfg["alarms"]["volume"]["min"],
                cfg["alarms"]["volume"]["max"],
            ),
            default_value=cfg["alarms"]["volume"]["min"],
            key=events.VOLUME_MIN_SLIDER_OPER,
        )
        self.volume_max = NumericSlider(
            "Max",
            metric="l/min",
            values=(
                cfg["alarms"]["volume"]["min"],
                cfg["alarms"]["volume"]["max"],
            ),
            default_value=cfg["alarms"]["volume"]["max"],
            key=events.VOLUME_MAX_SLIDER_OPER,
        )
        self.oxygen_min = NumericSlider(
            "Min",
            metric="%",
            values=(
                cfg["alarms"]["oxygen"]["min"],
                cfg["alarms"]["oxygen"]["max"],
            ),
            default_value=cfg["alarms"]["oxygen"]["min"],
            key=events.OXYGEN_MIN_SLIDER_OPER,
        )
        self.oxygen_max = NumericSlider(
            "Max",
            metric="%",
            values=(
                cfg["alarms"]["oxygen"]["min"],
                cfg["alarms"]["oxygen"]["max"],
            ),
            default_value=cfg["alarms"]["oxygen"]["max"],
            key=events.OXYGEN_MAX_SLIDER_OPER,
        )
        self.freq_max = NumericSlider(
            "Max",
            metric="rpm",
            values=(
                cfg["alarms"]["freq"]["min"],
                cfg["alarms"]["freq"]["max"],
            ),
            default_value=cfg["alarms"]["freq"]["max"],
            key=events.FREQ_MAX_SLIDER_OPER,
        )

        # Frames
        self.pressure_frame = sg.Frame(
            "Presión",
            [[self.pressure_min, self.pressure_max]],
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )
        self.volume_frame = sg.Frame(
            "Volumen",
            [[self.volume_min, self.volume_max]],
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )
        self.oxygen_frame = sg.Frame(
            "Oxígeno",
            [[self.oxygen_min, self.oxygen_max]],
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )
        self.freq_frame = sg.Frame(
            "Frecuencia",
            [[self.freq_max]],
            font=(style.FONT_FAMILY, style.FONT_SIZE_MEDIUM),
        )

        # Buttons
        self.commit_btn = sg.Button(
            "Aplicar",
            size=(10, 2),
            font=(style.FONT_FAMILY, style.FONT_SIZE_SMALL),
            key=events.APPLY_ALARMS_BUTTON_OPER,
        )

        super().__init__(
            "Alarmas",
            [
                [self.commit_btn],
                [self.pressure_frame],
                [self.volume_frame],
                [self.oxygen_frame],
                [self.freq_frame],
            ],
        )

    def show(self):
        super().expand(expand_x=True, expand_y=True)
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

        super().show()

    def lock(self):
        self.pressure_min.slider.update(disabled=True)
        self.pressure_max.slider.update(disabled=True)
        self.volume_min.slider.update(disabled=True)
        self.volume_max.slider.update(disabled=True)
        self.oxygen_min.slider.update(disabled=True)
        self.oxygen_max.slider.update(disabled=True)
        self.freq_max.slider.update(disabled=True)
        self.commit_btn.update(disabled=True)

    def unlock(self):
        self.pressure_min.slider.update(disabled=False)
        self.pressure_max.slider.update(disabled=False)
        self.volume_min.slider.update(disabled=False)
        self.volume_max.slider.update(disabled=False)
        self.oxygen_min.slider.update(disabled=False)
        self.oxygen_max.slider.update(disabled=False)
        self.freq_max.slider.update(disabled=False)
        self.commit_btn.update(disabled=False)

    def handle_event(self, event: str, values: Dict):
        if event == events.PRESSURE_MIN_SLIDER_OPER:
            self.pressure_min.value = ctx.pressure_min = int(values[event])
            if self.pressure_min.value >= self.pressure_max.value:
                self.pressure_max.value = self.pressure_min.value + 1
        elif event == events.PRESSURE_MAX_SLIDER_OPER:
            self.pressure_max.value = ctx.pressure_max = int(values[event])
            if self.pressure_max.value <= self.pressure_min.value:
                self.pressure_min.value = self.pressure_max.value - 1
        elif event == events.VOLUME_MIN_SLIDER_OPER:
            self.volume_min.value = ctx.volume_min = int(values[event])
            if self.volume_min.value >= self.volume_max.value:
                self.volume_max.value = self.volume_min.value + 1
        elif event == events.VOLUME_MAX_SLIDER_OPER:
            self.volume_max.value = ctx.volume_max = int(values[event])
            if self.volume_max.value <= self.volume_min.value:
                self.volume_min.value = self.volume_max.value - 1
        elif event == events.OXYGEN_MIN_SLIDER_OPER:
            self.oxygen_min.value = ctx.oxygen_min = int(values[event])
            if self.oxygen_min.value >= self.oxygen_max.value:
                self.oxygen_max.value = self.oxygen_min.value + 1
        elif event == events.OXYGEN_MAX_SLIDER_OPER:
            self.oxygen_max.value = ctx.oxygen_max = int(values[event])
            if self.oxygen_max.value <= self.oxygen_min.value:
                self.oxygen_min.value = self.oxygen_max.value - 1
        elif event == events.FREQ_MAX_SLIDER_OPER:
            self.freq_max.value = ctx.freq_max = int(values[event])
        elif event == events.APPLY_ALARMS_BUTTON_OPER:
            msg.send(
                topics.OPERATION_ALARMS,
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


class HistoryTab(ControlTab):
    """Tab that shows the history of triggered alarms."""

    def __init__(self):
        # Buttons
        self.silence_btn = sg.Button(
            "Silenciar alarmas",
            size=(10, 2),
            font=(style.FONT_FAMILY, style.FONT_SIZE_SMALL),
            key=events.SILENCE_ALARMS_BUTTON_OPER,
        )

        # Alarm cards
        self.alarm_cards = []
        for i in range(10):
            if i == 9:
                self.alarm_cards.append(AlarmCard(last=True))
            else:
                self.alarm_cards.append(AlarmCard())

        super().__init__(
            "Histórico",
            [[self.silence_btn]] + [[card] for card in self.alarm_cards],
        )

    def show(self):
        super().expand(expand_x=True, expand_y=True)
        self.silence_btn.expand(expand_x=True)
        for card in self.alarm_cards:
            card.expand()

        super().show()

    def lock(self):
        self.silence_btn.update(disabled=True)

    def unlock(self):
        self.silence_btn.update(disabled=False)

    def handle_event(self, event: str, values: Dict):
        if event == events.SILENCE_ALARMS_BUTTON_OPER:
            msg.send(topics.SILENCE_ALARMS, {})

    def refresh_alarms(self):
        for a, c in zip(ctx.alarms, self.alarm_cards):
            c.update(a.type, a.criticality, a.timestamp)
