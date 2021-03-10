import gui.views as views


class ViewDirector:
    """Director used for initializing the app's views."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.views = {}
        for v in map(views.__dict__.get, views.__all__):
            app.views[v.__name__] = v(app)
        app.layout([list(app.views.values())]).finalize()
        app.current_view = app.views[views.LoadingView.__name__]


vd = ViewDirector()
