from abc import ABCMeta, abstractmethod
from typing import Dict

import PySimpleGUI as sg


class View(sg.Column, metaclass=ABCMeta):
    """Base class for views."""

    def __init__(self, app, *args, **kwargs):
        super().__init__(visible=False, *args, **kwargs)
        self.__app = app

    @property
    def app(self):
        return self.__app

    def show(self):
        """Make the view visible."""

        super().update(visible=True)

    def hide(self):
        """Make the view invisible."""

        super().update(visible=False)

    @abstractmethod
    def handle_event(self, event: str, values: Dict):
        """Perform the appropiate logic in response to an event.

        Args:
            event (str): The event itself.
            values (Dict): This dict holds all the values of the views'
            components.
        """

        return
