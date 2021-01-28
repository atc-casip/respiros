from typing import Dict

from .events import Event
from .state import State


class Failure(State):
    """
    System failure.
    """

    def transitions(self) -> Dict[Event, State]:
        return {}

    def run(self) -> Event:
        # TODO: Define what to do on failure

        while True:
            pass
