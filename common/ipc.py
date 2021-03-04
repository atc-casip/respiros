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
