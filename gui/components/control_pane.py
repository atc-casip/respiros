from typing import Dict

import PySimpleGUI as sg

from .control_tabs import AlarmsTab, HistoryTab, ParametersTab

FONT_FAMILY = "Helvetica"
FONT_SIZE = 20


class ControlPane(sg.Column):
    """Pane with tabs for system control."""

    def __init__(self):
        # Tabs
        self.parameters = ParametersTab()
        self.alarms = AlarmsTab()
        self.history = HistoryTab()
        self.tabs = sg.TabGroup(
            [[self.parameters, self.alarms, self.history]],
            font=(FONT_FAMILY, FONT_SIZE),
            border_width=0,
        )

        # Buttons
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

    def handle_event(self, event: str, values: Dict):
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
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

        return self.__current_tab.handle_event(event, values)
