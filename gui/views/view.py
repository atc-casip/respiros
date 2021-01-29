"""
Define base view class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import PySimpleGUI as sg
from gui.context import Context
from gui.messenger import Messenger


class View(sg.Column, ABC):
    """
    Base class for views.
    """

    def __init__(self, layout: List[List[sg.Element]], pad=None):
        super().__init__(layout, pad=pad, visible=False)

    @abstractmethod
    def set_up(self, ctx: Context):
        """Prepare the view before actually using it.

        Usually, this involves expanding elements or updating the initial values with the ones
        provided by the context.

        Args:
            ctx (Context): Application context.
        """

    @abstractmethod
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
