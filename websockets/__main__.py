import logging

from .sockets import Messenger


logging.basicConfig(filename="websockets.log", filemode="w", level=logging.INFO)

messenger = Messenger()

while True:
    [topic, msg] = messenger.recv()
    logging.info("Message received <%s>", topic)
