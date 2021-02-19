from typing import Dict

import PySimpleGUI as sg

from .control_tabs import AlarmsTab, ControlTab, HistoryTab, ParametersTab

FONT_FAMILY = "Helvetica"
FONT_SIZE = 20


class ControlPane(sg.Column):
    """Pane with tabs for system control."""

    def __init__(self):
        # Tabs
        self.parameters = self.__current_tab = ParametersTab()
        self.alarms = AlarmsTab()
        self.history = HistoryTab()

        # Labels
        self.tab_label = sg.Text(
            self.__current_tab.title, font=(FONT_FAMILY, FONT_SIZE)
        )
        self.mode_label = sg.Text("VCP", font=(FONT_FAMILY, FONT_SIZE))

        # Buttons
        self.parameters_btn = sg.Button(
            self.parameters.title,
            size=(10, 2),
            font=("Helvetica", 12),
            disabled=True,
        )
        self.alarms_btn = sg.Button(
            self.alarms.title,
            size=(10, 2),
            font=("Helvetica", 12),
        )
        self.history_btn = sg.Button(
            self.history.title,
            size=(10, 2),
            font=("Helvetica", 12),
        )

        # Misc
        self.expander = sg.Text()

        super().__init__(
            [
                [self.tab_label, self.expander, self.mode_label],
                [self.parameters, self.alarms, self.history],
                [self.parameters_btn, self.alarms_btn, self.history_btn],
            ]
        )

    def show_tab(self, tab: ControlTab):
        """Show the specified tab

        Args:
            tab (ControlTab): The tab itself.
        """

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

    def expand(self):
        super().expand(expand_x=True, expand_y=True)
        self.expander.expand(expand_x=True, expand_row=False)
        self.parameters_btn.expand(expand_x=True, expand_row=False)
        self.alarms_btn.expand(expand_x=True, expand_row=False)
        self.history_btn.expand(expand_x=True, expand_row=False)

        self.__current_tab.show()

    def handle_event(self, event: str, values: Dict):
        """React to the event provided by the event loop.

        Args:
            event (str): The key of the element that dispatched the event.
            values (Dict): Dictionary of values present in the window.
        """

        if event == self.parameters_btn.Key:
            self.show_tab(self.parameters)
        elif event == self.alarms_btn.Key:
            self.show_tab(self.alarms)
        elif event == self.history_btn.Key:
            self.show_tab(self.history)
        else:
            self.__current_tab.handle_event(event, values)
