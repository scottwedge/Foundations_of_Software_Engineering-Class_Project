from server import *
from client import *
from game_state import *
from player_interface import *

if __name__ == '__main__':
    GameServer = Server()
    current_game = GameState(GameServer)
    
    while True:
        new_messages = GameServer.check_messages()
        for message in new_messages:
            move_type = literal_eval(message):
                