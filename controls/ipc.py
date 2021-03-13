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
        self.__builder.build_publisher(
            app.config["ZMQ_MONITOR_ADDR"],
            [app.config["ZMQ_SYNC_GUI_ADDR"], app.config["ZMQ_SYNC_API_ADDR"]],
        )
        self.__builder.build_subscriber(
            app.config["ZMQ_OPERATION_ADDR"],
            [
                Topic.OPERATION_PARAMS,
                Topic.OPERATION_ALARMS,
                Topic.REQUEST_READING,
            ],
            app.config["ZMQ_SYNC_CONTROLS_ADDR"],
        )
        app.ipc = self.__builder.manager


ipc = IPCDirector()
