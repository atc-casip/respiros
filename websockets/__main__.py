import logging

import zmq


MONITOR_ADDR = "ipc:///tmp/monitor"
MONITOR_SYNC_ADDR = "ipc:///tmp/sync-monitor"

OPERATION_ADDR = "ipc:///tmp/operation"
OPERATION_SYNC_ADDR = "ipc:///tmp/sync-operation"


class MessageManager(object):
    """
    This class handles communication between processes using ZeroMQ.
    """

    def __init__(self):
        self.ctx = zmq.Context()

        self.monitor = self.ctx.socket(zmq.SUB)
        self.monitor.connect(MONITOR_ADDR)
        self.__sync_monitor()

        self.operation = self.ctx.socket(zmq.SUB)
        self.operation.bind(OPERATION_ADDR)
        self.__sync_operation()

    def __sync_monitor(self):
        """
        Synchronize with operation publisher.
        """

        sync = self.ctx.socket(zmq.REQ)
        sync.connect(MONITOR_SYNC_ADDR)

        sync.send_string("websockets")
        sync.recv_string()
        logging.info("Subscribed to monitoring messages succesfully.")

        sync.close()

    def __sync_operation(self):
        """
        Synchronize with operation publisher.
        """

        sync = self.ctx.socket(zmq.REQ)
        sync.connect(OPERATION_SYNC_ADDR)

        sync.send_string("websockets")
        sync.recv_string()
        logging.info("Subscribed to operation messages succesfully.")

        sync.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    msg = MessageManager()
