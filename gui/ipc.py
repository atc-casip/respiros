import threading
from enum import Enum, auto

from common.ipc import IPCBuilder, Topic


class ZMQEvent(Enum):
    CHECK = auto()
    READING = auto()
    CYCLE = auto()
    ALARM = auto()
    OPER_MODE = auto()


class IPCDirector:
    """Director used for building the correct manager.

    Makes use of the manager builder.
    """

    def __init__(self, app=None):
        self.__builder = IPCBuilder()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.__builder.build_subscriber(
            app.config["ZMQ_MONITOR_ADDR"],
            [
                Topic.CHECK,
                Topic.READING,
                Topic.CYCLE,
                Topic.ALARM,
                Topic.OPERATION_MODE,
            ],
            app.config["ZMQ_SYNC_GUI_ADDR"],
        )
        self.__builder.build_publisher(
            app.config["ZMQ_OPERATION_ADDR"],
            [
                app.config["ZMQ_SYNC_CONTROLS_ADDR"],
                app.config["ZMQ_SYNC_API_ADDR"],
            ],
        )
        app.ipc = self.__builder.manager
        threading.Thread(
            target=self.__ipc_watchdog, args=[app], daemon=True
        ).start()

    def __ipc_watchdog(self, app):
        while True:
            topic, body = app.ipc.recv()
            if topic == Topic.CHECK:
                app.write_event_value(ZMQEvent.CHECK.name, body)
            elif topic == Topic.READING:
                app.write_event_value(ZMQEvent.READING.name, body)
            elif topic == Topic.CYCLE:
                app.write_event_value(ZMQEvent.CYCLE.name, body)
            elif topic == Topic.ALARM:
                app.write_event_value(ZMQEvent.ALARM.name, body)
            elif topic == Topic.OPERATION_MODE:
                app.write_event_value(ZMQEvent.OPER_MODE.name, body)


ipc = IPCDirector()
