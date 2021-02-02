"""
ZeroMQ sockets for interprocess communication.
"""

import atexit
import json
import logging
from typing import Dict, Tuple

import zmq

PUB_ADDR = "ipc:///tmp/operation"
SUB_ADDR = "ipc:///tmp/monitor"

SYNC_CONTROLS = "ipc:///tmp/sync-controls"
SYNC_GUI = "ipc:///tmp/sync-gui"
SYNC_WEBSOCKETS = "ipc:///tmp/sync-websockets"


class Messenger:
    """This class handles communication between processes using ZeroMQ."""

    def __init__(self):
        self.ctx = zmq.Context()

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(SUB_ADDR)
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "check")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "reading")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "cycle")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "alarm")
        self.__sync_sub()

        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(PUB_ADDR)
        self.__sync_pub()

        atexit.register(self.__cleanup)

    def __cleanup(self):
        """Clean things up before dumping."""

        self.pub.close()
        self.sub.close()
        self.ctx.destroy()

        logging.info("Destroyed messenger")

    def __sync_pub(self):
        """Wait for the required subscribers."""

        sync_controls = self.ctx.socket(zmq.REP)
        sync_controls.bind(SYNC_CONTROLS)

        while True:
            self.pub.send_string("sync-controls")
            try:
                sync_controls.recv(zmq.NOBLOCK)
                logging.info("Control system process subscribed")
                break
            except zmq.Again:
                continue

        sync_controls.close()

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

        """
        poller = zmq.Poller()
        poller.register(sync_controls, zmq.POLLIN)
        poller.register(sync_websockets, zmq.POLLIN)

        subscribers = []
        while len(subscribers) < 2:
            self.pub.send_string("sync")

            try:
                sockets = dict(poller.poll(timeout=0))
            except KeyboardInterrupt:
                break

            if sync_controls in sockets and sync_controls not in subscribers:
                subscribers.append(sync_controls)
                logging.info("Control system process subscribed")

            if sync_websockets in sockets and sync_websockets not in subscribers:
                subscribers.append(sync_websockets)
                logging.info("WebSockets process subscribed")

        sync_controls.close()
        sync_websockets.close()
        """

    def __sync_sub(self):
        """Synchronize with monitoring publisher."""

        self.sub.setsockopt_string(zmq.SUBSCRIBE, "sync")
        sync = self.ctx.socket(zmq.REQ)
        sync.connect(SYNC_GUI)

        while True:
            msg = self.sub.recv_string()
            if msg == "sync-gui":
                sync.send_string("gui")
                logging.info("Subscribed to monitoring messages")
                break

        self.sub.setsockopt_string(zmq.UNSUBSCRIBE, "sync")
        sync.close()

    def send(self, topic: str, body: Dict):
        """Send a message to the other processes.

        Args:
            topic (str): The topic for the message.
            body (Dict): Message's content in JSON format.
        """

        self.pub.send_multipart([topic.encode(), json.dumps(body).encode()])

    def recv(self, block=True) -> Tuple[str, Dict]:
        """Receive a message from the other processes.

        Args:
            block (bool, optional): Whether or not this call should block. Defaults to True.

        Returns:
            Tuple[str, Dict]: The received message's topic and JSON-formatted content.
        """

        [topic, body] = self.sub.recv_multipart(zmq.NOBLOCK if not block else 0)
        return [topic.decode(), json.loads(body)]
