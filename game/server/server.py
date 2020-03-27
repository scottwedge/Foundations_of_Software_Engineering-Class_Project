"""Defines server architecture."""
from itertools import cycle
import socket
import asyncore
HOST, PORT = "localhost", 9999
connections = []
player_list = []
turn = b""
cycler = cycle(player_list)
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

class PlayerServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        global turn
        global cycler
        data = self.recv(1)
        if data == b"?":
            print("query")   # inside this branch, we would check in the future whether the move is valid or not. 
            self.send(turn)
        elif data == b"!": 
            print("start")
            print(player_list)
            cycler = cycle(player_list)
        elif data == b"T":
            print("turn")
            self.recv(5)
            self.send(bytes("V", "utf-8"))
            turn = next(cycler)
        else: self.close()

if __name__ == "__main__":
    # Create the server, binding to localhost on port 9999
    try:
        Server(HOST, PORT)
        asyncore.loop()
    except KeyboardInterrupt:
        print("Caught exit!")