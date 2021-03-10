from typing import Dict

import PySimpleGUI as sg
from gui.component import Component
from gui.ipc import ZMQEvent

from .tabs import AlarmsTab, HistoryTab, ParametersTab


class ControlPane(Component):
    """Pane with tabs for system control."""

    def __init__(self, app):
        super().__init__(app)
        self.__locked = False

        # Tabs
        self.parameters = ParametersTab(app)
        self.alarms = AlarmsTab(app)
        self.history = HistoryTab(app)
        self.__current_tab = None

        # Labels
        self.tab_label = sg.Text(
            size=(10, 1),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_BIG"]),
        )
        self.mode_label = sg.Text(
            size=(5, 1),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_BIG"]),
            justification="right",
        )

        # Buttons
        self.parameters_btn = sg.Button(
            self.parameters.title,
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )
        self.alarms_btn = sg.Button(
            self.alarms.title,
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )
        self.history_btn = sg.Button(
            self.history.title,
            size=(10, 2),
            font=(app.config["FONT_FAMILY"], app.config["FONT_SIZE_SMALL"]),
        )

        # Misc
        self.expander = sg.Text()

        self.layout(
            [
                [self.tab_label, self.expander, self.mode_label],
                [self.parameters, self.alarms, self.history],
                [self.parameters_btn, self.alarms_btn, self.history_btn],
            ]
        )

    def handle_event(self, event: str, values: Dict):
        self.__current_tab.handle_event(event, values)
        if event == self.parameters_btn.Key:
            self.show_tab(self.parameters)
        elif event == self.alarms_btn.Key:
            self.show_tab(self.alarms)
        elif event == self.history_btn.Key:
            self.show_tab(self.history)
        elif event == ZMQEvent.OPER_MODE.name:
            self.app.ctx.mode = values[event]["mode"]
            self.mode_label.update(self.app.ctx.mode.upper())
            self.parameters.switch_mode()

        if self.__locked != self.app.ctx.locked:
            self.__locked = self.app.ctx.locked
            if self.__locked:
                self.parameters.lock()
                self.alarms.lock()
                self.history.lock()
            else:
                self.parameters.unlock()
                self.alarms.unlock()
                self.history.unlock()

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.expander.expand(expand_x=True, expand_row=False)
        self.parameters_btn.expand(expand_x=True, expand_row=False)
        self.alarms_btn.expand(expand_x=True, expand_row=False)
        self.history_btn.expand(expand_x=True, expand_row=False)

        self.parameters.ipap_vcp.value = (
            self.parameters.ipap_vps.value
        ) = self.app.ctx.ipap
        self.parameters.epap_vcp.value = (
            self.parameters.epap_vps.value
        ) = self.app.ctx.epap
        self.parameters.freq_vcp.value = self.app.ctx.freq
        self.parameters.trigger_vcp.value = (
            self.parameters.trigger_vps.value
        ) = self.app.ctx.trigger
        self.parameters.ie_vcp.value = (
            self.app.ctx.inhale,
            self.app.ctx.exhale,
        )

        self.mode_label.update(self.app.ctx.mode.upper())

        super().show()

    def show_tab(self, tab):
        """Show the specified tab

        Args:
            tab (ControlTab): The tab itself.
        """

        if self.__current_tab:
            self.__current_tab.hide()
            if isinstance(self.__current_tab, ParametersTab):
                self.parameters_btn.update(disabled=False)
            elif isinstance(self.__current_tab, AlarmsTab):
                self.alarms_btn.update(disabled=False)
            elif isinstance(self.__current_tab, HistoryTab):
                self.history_btn.update(disabled=False)

        self.__current_tab = tab

        self.__current_tab.show()
        if isinstance(self.__current_tab, ParametersTab):
            self.parameters_btn.update(disabled=True)
        elif isinstance(self.__current_tab, AlarmsTab):
            self.alarms_btn.update(disabled=True)
        elif isinstance(self.__current_tab, HistoryTab):
            self.history_btn.update(disabled=True)

        self.tab_label.update(self.__current_tab.title)
