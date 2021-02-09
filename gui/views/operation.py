"""
Main operation view.
"""

import logging
from typing import Dict, Optional

import zmq
from gui.components import ControlPane, MonitorBar, PlotCanvas
from gui.context import Context
from gui.messenger import Messenger

from .view import View

FIGURE_SECONDS = 20  # seconds
SAMPLE_PERIOD = 0.02  # samples
N_SAMPLES = FIGURE_SECONDS / SAMPLE_PERIOD


class OperationView(View):
    """
    This view allows the user to monitor and control the operation of the
    system.
    """

    __first = True

    timestamp_old = 0.0
    pressure_old = 0.0
    airflow_old = 0.0
    volume_old = 0.0
    nsamples = N_SAMPLES

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

        if self.__first:
            msg.send("request-reading", {})
            self.__first = False

        try:
            [topic, body] = msg.recv()
            if topic == "reading":
                self.__interpolate(ctx, body)
                self.canvas.update_plots(
                    ctx.pressure_data, ctx.airflow_data, ctx.volume_data
                )
                msg.send("request-reading", {})
            elif topic == "cycle":
                self.topbar.update_values(
                    ipap=body["ipap"],
                    epap=body["epap"],
                    freq=body["freq"],
                    vc_in=body["vc_in"],
                    vc_out=body["vc_out"],
                    oxygen=body["oxygen"],
                )
            elif topic == "alarm":
                logging.info("Received new alarm <%s>", body["type"])
                self.topbar.set_alarm(body["type"], body["criticality"])
        except zmq.Again:
            pass

        return resp

    def __interpolate(self, ctx: Context, reading: Dict):
        """Interpolate the given reading in the time series.

        Args:
            ctx (Context): Application context.
            reading (Dict): Values of the new reading.
        """

        pressure = float(reading["pressure"])
        airflow = float(reading["airflow"])
        volume = float(reading["volume"])
        timestamp = float(reading["timestamp"])

        period = timestamp - self.timestamp_old
        n_samples = int(period / SAMPLE_PERIOD)

        if len(ctx.pressure_data) == 0:
            self.timestamp_old = timestamp
            self.pressure_old = pressure
            self.airflow_old = airflow
            self.volume_old = volume

            ctx.pressure_data.append(pressure)
            ctx.airflow_data.append(airflow)
            ctx.volume_data.append(volume)
        elif n_samples >= 1:
            # Obtain the line equation
            m = (pressure - self.pressure_old) / period
            b = self.pressure_old
            h = 1

            m2 = (airflow - self.airflow_old) / period
            b2 = self.airflow_old

            m3 = (volume - self.volume_old) / period
            b3 = self.volume_old

            while n_samples > 0:
                if len(ctx.pressure_data) == self.nsamples:
                    ctx.pressure_data = ctx.pressure_data[1:]
                    ctx.airflow_data = ctx.airflow_data[1:]
                    ctx.volume_data = ctx.volume_data[1:]

                ctx.pressure_data.append(m * (SAMPLE_PERIOD * h) + b)
                ctx.airflow_data.append(m2 * (SAMPLE_PERIOD * h) + b2)
                ctx.volume_data.append(m3 * (SAMPLE_PERIOD * h) + b3)

                n_samples -= 1
                h += 1

            self.timestamp_old = timestamp
            self.pressure_old = pressure
            self.airflow_old = airflow
            self.volume_old = volume
