from typing import Dict

from common.ipc import Topic
from gui.component import Component
from gui.widgets.control import ControlPane
from gui.widgets.monitor import MonitorBar
from gui.widgets.plots import PlotCanvas


class OperationView(Component):
    """Main monitorization and control view."""

    def __init__(self, app):
        super().__init__(app, pad=(0, 0), visible=False, key="OperationView")
        self.__first = True

        self.monitor_bar = MonitorBar(app)
        self.control_pane = ControlPane(app)
        self.canvas = PlotCanvas(app, size=(650, 750))

        self.children = [self.monitor_bar, self.canvas, self.control_pane]
        self.layout([[self.monitor_bar], [self.canvas, self.control_pane]])

    def handle_event(self, event: str, values: Dict):
        # On first execution, request the first reading
        if self.__first:
            self.app.ipc.send(Topic.REQUEST_READING, {})
            self.__first = False

        super().handle_event(event, values)

    def show(self):
        self.expand(expand_x=True, expand_y=True)
        self.control_pane.show_tab(self.control_pane.parameters)
        super().show()
