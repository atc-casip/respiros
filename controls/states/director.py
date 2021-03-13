import controls.states as states


class StateDirector:
    """Director used for initializing the app's states."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.states = {}
        for s in map(states.__dict__.get, states.__all__):
            app.states[s.__name__] = s(app)
        app.current_state = app.states[states.SelfCheckState.__name__]


sd = StateDirector()
