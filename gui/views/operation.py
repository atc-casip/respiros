"""
Main operation view.
"""

from typing import Dict, Optional

import zmq
from gui.components import ControlPane, MonitorBar, PlotCanvas
from gui.context import Context
from gui.messenger import Messenger

from .view import View


class OperationView(View):
    """This view allows the user to monitor and control the operation of the system."""

    topbar: MonitorBar
    canvas: PlotCanvas
    menu: ControlPane

    def __init__(self):
        self.topbar = MonitorBar()
        self.canvas = PlotCanvas(size=(650, 750), key="canvas")
        self.menu = ControlPane()

        super().__init__(
            [[self.topbar], [self.canvas, self.menu]],
            pad=(0, 0),
        )

    def set_up(self, ctx: Context):
        super().expand(expand_x=True, expand_y=True)
        self.topbar.expand()
        self.menu.expand()

        self.menu.parameters.update_values(
            ipap=ctx.ipap,
            epap=ctx.epap,
            freq=ctx.freq,
            trigger=ctx.trigger,
            inhale=ctx.inhale,
            exhale=ctx.exhale,
        )

        self.canvas.draw()

    def handle_event(
        self, event: str, values: Dict, ctx: Context, msg: Messenger
    ) -> Optional[str]:
        resp = self.menu.handle_event(event, values, ctx, msg)

        msg.send("request-reading", {})
        try:
            [topic, msg] = msg.recv(block=False)
            if topic == "reading":
                if len(ctx.pressure_data) == 1000:
                    ctx.pressure_data = ctx.pressure_data[1:]
                    ctx.airflow_data = ctx.airflow_data[1:]
                    ctx.volume_data = ctx.volume_data[1:]

                ctx.pressure_data.append(msg["pressure"])
                ctx.airflow_data.append(msg["airflow"])
                ctx.volume_data.append(msg["volume"])

                self.canvas.update_plots(
                    ctx.pressure_data, ctx.airflow_data, ctx.volume_data
                )
        except zmq.Again:
            pass

        return resp
