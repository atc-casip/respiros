"""
Definition of the state machine and base state class for the control system.
"""

from abc import ABC, abstractmethod
from typing import Dict

from controls.context import Context

from .events import Event


class State(ABC):
    """
    Base state class.
    """

    def __init__(self, ctx: Context):
        self.ctx = ctx

    @abstractmethod
    def transitions(self) -> Dict:
        """
        Generate transition map for the state.
        """

        return

    @abstractmethod
    def run(self) -> Event:
        """
        Execute the state's logic and return the event for the next transition.
        """

        return

    def next(self, event: Event):
        """
        Based on the given event, determine the next state.
        """

        transitions = self.transitions()
        if type(event) in transitions:
            if event.payload:
                return transitions[type(event)](self.ctx, event.payload)
            return transitions[type(event)](self.ctx)
        raise "Event not supported for current state"
