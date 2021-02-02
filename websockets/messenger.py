"""
ZeroMQ sockets for interprocess communication.
"""

import atexit
import json
import logging
from typing import Dict, Tuple

import zmq

OPERATION_ADDR = "ipc:///tmp/operation"
MONITOR_ADDR = "ipc:///tmp/monitor"

SYNC = "ipc:///tmp/sync-websockets"


class Messenger:
    """This class handles communication between processes using ZeroMQ."""

    def __init__(self):
        self.ctx = zmq.Context()

        self.monitor_sub = self.ctx.socket(zmq.SUB)
        self.monitor_sub.connect(MONITOR_ADDR)
        self.monitor_sub.setsockopt_string(zmq.SUBSCRIBE, "reading")
        self.monitor_sub.setsockopt_string(zmq.SUBSCRIBE, "cycle")
        self.monitor_sub.setsockopt_string(zmq.SUBSCRIBE, "alarm")
        self.__sync_monitor()

        self.operation_sub = self.ctx.socket(zmq.SUB)
        self.operation_sub.connect(OPERATION_ADDR)
        self.operation_sub.setsockopt_string(zmq.SUBSCRIBE, "operation")
        self.__sync_operation()

        self.poller = zmq.Poller()
        self.poller.register(self.monitor_sub, zmq.POLLIN)
        self.poller.register(self.operation_sub, zmq.POLLIN)

        atexit.register(self.__cleanup)

    def __cleanup(self):
        """Clean things up before dumping."""

        self.monitor_sub.close()
        self.operation_sub.close()
        self.ctx.destroy()

        logging.info("Destroyed messenger")

    def __sync_monitor(self):
        """Synchronize with monitoring publisher."""

        self.monitor_sub.setsockopt_string(zmq.SUBSCRIBE, "sync")
        sync = self.ctx.socket(zmq.REQ)
        sync.connect(SYNC)

        while True:
            msg = self.monitor_sub.recv_string()
            if msg == "sync-websockets":
                sync.send_string("websockets")
                logging.info("Subscribed to monitoring messages")
                break

        self.monitor_sub.setsockopt_string(zmq.UNSUBSCRIBE, "sync")
        sync.close()

    def __sync_operation(self):
        """Synchronize with operation publisher."""

        self.operation_sub.setsockopt_string(zmq.SUBSCRIBE, "sync")
        sync = self.ctx.socket(zmq.REQ)
        sync.connect(SYNC)

        while True:
            msg = self.operation_sub.recv_string()
            if msg == "sync-websockets":
                sync.send_string("controls")
                logging.info("Subscribed to operation messages")
                break

        self.operation_sub.setsockopt_string(zmq.UNSUBSCRIBE, "sync")
        sync.close()

    def recv(self, block=True) -> Tuple[str, Dict]:
        """Receive a message from the other processes.

        Args:
            block (bool, optional): Whether or not this call should block.
                Defaults to True.

        Returns:
            Tuple[str, Dict]: The received message's topic and JSON-formatted
                content.
        """

        sockets = dict(self.poller.poll(timeout=0 if not block else None))
        if self.monitor_sub in sockets:
            [topic, body] = self.monitor_sub.recv_multipart()
        elif self.operation_sub in sockets:
            [topic, body] = self.operation_sub.recv_multipart()
        else:
            return [None, None]
        return [topic.decode(), json.loads(body)]
