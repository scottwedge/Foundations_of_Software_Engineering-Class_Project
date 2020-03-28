"""Defines server architecture."""
from itertools import cycle
from game_state import GameState
import socket
import asyncore
HOST, PORT = "localhost", 9999
connections = []
player_list = []
turn = b""
cycler = cycle(player_list)
ready = False
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
        new_name = connection.recv(4) # todo change to be length of name
        print("Player {} connected".format(new_name))
        player_list.append(new_name)
        if turn == b"":
            turn = new_name
        PlayerServer(connection)

    def get_player_list(self):
        return player_list

    def get_character(self, name):
        return player_list["name"]

class PlayerServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        global turn
        global cycler
        global ready
        data = self.recv(1)
        if data == b"?":
            print("query")   # inside this branch, we would check in the future whether the move is valid or not. 
            self.send(turn)  # instead of sending just whos turn it is here, send whole game state. 
        elif data == b"!": 
            print("start")
            ready = True
            print(player_list)
            cycler = cycle(player_list)
        elif data == b"T":
            print("turn")
            self.recv(5)
            self.send(bytes("V", "utf-8"))
            turn = next(cycler)
        else: self.close()

if __name__ == "__main__":
    # Create the server, binding to localhost on port 4444
    try:
        Server(HOST, PORT)
        GameState(Server)
        asyncore.loop()
    except KeyboardInterrupt:
        print("Caught exit!")