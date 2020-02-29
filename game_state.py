from server import *
from client import *
from player_interface import *
from time import sleep
import random

class GameState:
    def __init__(GameServer):
        # the Server object manages all incoming and outgoing messages between
        # player clients and the server
        self.GameServer = GameServer

        while not GameServer.all_ready():
            # Server object all_ready method checks if enough players are
            # connected and that they have all marked themselves ready to start
            sleep(15)

        # initialize list of players, with their chosen characters
        self.player_list = random.shuffle(GameServer.get_player_list())
        self.player_chars = {player:GameServer.getChar(player) for player in player_list}
        self.char_players = {v:k for k, v in player_chars.items()}
        self.player_hands = {p:[] for p in player_list}

        # shuffle decks
        rooms = ['Study', 'Hall', 'Lounge', 'Library', 'Billiard Room',
                 'Dining Room', 'Conservatory', 'Ballroom', 'Kitchen']
        weapons = ['Rope', 'Lead Pipe', 'Knife', 'Wrench', 'Candlestick', 'Revolver']
        suspects = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
                    'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
        random.shuffle(rooms)
        random.shuffle(weapons)
        random.shuffle(suspects)

        # initialize game_board
        hallways = [('Billiard Room', 'Dining Room'), ('Study', 'Hall'),
                    ('Hall', 'Billiard Room'), ('Dining Room', 'Kitchen'),
                    ('Lounge', 'Dining Room'), ('Library', 'Conservatory'),
                    ('Billiard Room', 'Ballroom'), ('Ballroom', 'Kitchen'),
                    ('Study', 'Library'), ('Library', 'Billiard Room'),
                    ('Hall', 'Lounge'), ('Conservatory', 'Ballroom')]
        secret_passages = [('Study', 'Kitchen'), ('Lounge', 'Conservatory')]
        self.game_board = GameBoard(rooms=rooms, hallways=hallways,
                                    secret_passages=secret_passages,
                                    players=self.player_list,
                                    player_chars=self.player_chars,
                                    char_players=self.char_players)
        
        # Set Game Solution
        self.solution = {'room': rooms.pop(), 'weapon': weapons.pop(), 'suspect': suspects.pop()}

        # deal out cards to players
        cards = rooms+weapons+suspects
        random.shuffle(cards)
        while len(cards)>0:
            for player in self.player_list:
                try:
                    self.player_hands[player].append(cards.pop())
                except IndexError as e:
                    break
        
        # initial player is always Miss Scarlet
        self.current_player = 'Miss Scarlet'
        self.turn_counter = 1
    
    def process_player_move(move_type, move_info):
        if move_type=='checkAvailableMoves':
            pass
        elif move_type=='checkHand':
            pass
        elif move_type=='makeSuggestion':
            pass
        elif move_type=='makeAccusation':
            pass
        elif move_type=='moveChar':
            pass

class GameBoard:
    def __init__(rooms, hallways, secret_passages, players, player_chars):
        # GameBoard class is basically a Graph class that's already implemented
        # pretty well in networkx library. TBD whether it would be better to
        # use that library or this instead.  Most of the verbiage below
        # replicates graph metadata management that networkx already does, and
        # can be replaced as such unless there is a strong preference for only
        # using Python Standard Library code.
        self.edges = []
        self.nodes = {r:[] for r in rooms+hallways}
        self.remaining_space = {r:1 for r in hallways}
        self.remaining_space.update({r:6 for r in rooms})
        self.player_locs = {'Miss Scarlet': ('Hall', 'Lounge'),
                            'Professor Plum': ('Study', 'Library'),
                            'Colonel Mustard': ('Lounge', 'Dining Room'),
                            'Mrs. Peacock': ('Library', 'Conservatory'),
                            'Mr. Green': ('Conservatory', 'Ballroom'),
                            'Mrs. White': ('Ballroom', 'Kitchen')}
        for p,r in self.player_locs:
            self.remaining_space[r]-=1

        for hallway in hallways:
            self.edges.append((hallway[0],hallway))
            self.nodes[hallway[0]].append(hallway)
            self.nodes[hallway].append(hallway[0])
            
            self.edges.append((hallway[1],hallway))
            self.nodes[hallway[1]].append(hallway)
            self.nodes[hallway].append(hallway[1])
            
            self.edges.extend(secret_passages)
            for sp in secret_passages:
                self.nodes[sp[0]].append(sp[1])
                self.nodes[sp[1]].append(sp[0])
    
    def move_char(char,new_room):
        # at present presumes that validity of the move is already verified
        self.remaining_space[self.player_locs[char]]+=1
        self.player_locs[char] = new_room
        self.remaining_space[self.player_locs[char]]-=1