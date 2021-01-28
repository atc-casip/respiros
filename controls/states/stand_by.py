"""
Before starting operation, the system waits for the user to define the necessary parameters.
"""

import logging
from typing import Dict

from .events import Event, StartOperationControlled
from .operation import OperationControlled
from .state import State


class StandBy(State):
    """
    Waiting for the user to select an operation mode.
    """

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationControlled: OperationControlled}

    def run(self) -> Event:
        while True:
            [topic, msg] = self.ctx.messenger.recv()
            if topic == "operation":
                break

        logging.info("Starting operation in controlled mode")
        logging.info("IPAP -> %d", msg["ipap"])
        logging.info("EPAP -> %d", msg["epap"])
        logging.info("Frequency -> %d", msg["freq"])
        logging.info("Trigger -> %d", msg["trigger"])
        logging.info("I:E -> %d:%d", msg["inhale"], msg["exhale"])

        return StartOperationControlled(
            {
                "ipap": msg["ipap"],
                "epap": msg["epap"],
                "freq": msg["freq"],
                "inhale": msg["inhale"],
                "exhale": msg["exhale"],
                "trigger": msg["trigger"],
                "from_standby": True,
            }
        )
