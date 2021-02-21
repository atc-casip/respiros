import threading

import common.ipc.topics as topics
import PySimpleGUI as sg

import gui.events as events
import gui.style as style
import gui.views as views
from gui.messenger import msg


class App(sg.Window):
    """The ventilator's GUI application.

    Monitoring data is shown to users, who can also control the system with
    their inputs.
    """

    def __init__(self, initial_view=views.LoadingView):
        sg.theme(style.THEME)

        super().__init__("RespirOS", size=(1366, 768), margins=(10, 10))

        self.__views = {}
        for v in map(views.__dict__.get, views.__all__):
            self.__views[v.__name__] = v(self)

        super().layout([list(self.__views.values())]).finalize()

        self.__current_view = self.__views[initial_view.__name__]
        self.__current_view.show()

    def show_view(self, view):
        """Show the specified view.

        As PySimpleGUI doesn't support navigation as we know it, the app is
        created with all the views as columns. We can achieve a behaviour akin
        to navigation by making the views visible and invisible.

        Args:
            view : The class of the view to show.
        """

        self.__current_view.hide()
        self.__current_view = self.__views[view.__name__]
        self.__current_view.show()

    def run(self):
        """Main loop of the application."""

        threading.Thread(target=self.check_ipc, daemon=True).start()

        while True:
            event, values = super().read()
            self.__current_view.handle_event(event, values)

    def check_ipc(self):
        """Receive messages from other system processes.

        This function is meant to be run on a different thread than the main
        loop. When a new message is received, it is sent to the window just
        like a normal event, so it can be handled by the views.
        """

        while True:
            topic, body = msg.recv()
            if topic == topics.CHECK:
                super().write_event_value(events.ZMQ_CHECK, body)
            elif topic == topics.READING:
                super().write_event_value(events.ZMQ_READING, body)
            elif topic == topics.CYCLE:
                super().write_event_value(events.ZMQ_CYCLE, body)
            elif topic == topics.ALARM:
                super().write_event_value(events.ZMQ_ALARM, body)
            elif topic == topics.OPERATION_MODE:
                super().write_event_value(events.ZMQ_OPER_MODE, body)
