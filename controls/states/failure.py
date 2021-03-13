from .state import State


class FailureState(State):
    """
    System failure.
    """

    def run(self):
        return super().run()
