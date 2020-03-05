import socket
import json
import ast
from player import Player
from command import *

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8192         # The port used by the server

rooms=[
'0','1','2','3','4','5','6'
]

# where will we store this data
CHARACTERS = [
'Mrs. White',
'Professor Plum',
'Col Mustard',
'Mr. Green',
'Mrs. Peacock',
'Miss Scarlet'
]

WEAPONS = [
'Candlestick', 
'Revolver', 
'Knife', 
'Lead Pipe', 
'Rope', 
'Wrench'
]

class Client():
    def __init__(self, host, port):
        self.host = HOST
        self.port = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = None

    def connect_sock(self):
        self.sock.connect((self.host, self.port))
        self.game_play()

    def send_message(self, data):
        temp = json.dumps(data, default=lambda o: o.__dict__)
        self.sock.sendall(temp.encode())

    def recv(self):
        data = self.sock.recv(1024)
        buf = data.decode()
        return ast.literal_eval(buf)

    def process_text(self,command):
        print("got text")
        rsp = {}
        if command['need_rsp'] == 0:
            print(command['text'])
        else:
            print("here?")
            answer = input(command['text'])
        if ('turn' in command['text']):
            if 'move' in answer.lower():
                rsp['command_type'] = 1
                rsp['move_location'] = input('select a rooom: \n' + (str(rooms)))

            elif 'guess' in answer.lower():
                rsp['command_type'] = 2
                rsp['character'] = input('Who?\n %s\n' % (', '.join(CHARACTERS)))
                rsp['location'] = input("Where?\n %s\n" % (str(rooms)))

                rsp['weapon'] = input("How??\n %s\n" % (', '.join(WEAPONS)))
            else:
                'not a valid option'
        else:
            rsp['command_type'] = 0
            rsp['text'] = answer
        return rsp

    def game_play(self):
        print("game play")
        while 1:
            command = self.recv()
            action = int(command['command_type'])
            print("got message from server")
            if action == 0:
                rsp = self.process_text(command)
            else:
                print("not processing yet")
                break
            print('sending back')
            self.send_message(rsp)

#c = Client(HOST, PORT)

if __name__ == "__main__":
    c = Client(HOST, PORT)
    #g = Guess('candlestick', 'ballroom')
    #c.player = Player('violet')
    c.connect_sock()

