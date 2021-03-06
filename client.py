"""Implements PlayerInterface functionality and provides startup sequence."""

import socket
import struct
import logging
import sys

from game.client.player_interface import PlayerInterface
from game.messages.messages import MessageInterface, REGISTER, QUERY, START

logger = logging.getLogger(__name__)


class Client:
    def __init__(self):
        # TODO make host and port be parameters
        self.HOST, self.PORT = "localhost", 4444
        self.player_interface = None

    def startup(self):
        player_name = input("Enter the name other players should see you as!\n")
        self.player_interface = PlayerInterface(str(player_name))               
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send player name
            sock.connect((self.HOST, self.PORT))
            register_msg = MessageInterface.create_message(REGISTER, player_name)
            print(register_msg)
            sock.sendall(struct.pack("!I", len(bytes(register_msg, "utf-8"))))
            sock.sendall(bytes(register_msg, "utf-8"))
            ready = False
            while not ready:
                i = input("When you are ready, type 'ready': ")
                if i.lower()=='ready':
                    ready = True
            while sock:
                query_msg = MessageInterface.create_message(QUERY, "")
                print(query_msg)
                sock.sendall(struct.pack("!I", len(bytes(query_msg, "utf-8"))))
                sock.sendall(bytes(query_msg, "utf-8"))
                msg = sock.recv(1024)
                buf = msg.decode()
                print(buf)
                # TODO two process_message functions - naming is off
                buf = MessageInterface.process_message(buf, query=True)
                rsp = self.player_interface.process_msg(buf, query=True)
                print(rsp)
                if rsp != None:
                    sock.sendall(struct.pack("!I", len(bytes(rsp, "utf-8"))))
                    sock.sendall(bytes(rsp, "utf-8"))
                    print("Message sent!")
                print("Waiting for next message from server")

if __name__ == "__main__":

    # Set optional verbose debugging level
    logger.setLevel(logging.CRITICAL)
    if len(sys.argv) > 1 and sys.argv[1] == "-V":
        logger.setLevel(logging.DEBUG)

    client = Client()
    client.startup()