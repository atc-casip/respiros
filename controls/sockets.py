"""
Communication between processes using ZeroMQ.
"""

import atexit
import json
import logging
from typing import Dict, Tuple

import zmq

PUB_ADDR = "ipc:///tmp/monitor"
PUB_SYNC_ADDR = "ipc:///tmp/sync-monitor"

SUB_ADDR = "ipc:///tmp/operation"
SUB_SYNC_ADDR = "ipc:///tmp/sync-operation"


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

        sync = self.ctx.socket(zmq.REP)
        sync.bind(PUB_SYNC_ADDR)

        subs = 0
        while subs < 2:
            msg = sync.recv_string()
            if msg is not None:
                subs += 1
                sync.send_string("ok")
                logging.info("Process <%s> subscribed", msg)

        sync.close()

    def __sync_sub(self):
        """
        Synchronize with operation publisher.
        """

        sync = self.ctx.socket(zmq.REQ)
        sync.connect(SUB_SYNC_ADDR)

        sync.send_string("controls")
        sync.recv_string()
        logging.info("Subscribed to operation messages")

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

        [topic, body] = self.sub.recv_multipart(zmq.NOBLOCK if not block else 0)
        return [topic.decode(), json.loads(body)]
