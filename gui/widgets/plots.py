import tkinter
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import matplotlib.pyplot as plt
import PySimpleGUI as sg
from common.ipc import Topic
from gui.component import Component
from gui.ipc import ZMQEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FIGURE_SECONDS = 20  # seconds
SAMPLE_PERIOD = 0.02  # samples


class PlotCanvas(Component):
    """Custom canvas with three plots."""

    def __init__(self, app, size):
        super().__init__(app, pad=(0, 0))
        self.nsamples = FIGURE_SECONDS / SAMPLE_PERIOD
        self.timestamp_old = 0.0
        self.pressure_old = 0.0
        self.airflow_old = 0.0
        self.volume_old = 0.0

        self.canvas = sg.Canvas(size=size, pad=(0, 0))

        self.layout([[self.canvas]])

    def handle_event(self, event: str, values: Dict):
        if event == ZMQEvent.READING.name:
            self.__add_reading(values[event])
            self.app.ipc.send(Topic.REQUEST_READING, {})

    def show(self):
        with plt.rc_context(
            {
                "figure.facecolor": "black",
                "axes.facecolor": "black",
                "axes.edgecolor": "white",
                "axes.titlecolor": "white",
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
            }
        ):
            self.fig, self.axes = plt.subplots(3, 1, constrained_layout=True)
            self.fig.set_figheight(6.5)
            self.fig.set_figwidth(8)

            # Configure axes and create lines
            self.lines = []
            for ax, meta in zip(
                self.axes,
                [
                    ("PRESIÓN", "cmH\N{SUBSCRIPT TWO}O", (-2, 35), "violet"),
                    ("FLUJO", "l/min", (-40, 55), "greenyellow"),
                    ("VOLUMEN", "ml", (-2, 60), "cyan"),
                ],
            ):
                ax.set_title(meta[0])
                ax.set_ylabel(meta[1])
                ax.set_xlim(0, self.nsamples)
                ax.set_ylim(meta[2][0], meta[2][1])
                ax.grid()
                ax.tick_params(
                    axis="x",  # changes apply to the x-axis
                    which="both",  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False,  # no label on the bottom edge
                )

                (line,) = ax.plot(0, animated=True, color=meta[3])
                self.lines.append(line)

            # Create GUI element
            self.graph = FigureCanvasTkAgg(self.fig, self.canvas.TKCanvas)
            self.graph.draw()
            self.graph.get_tk_widget().pack(
                side=tkinter.TOP, fill=tkinter.BOTH, expand=1
            )
            self.background = self.graph.copy_from_bbox(self.fig.bbox)

    def __add_reading(self, reading: Dict):
        pressure = float(reading["pressure"])
        airflow = float(reading["airflow"])
        volume = float(reading["volume"])
        timestamp = float(reading["timestamp"])

        period = timestamp - self.timestamp_old
        nsamples = int(period / SAMPLE_PERIOD)

        # Clear graph area
        self.graph.restore_region(self.background)

        # Update lines' data concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            for ax, ln, value, value_old in zip(
                self.axes,
                self.lines,
                [pressure, airflow, volume],
                [self.pressure_old, self.airflow_old, self.volume_old],
            ):
                executor.submit(
                    self.__interpolate,
                    ax,
                    ln,
                    value,
                    value_old,
                    nsamples,
                    period,
                )

        # Draw new lines
        self.graph.blit(self.fig.bbox)
        self.graph.flush_events()

        # Update previous values
        self.pressure_old = pressure
        self.airflow_old = airflow
        self.volume_old = volume
        self.timestamp_old = timestamp

    def __interpolate(self, ax, ln, value, value_old, nsamples, period):
        data = ln.get_ydata()
        if len(data) == 1:
            data = data.tolist()
            data.append(value)
        elif nsamples >= 1:
            m = (value - value_old) / period
            b = value_old
            h = 1
            while nsamples > 0:
                if len(data) == self.nsamples:
                    data = data[1:]
                data.append(m * (SAMPLE_PERIOD * h) + b)
                nsamples -= 1
                h += 1
        ln.set_xdata(range(len(data)))
        ln.set_ydata(data)
        ax.draw_artist(ln)
