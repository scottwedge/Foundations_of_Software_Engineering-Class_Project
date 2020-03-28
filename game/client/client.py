"""
"""
import select
import socket
import sys
import time
import ast
from playerInterface import PlayerInterface
sys.path.append('../messages')
from messages import MessageInterface
from messages import Message

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
            sock.sendall(bytes(player_name, "utf-8"))
            sock.sendall(b"!")
            while sock:
                msg = sock.recv(1024)
                buf = msg.decode()
                # TODO two process_message functions - naming is off
                buf = MessageInterface.process_message(buf)
                rsp = self.player_interface.process_msg(buf)
                if rsp != None:
                    sock.sendall(bytes(rsp, "utf-8"))
                    print("Message sent!")
                print("Waiting for next message from server")

if __name__ == "__main__":
    client = Client()
    client.startup()