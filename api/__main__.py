from gevent.pywsgi import WSGIServer

from api import create_app

app = create_app()
WSGIServer(("", app.config["PORT"]), app).serve_forever()
