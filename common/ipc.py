import atexit
import json
import logging
from enum import Enum, auto
from typing import Dict, Set, Tuple

import zmq


class Topic(Enum):
    SYNC = auto()
    CHECK = auto()
    OPERATION_MODE = auto()
    OPERATION_PARAMS = auto()
    OPERATION_ALARMS = auto()
    ALARM = auto()
    SILENCE_ALARMS = auto()
    REQUEST_READING = auto()
    READING = auto()
    CYCLE = auto()


class PublisherError(Exception):
    pass


class Publisher:
    def __init__(self, ctx: zmq.Context, addr: str, subscribers: Set[str]):
        self.__ctx = ctx
        self.__socket = ctx.socket(zmq.PUB)
        atexit.register(self.__socket.close)
        self.__socket.bind(addr)
        self.__sync(subscribers)

    def __sync(self, subscribers: Set[str]):
        sync_socket = self.__ctx.socket(zmq.REP)
        for sub in subscribers:
            sync_socket.bind(sub)
            while True:
                self.__socket.send_string(Topic.SYNC.name)
                try:
                    resp = sync_socket.recv_string(zmq.NOBLOCK)
                    sync_socket.send_string(Topic.SYNC.name)
                    logging.info("Process <%s> subscribed", resp)
                    break
                except zmq.Again:
                    continue
        sync_socket.close()

    def send(self, topic: Topic, body: Dict):
        self.__socket.send_multipart(
            [topic.name.encode(), json.dumps(body).encode()]
        )


class Subscriber:
    def __init__(
        self, ctx: zmq.Context, addr: str, topics: Set[Topic], sync_addr: str
    ):
        self.__ctx = ctx
        self.__socket = ctx.socket(zmq.SUB)
        atexit.register(self.__socket.close)
        self.__socket.connect(addr)
        self.__sync(sync_addr)

        for t in topics:
            self.__socket.setsockopt_string(zmq.SUBSCRIBE, t.name)

    def __sync(self, addr: str):
        self.__socket.setsockopt_string(zmq.SUBSCRIBE, Topic.SYNC.name)
        sync = self.__ctx.socket(zmq.REQ)
        sync.connect(addr)
        while True:
            msg = self.__socket.recv_string()
            if msg == Topic.SYNC.name:
                try:
                    sync.send_string("test")
                    sync.recv_string()
                    break
                except zmq.Again:
                    continue
        sync.close()
        self.__socket.setsockopt_string(zmq.UNSUBSCRIBE, Topic.SYNC.name)

    def recv(self, block=True) -> Tuple[Topic, Dict]:
        try:
            topic, body = self.__socket.recv_multipart(
                zmq.NOBLOCK if not block else 0
            )
            return Topic[topic.decode()], json.loads(body)
        except zmq.Again:
            return None, None


class IPCManager:
    def __init__(self):
        self.pub = None
        self.subs = []
        self.poller = None

    def send(self, topic: Topic, body: Dict):
        self.pub.send_multipart(
            [topic.name.encode(), json.dumps(body).encode()]
        )

    def recv(self, block=True) -> Tuple[Topic, Dict]:
        if not self.subs:
            return None, None
        elif not self.poller:
            sub = self.subs[0]
        else:
            sockets = dict(self.poller.poll(timeout=0 if not block else None))
            for s in self.subs:
                if s in sockets:
                    sub = s
                    break

        try:
            topic, body = sub.recv_multipart(zmq.NOBLOCK if not block else 0)
            return Topic[topic.decode()], json.loads(body)
        except Exception:
            return None, None


class IPCBuilder:
    def __init__(self):
        self.__ctx = zmq.Context()
        self.__ipc = IPCManager()

    @property
    def manager(self):
        product = self.__ipc
        self.__ipc = IPCManager()
        return product

    def build_publisher(self, addr: str, subscribers: Set[str]):
        if self.__ipc.pub:
            raise PublisherError()

        pub = self.__ctx.socket(zmq.PUB)
        pub.bind(addr)

        # Sync with subscribers
        sync_socket = self.__ctx.socket(zmq.REP)
        for sync_addr in subscribers:
            sync_socket.bind(sync_addr)
            while True:
                pub.send_string(Topic.SYNC.name)
                try:
                    sync_socket.recv_string(zmq.NOBLOCK)
                    sync_socket.send_string(Topic.SYNC.name)
                    break
                except zmq.Again:
                    continue
        logging.info("Succesfully synced publisher on %s", addr)
        sync_socket.close()

        self.__ipc.pub = pub

    def build_subscriber(self, addr: str, topics: Set[Topic], sync_addr: str):
        logging.info("Building subscriber on %s", addr)
        sub = self.__ctx.socket(zmq.SUB)
        sub.connect(addr)

        # Sync with publisher
        sub.setsockopt_string(zmq.SUBSCRIBE, Topic.SYNC.name)
        sync = self.__ctx.socket(zmq.REQ)
        sync.connect(sync_addr)
        while True:
            msg = sub.recv_string()
            if msg == Topic.SYNC.name:
                logging.info("%s received sync msg", addr)
                try:
                    sync.send_string(Topic.SYNC.name)
                    sync.recv_string()
                    break
                except zmq.Again:
                    continue
        logging.info("Successfully synced subscriber on %s", addr)
        sync.close()
        sub.setsockopt_string(zmq.UNSUBSCRIBE, Topic.SYNC.name)

        for t in topics:
            sub.setsockopt_string(zmq.SUBSCRIBE, t.name)

        self.__ipc.subs.append(sub)

        # Create poller if there is more than one subscriber
        if len(self.__ipc.subs) > 1:
            self.__ipc.poller = zmq.Poller()
            for sub in self.__ipc.subs:
                self.__ipc.poller.register(sub, zmq.POLLIN)
