import logging
from typing import Dict

import gui.events as events
from gui.components import ControlPane, MonitorBar, PlotCanvas
from gui.context import ctx
from gui.messenger import msg

from .view import View

FIGURE_SECONDS = 20  # seconds
SAMPLE_PERIOD = 0.02  # samples
N_SAMPLES = FIGURE_SECONDS / SAMPLE_PERIOD


class OperationView(View):
    """Main monitorization and control view."""

    __first = True

    timestamp_old = 0.0
    pressure_old = 0.0
    airflow_old = 0.0
    volume_old = 0.0
    nsamples = N_SAMPLES

    def __init__(self, app):
        self.topbar = MonitorBar()
        self.canvas = PlotCanvas(size=(650, 750), key="canvas")
        self.control_pane = ControlPane()

        super().__init__(
            app,
            [[self.topbar], [self.canvas, self.control_pane]],
            pad=(0, 0),
        )

    def show(self):
        super().expand(expand_x=True, expand_y=True)
        self.topbar.expand()
        self.control_pane.expand()

        self.control_pane.parameters.ipap.value = ctx.ipap
        self.control_pane.parameters.epap.value = ctx.epap
        self.control_pane.parameters.freq.value = ctx.freq
        self.control_pane.parameters.trigger.value = ctx.trigger
        self.control_pane.parameters.ie.value = ctx.inhale, ctx.exhale

        self.canvas.draw()

        super().show()

    def handle_event(self, event: str, values: Dict):
        if self.__first:
            msg.send("request-reading", {})
            self.__first = False

        if event == events.ZMQ_READING:
            self.__interpolate(values[event])
            self.canvas.update_plots(
                ctx.pressure_data, ctx.airflow_data, ctx.volume_data
            )
            msg.send("request-reading", {})
        elif event == events.ZMQ_CYCLE:
            self.topbar.ipap.value = values[event]["ipap"]
            self.topbar.epap.value = values[event]["epap"]
            self.topbar.freq.value = values[event]["freq"]
            self.topbar.vc_in.value = values[event]["vc_in"]
            self.topbar.vc_out.value = values[event]["vc_out"]
            self.topbar.oxygen.value = values[event]["oxygen"]
        elif event == events.ZMQ_ALARM:
            logging.info(
                "Received alarm <%s> with criticality: %s",
                values[event]["type"],
                values[event]["criticality"],
            )

            if values[event]["type"] == "pressure_min":
                self.topbar.epap.show_alarm(values[event]["criticality"])
            elif values[event]["type"] == "pressure_max":
                self.topbar.ipap.show_alarm(values[event]["criticality"])
            elif values[event]["type"] == "volume_min":
                pass
            elif values[event]["type"] == "volume_max":
                pass
            elif values[event]["type"] in {"oxygen_min", "oxygen_max"}:
                self.topbar.oxygen.show_alarm(values[event]["criticality"])
            elif values[event]["type"] == "freq_max":
                self.topbar.freq.show_alarm(values[event]["criticality"])
        elif event == events.ZMQ_OPER_MODE:
            self.control_pane.mode_label.update(values[event]["mode"].upper())

        self.control_pane.handle_event(event, values)

    def __interpolate(self, reading: Dict):
        """Interpolate the given reading in the time series.

        Args:
            reading (Dict): The new values.
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
