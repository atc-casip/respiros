from abc import ABCMeta, abstractmethod
from typing import Dict

import PySimpleGUI as sg


class Component(sg.Column, metaclass=ABCMeta):
    """Base class for GUI components.

    All views and other smaller components extend this class.
    """

    def __init__(self, app, *args, **kwargs):
        super().__init__([], *args, **kwargs)
        self.app = app
        self.children = []

    @abstractmethod
    def handle_event(self, event: str, values: Dict):
        """Perform the appropiate logic in response to an event.

        Args:
            event (str): The event key.
            values (Dict): Map of values associated to the window.
        """

        for c in self.children:
            c.handle_event(event, values)

    def show(self):
        """Make the component visible."""

        self.update(visible=True)
        for c in self.children:
            c.show()

    def hide(self):
        """Make the component invisible."""

        self.update(visible=False)
