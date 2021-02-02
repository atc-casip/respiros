"""
Plots shown on the GUI.
"""

import tkinter
from typing import List

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotCanvas(sg.Canvas):
    """Custom canvas with three plots."""

    fig: plt.Figure
    graph: FigureCanvasTkAgg
    background: patches.Patch

    ax_pressure: plt.Axes
    ax_airflow: plt.Axes
    ax_volume: plt.Axes

    ln_pressure: plt.Line2D
    ln_airflow: plt.Line2D
    ln_volume: plt.Line2D

    def draw(self):
        """Draw the plots on the canvas."""

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
            # Create figure and subplots
            self.fig, [
                self.ax_pressure,
                self.ax_airflow,
                self.ax_volume,
            ] = plt.subplots(3, 1, constrained_layout=True)
            self.fig.set_figheight(6.5)
            self.fig.set_figwidth(8)

            # Configure pressure subplot
            self.ax_pressure.set_title("PRESION")
            self.ax_pressure.set_ylabel("cmH\N{SUBSCRIPT TWO}O")
            self.ax_pressure.set_xlim(0, 1000)
            self.ax_pressure.set_ylim(0, 21)
            self.ax_pressure.grid()
            self.ax_pressure.tick_params(
                axis="x",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
            )

            # Configure airflow subplot
            self.ax_airflow.set_title("FLUJO")
            self.ax_airflow.set_ylabel("l/min")
            self.ax_airflow.set_xlim(0, 1000)
            self.ax_airflow.set_ylim(-20, 20)
            self.ax_airflow.grid()
            self.ax_airflow.tick_params(
                axis="x",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
            )

            # Configure volume subplot
            self.ax_volume.set_title("VOLUMEN")
            self.ax_volume.set_ylabel("ml")
            self.ax_volume.set_xlim(0, 1000)
            self.ax_volume.set_ylim(-1, 15)
            self.ax_volume.grid()
            self.ax_volume.tick_params(
                axis="x",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
            )

            # Create GUI element
            self.graph = FigureCanvasTkAgg(self.fig, self.TKCanvas)
            self.graph.draw()
            self.graph.get_tk_widget().pack(
                side=tkinter.TOP, fill=tkinter.BOTH, expand=1
            )
            self.background = self.graph.copy_from_bbox(self.fig.bbox)

            # Create dynamic lines
            (self.ln_pressure,) = self.ax_pressure.plot(
                0, animated=True, color="violet"
            )
            (self.ln_airflow,) = self.ax_airflow.plot(
                0, animated=True, color="greenyellow"
            )
            (self.ln_volume,) = self.ax_volume.plot(
                0, animated=True, color="cyan"
            )

    def update_plots(
        self,
        pressure_data: List[float],
        airflow_data: List[float],
        volume_data: List[float],
    ):
        """Update the plots with new data.

        Args:
            pressure_data (List[float]): New data for the pressure plot.
            airflow_data (List[float]): New data for the airflow plot.
            volume_data (List[float]): New data for the volume plot.
        """

        # Update lines
        self.ln_pressure.set_xdata(range(len(pressure_data)))
        self.ln_pressure.set_ydata(pressure_data)

        self.ln_airflow.set_xdata(range(len(airflow_data)))
        self.ln_airflow.set_ydata(airflow_data)

        self.ln_volume.set_xdata(range(len(volume_data)))
        self.ln_volume.set_ydata(volume_data)

        # Redraw graph
        self.graph.restore_region(self.background)

        self.ax_pressure.draw_artist(self.ln_pressure)
        self.ax_airflow.draw_artist(self.ln_airflow)
        self.ax_volume.draw_artist(self.ln_volume)

        self.graph.blit(self.fig.bbox)
        self.graph.flush_events()
