"""Implements game and board state functionality."""

from time import sleep
from copy import deepcopy
import random
import logging

logger = logging.getLogger(__name__)

# TODO: finish fleshing out turn action logic
# TODO: keep a running turn_counter in here to supplement server2's turn counter.  However, make it so that advancing turn must be manually called by the server, unless triggered automatically.
# TODO: all class methods for actions or game logic must not rely on additional inputs than what is given at the start because there is not an easy way for game_state to make callbacks
# if additional input is required (ie, to check suggestion validity), then that must be split into multiple methods. So for example, if implementing suggestion requires an additional response from another player
# then that additional response must be in its own separate method that server2 must call by itself (alternatively, just implement callbacks)

class GameState:
    def __init__(self, rooms=None, weapons=None, suspects=None, hallways=None, secret_passages=None, starting_locs=None):
        # the Server object manages all incoming and outgoing messages between
        # player clients and the server
        # TODO: GameState will be controlled by GameServer, so after initializing all game attributes, drop references to Game Server and replace with class methods
        self.GameServer = GameServer
        
        # initialize game_board
        if not hallways:
            hallways = [('Billiard Room', 'Dining Room'), ('Study', 'Hall'),
                        ('Hall', 'Billiard Room'), ('Dining Room', 'Kitchen'),
                        ('Lounge', 'Dining Room'), ('Library', 'Conservatory'),
                        ('Billiard Room', 'Ballroom'), ('Ballroom', 'Kitchen'),
                        ('Study', 'Library'), ('Library', 'Billiard Room'),
                        ('Hall', 'Lounge'), ('Conservatory', 'Ballroom')]
        if not secret_passages:
            secret_passages = [('Study', 'Kitchen'), ('Lounge', 'Conservatory')]
        if not starting_locs:
            starting_locs = {'Miss Scarlet': ('Hall', 'Lounge'),
                             'Professor Plum': ('Study', 'Library'),
                             'Colonel Mustard': ('Lounge', 'Dining Room'),
                             'Mrs. Peacock': ('Library', 'Conservatory'),
                             'Mr. Green': ('Conservatory', 'Ballroom'),
                             'Mrs. White': ('Ballroom', 'Kitchen')}

        # shuffle decks
        if not rooms:
            rooms = ['Study', 'Hall', 'Lounge', 'Library', 'Billiard Room',
                     'Dining Room', 'Conservatory', 'Ballroom', 'Kitchen']
        if not weapons:
            weapons = ['Rope', 'Lead Pipe', 'Knife', 'Wrench', 'Candlestick',
                       'Revolver']
        if not suspects:
            suspects = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
                        'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
        random.shuffle(rooms)
        random.shuffle(weapons)
        random.shuffle(suspects)
        
        # Set game solution
        self.solution = {'room': rooms.pop(), 'weapon': weapons.pop(), 'suspect': suspects.pop()}

        # combine and shuffle deck
        cards = rooms+weapons+suspects
        random.shuffle(cards)

        # add solution cards back to reference lists
        rooms.append(self.solution['room'])
        weapons.append(self.solution['weapon'])
        suspects.append(self.solution['suspect'])
        
        # set game info as class attributes
        self.hallways = hallways
        self.secret_passages = secret_passages
        self.rooms = rooms
        self.starting_locs = starting_locs
        self.weapons = weapons
        self.suspects = suspects
        self.cards = cards

    def setup_game(connections):
        '''
        TODO: add docstring
        '''
        # initialize list of players, with their chosen characters
        self.player_list = [p[0] for p in connections]
        self.player_hands = {p:[] for p in self.player_list}

        # initialize game board
        self.game_board = GameBoard(rooms=self.rooms, hallways=self.hallways,
                                    secret_passages=self.secret_passages,
                                    players=self.player_list,
                                    starting_locs=self.starting_locs)

        # deal out cards to players
        while len(cards)>0:
            for player in self.player_list:
                try:
                    self.player_hands[player].append(cards.pop())
                except IndexError as e:
                    break
        
        # Randomize player turn order. Initial player is always Miss Scarlet,
        # if no Miss Scarlet, then use random first player
        self.player_order = deepcopy(self.player_list)
        random.shuffle(self.player_order)
        if 'Miss Scarlet' in self.player_order:
            self.current_character = 'Miss Scarlet'
            self.player_order.remove('Miss Scarlet')
            self.player_order.insert(0,'Miss Scarlet')

        self.turn_counter = 0

    def check_available_moves(character):
        loc = self.game_board.player_locs[character]
        possible_moves = self.game_board.nodes[loc]
        allowed_moves = []
        for move in possible_moves:
            if self.game_board.remaining_space[move]>0:
                allowed_moves.append(str(move))

        return allowed_moves

    def check_hand(player):
        hand_contents = '\n'.join(self.player_hands[player])

        return hand_contents

    def move_char(char,destination):
        loc = self.game_board.player_locs[character]
        destination = action_info['destination']
        if destination not in self.game_board.nodes[loc]:
            resp['status'] = 'Rejected'
            resp['message'] = 'You cannot reach that location from your current location'
        elif self.game_board.remaining_space[destination]==0:
            resp['status'] = 'Rejected'
            resp['message'] = 'That location has no room, you cannot move there'
        else:
            self.game_board.move_char(character,destination)

    def unpack_suggestion(char,weapon,suspect,room):
        loc = self.game_board.player_locs[character]
        if loc in self.hallways:
            resp['status'] = 'Invalid'
            resp['message'] = 'The murder did not occur in a hallway, so you cannot make a suggestion here'
            return resp

        weapon = action_info['weapon']
        suspect = action_info['suspect']
        cardlist = (weapon, suspect, loc)

        self.game_board.move_char(suspect, loc)

        return cardlist

    def formulate_suggestion_response(char,cardlist,responses):
        for responder, hand in self.player_hands.items():
            intersection = self._intersection(hand, cardlist)
            if len(intersection)==0:
                self.GameServer.broadcast({'recipients':responder,'message_type':'announcement','needs_acknowledgment':True,'message':responder+' does not have any cards which refute the suggestion of '+player})
            elif len(intersection)==1:
                refutation = intersection[0]
                self.GameServer.broadcast({'recipients':responder,'message_type':'announcement','needs_acknowledgment':True,'message':responder+' has the card '+refutation+' which refutes the suggestion of '+player})
            elif len(intersection)>=2:
                self.GameServer.broadcast({'recipients':responder,'message_type':'prompt_suggestion_response','message':'you have multiple cards which can refute the suggestion, pick one to show to '+player})

        message = 'Each player responded in the following way:\n'
        for player, r in sugg_resps:
            message = message+player+': '+r
        resp['message'] = message
        return resp

    def make_accusation(char,weapon,suspect,room):
        pass

    def rollover_turn(self):
        self.turn_counter += 1
        self.current_character = self.player_order[self.turn_counter % len(self.player_order)]
        self.current_player = self.player_order[self.turn_counter % len(self.player_order)]

    def _intersection(self, lst1, lst2):
        return list(set(lst1) & set(lst2))

class GameBoard:
    def __init__(self, rooms, hallways, secret_passages, players, starting_locs):
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
        self.player_locs = starting_locs
        for r  in self.player_locs.values():
            self.remaining_space[r]-=1
        print(self.remaining_space)
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
    
    def move_char(self, char,new_room):
        # at present presumes that validity of the move is already verified
        self.remaining_space[self.player_locs[char]]+=1
        self.player_locs[char] = new_room
        self.remaining_space[self.player_locs[char]]-=1