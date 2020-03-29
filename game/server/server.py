"""Defines server architecture."""
from itertools import cycle
from game_state import GameState
import sys
sys.path.append('../messages')
from messages import Message, MessageInterface, REGISTER, QUERY, START, TURN, MOVE, GUESS, ACCUSE
import socket
import struct
import asyncore
import json
HOST, PORT = "localhost", 9999
connections = []
player_list = {
    "nick": "Miss Scarlet",   # Dummy value
}
turn = b""
cycler = cycle(player_list)
ready = False
status = dict()
class Server(asyncore.dispatcher):
    def __init__(self, ip, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((ip, 4444))
        self.listen(10)

    def handle_accepted(self, connection, ip):
        global turn
        print(ip)
        connections.append(connection)
        data = connection.recv(4)
        (length,) = struct.unpack("!I", data)
        print(length)
        data = connection.recv(length).decode('utf8')
        data = json.loads(data)
        print(data)
        new_name = data["data"]
        print("Player {} connected".format(new_name))
        player_list[new_name] = "TEMP NAME WHATEVER THEY INPUT"
        if turn == b"":
            turn = new_name
        PlayerServer(connection)

    def get_player_list(self):
        return player_list

    def get_character(self, name):
        return player_list[name]

    def broadcast(self, new_status):    # for now just store a dict that is returned when queried. 
        global status
        status = new_status
    

class PlayerServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        global gs
        global turn
        global cycler
        global ready
        data = self.recv(4)
        (length,) = struct.unpack("!I", data)
        print(length)
        data = self.recv(length).decode('utf8')
        data = json.loads(data)
        print(data)
        if data["function"] == QUERY:
            print("query")   # inside this branch, we would check in the future whether the move is valid or not. 
            self.send(b'{"turn":"nick"}')  # instead of sending just whos turn it is here, send whole game state. 
            #self.send(status) # do this when logic exists
        elif data["function"] == START: 
            print("start")
            ready = True
            print(player_list)
            cycler = cycle(player_list)
        elif data["function"] == MOVE or  data["function"] == GUESS or  data["function"] == ACCUSE: 
            print("Turn was {}".format(data["function"]))
            print(data["data"])
            #gs.process_player_action("") # idk format yet
            turn = next(cycler)
        else: self.close()

if __name__ == "__main__":
    # Create the server, binding to localhost on port 4444
    try:
        Server(HOST, PORT)
        gs = GameState(Server)
        asyncore.loop()
    except KeyboardInterrupt:
        print("Caught exit!")