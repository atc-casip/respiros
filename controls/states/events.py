"""
Events that trigger state transitions.
"""

from typing import Dict


class Event:
    """
    Base event class. All events have a payload that may contain important
    values or be `None`.
    """

    def __init__(self, payload: Dict):
        self.payload = payload


class ChecksSuccessful(Event):
    """
    This event triggers when all component checks are succesful.
    """


class ChecksUnsuccessful(Event):
    """
    This event triggers when any component check fails.
    """


class StartOperationControlled(Event):
    """
    This event triggers when the user inputs the starting operation parameters.

    The payload contains the parameters that must be used for operation.
    """


class StartOperationAssisted(Event):
    """
    This event triggers when the operation goes from controlled to assisted.

    The payload contains the parameters that must be used for operation.
    """
