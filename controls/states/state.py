from abc import ABCMeta, abstractmethod


class State(metaclass=ABCMeta):
    """
    Base state class.
    """

    def __init__(self, app):
        self.app = app

    @abstractmethod
    def run(self):
        """Execute the state's logic.

        This method can return when a transition to another state needs to be
        made.
        """

        return
