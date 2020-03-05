import socket
import ast
import json
from player import Player
from Murderer import Murderer
import random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8192         # The port used by the server

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

rooms=[
'0','1','2','3','4','5','6'
]

class GameControl():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.map = None
        self.murderer = None
        self.conn = None
        self.players = [] # will be an array of all players 

    def start(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST,PORT))
        self.sock.listen()
        print("waiting for connection...")
        print('Listening for client...')
        self.conn, addr = self.sock.accept()
        print('Connection address:', addr)
        self.murderer = Murderer(CHARACTERS[random.randint(0,len(CHARACTERS)-1)], 
            rooms[random.randint(0,len(rooms)-1)],
            WEAPONS[random.randint(0,len(WEAPONS)-1)])
        print(self.murderer)
        self.start_game()

    def send(self, data):
        buf = json.dumps(data)
        print("sending : " + str(buf))
        self.conn.send(buf.encode())

    def recv(self):
        buf = self.conn.recv(2048)
        buf = buf.decode()
        return ast.literal_eval(buf)

    def process_move(self, rsp, player):
        print("doing move")
        # when more stuff is in place
        move_possible = 1 # temporary -- need to check if move is valid
        if move_possible:
            self.send_text('You moved!')
        else:
            self.send_text('Not a valid move, try another spot')

    def process_guess(self, rsp, player):
        if self.murderer.check_guess(rsp['character'], rsp['location'], rsp['weapon']):
            self.send_text('You win!')
        else:
            self.send_text('Nice try...')

    def start_game(self):
        move = {}
        move['command_type'] = 0
        move['text'] = 'Welcome! Select a player from the following list : \n' + ', '.join(CHARACTERS)+'\n'
        move['need_rsp'] = 1
        self.send(move)
        rsp = self.recv()
        self.players.append(Player(rsp['text'], 0))

    def send_text(self, text, need_rsp=0):
        move={}
        move['command_type'] = 0
        move['text'] = text
        move['need_rsp'] = need_rsp
        self.send(move)

    def game_play(self):
        while 1:
            for player in self.players:
                # get the players command
                self.send_text(str(player.character)+", it is your turn. Select one of the following: Move, Guess\n", 1)
                rsp = self.recv()
                if rsp['command_type'] == 1:
                    self.process_move(rsp, player)
                elif rsp['command_type'] == 2:
                    self.process_guess(rsp, player)


if __name__ == "__main__":
    s = GameControl(HOST, PORT)
    s.start()
    s.game_play()

