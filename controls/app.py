import logging
from flask.config import Config


class ControlApplication:
    """Main control process.

    Behaves like a state machine.
    """

    def __init__(self):
        self.config = Config({})

    def run(self):
        """Main loop of the application."""

        while True:
            self.current_state.run()

    def transition_to(self, state):
        """Change the current state of the application.

        Args:
            state: The state to transition to.
        """

        logging.info("Transitioning to state %s", state.__name__)
        self.current_state = self.states[state.__name__]
