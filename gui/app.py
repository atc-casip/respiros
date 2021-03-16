import logging

import PySimpleGUI as sg
from flask.config import Config

sg.theme("Black")  # Use the dark theme


class GUIApplication(sg.Window):
    """The ventilator's GUI application.

    Monitoring data is shown to users, who can also control the system with
    their inputs.
    """

    def __init__(self):
        super().__init__("RespirOS", size=(1366, 768), margins=(10, 10))
        self.config = Config({})

    def run(self):
        """Main loop of the application."""

        self.current_view.show()
        while True:
            event, values = super().read()
            self.current_view.handle_event(event, values)

    def show_view(self, view):
        """Show the specified view.

        As PySimpleGUI doesn't support navigation as we know it, the app is
        created with all the views as columns. We can achieve a behaviour akin
        to navigation by making the views visible and invisible.

        Args:
            view: The class of the view to show.
        """

        logging.info("Showing view %s", view.__name__)
        self.current_view.hide()
        self.current_view = self.views[view.__name__]
        self.current_view.show()
