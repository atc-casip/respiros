"""
Main logic for running the application.
"""

import logging

import PySimpleGUI as sg

import gui.views as views

from .context import Context
from .sockets import Messenger


logging.basicConfig(filename="gui.log", filemode="w", level=logging.INFO)

msg = Messenger()
ctx = Context()

sg.theme("Reddit")

routes = {
    "/": views.ChecksView(),
    "/parameters": views.ParametersView(),
    "/operation": views.OperationView(),
}

window = sg.Window(
    "RespirOS",
    [list(routes.values())],
    size=(1366, 768),
    margins=(10, 10),
    finalize=True,
)

current_view = routes["/"]
current_view.set_up(ctx)
current_view.update(visible=True)
while True:
    event, values = window.read(timeout=10)
    resp = current_view.handle_event(event, values, ctx, msg)
    if resp is not None:
        next_view = routes[resp]
        next_view.set_up(ctx)
        current_view.update(visible=False)
        next_view.update(visible=True)
        current_view = next_view

        logging.info("Transitioned to view <%s>", type(current_view))

window.close()
