import logging

import gevent
from common.ipc import IPCBuilder, Topic


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
            [Topic.READING, Topic.CYCLE, Topic.ALARM],
            app.config["ZMQ_SYNC_API_ADDR"],
        )
        self.__builder.build_subscriber(
            app.config["ZMQ_OPERATION_ADDR"],
            [Topic.OPERATION_PARAMS],
            app.config["ZMQ_SYNC_API_ADDR"],
        )
        app.ipc = self.__builder.manager
        app.extensions["socketio"].start_background_task(
            self.__ipc_watchdog, app
        )

    def __ipc_watchdog(self, app):
        while True:
            topic, body = app.ipc.recv(block=False)
            if topic == Topic.OPERATION_PARAMS:
                logging.info("emitting params")
                app.extensions["socketio"].emit(
                    "parameters",
                    {
                        "mode": "VPS",
                        "ipap": body["ipap"],
                        "epap": body["epap"],
                        "breathing_freq": body["freq"],
                        "trigger": body["trigger"],
                        "ie_relation": f"{body['inhale']}:{body['exhale']}",
                    },
                )
            elif topic == Topic.READING:
                app.extensions["socketio"].emit(
                    "readings",
                    {
                        "pressure": body["pressure"],
                        "flow": body["airflow"],
                        "volume": body["volume"],
                        "timestamp": body["timestamp"],
                    },
                )
            elif topic == Topic.CYCLE:
                # TODO: Send cycle event.
                pass
            elif topic == Topic.ALARM:
                # TODO: Send alarm event.
                pass

            gevent.sleep(0.1)


ipc = IPCDirector()
