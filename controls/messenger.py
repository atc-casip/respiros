"""
Communication between processes using ZeroMQ.
"""

import atexit
import json
import logging
from typing import Dict, Tuple

import zmq

PUB_ADDR = "ipc:///tmp/monitor"
SUB_ADDR = "ipc:///tmp/operation"

SYNC_CONTROLS = "ipc:///tmp/sync-controls"
SYNC_GUI = "ipc:///tmp/sync-gui"
SYNC_WEBSOCKETS = "ipc:///tmp/sync-websockets"


class Messenger:
    """
    This class handles communication between processes using ZeroMQ.
    """

    def __init__(self):
        self.ctx = zmq.Context()

        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(PUB_ADDR)
        self.__sync_pub()

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(SUB_ADDR)
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "operation")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "change-alarms")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "request-reading")
        self.__sync_sub()

        atexit.register(self.__cleanup)

    def __cleanup(self):
        """
        Clean things up before dumping.
        """

        self.pub.close()
        self.sub.close()
        self.ctx.destroy()

        logging.info("Destroyed messenger")

    def __sync_pub(self):
        """
        Wait for the required subscribers.
        """

        sync_gui = self.ctx.socket(zmq.REP)
        sync_gui.bind(SYNC_GUI)

        while True:
            self.pub.send_string("sync-gui")
            try:
                sync_gui.recv(zmq.NOBLOCK)
                logging.info("GUI process subscribed")
                break
            except zmq.Again:
                continue

        sync_gui.close()

        sync_websockets = self.ctx.socket(zmq.REP)
        sync_websockets.bind(SYNC_WEBSOCKETS)

        while True:
            self.pub.send_string("sync-websockets")
            try:
                sync_websockets.recv(zmq.NOBLOCK)
                logging.info("WebSockets process subscribed")
                break
            except zmq.Again:
                continue

        sync_websockets.close()

    def __sync_sub(self):
        """
        Synchronize with operation publisher.
        """

        self.sub.setsockopt_string(zmq.SUBSCRIBE, "sync")
        sync = self.ctx.socket(zmq.REQ)
        sync.connect(SYNC_CONTROLS)

        while True:
            msg = self.sub.recv_string()
            if msg == "sync-controls":
                sync.send_string("controls")
                logging.info("Subscribed to operation messages")
                break

        self.sub.setsockopt_string(zmq.UNSUBSCRIBE, "sync")
        sync.close()

    def send(self, topic: str, body: Dict):
        """
        Send a message to the subscribers.
        """

        self.pub.send_multipart([topic.encode(), json.dumps(body).encode()])

    def recv(self, block=True) -> Tuple[str, Dict]:
        """
        Receive a message from the operation publisher.

        Returns both the topic and the contents in a tuple.
        """

        [topic, body] = self.sub.recv_multipart(
            zmq.NOBLOCK if not block else 0
        )
        return [topic.decode(), json.loads(body)]
