from server import *
from client import *
from time import sleep
import random

class GameState:
    def __init__(self, GameServer):
        # the Server object manages all incoming and outgoing messages between
        # player clients and the server
        self.GameServer = GameServer

        while not self.GameServer.all_ready():
            # Server object all_ready method checks if enough players are
            # connected and that they have all marked themselves ready to start
            sleep(15)

        # initialize list of players, with their chosen characters
        self.player_list = self.GameServer.get_player_list()
        random.shuffle(self.player_list)
        self.player_chars = {player:self.GameServer.getChar(player) for player in self.player_list}
        self.char_players = {v:k for k, v in self.player_chars.items()}
        self.player_hands = {p:[] for p in self.player_list}

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
        
        # add solution cards back to reference lists
        rooms.append(self.solution['room'])
        weapons.append(self.solution['weapon'])
        suspects.append(self.solution['suspect'])
        self.rooms = rooms
        self.hallways = hallways
        self.weapons = weapons
        self.suspects = suspects
        
        while len(cards)>0:
            for player in self.player_list:
                try:
                    self.player_hands[player].append(cards.pop())
                except IndexError as e:
                    break
        
        # initial player is always Miss Scarlet, if no Miss Scarlet, then
        # use random player order
        self.character_order = list(self.char_players.keys())
        random.shuffle(self.character_order)
        if 'Miss Scarlet' in self.character_order:
            self.current_character = 'Miss Scarlet'
            self.character_order.remove('Miss Scarlet')
            self.character_order.insert(0,'Miss Scarlet')
            self.turn_counter = 0
        self.player_order = [self.char_players[c] for c in self.character_order]
        self.current_player = self.char_players[self.current_character]

    def process_player_action(self,action_info):
        '''
        Evaluates the player action that was received by the server from the
        player client.  Either rejects it if it is an invalid action, or
        acccepts it if it is valid, in which case it prepares a response dict.
        '''
        action_type = action_info['action_type']
        character = action_info['character']
        player = action_info['player']
        resp = {'status':'Completed','character':character,'player':player}

        if 'check' not in action_type and (character!=self.current_character or player!=self.current_player):
            resp['status'] = 'Rejected'
            resp['message'] = 'It\'s not your turn!'
            return resp

        if action_type=='checkAvailableMoves':
            loc = self.game_board.player_locs[character]
            possible_moves = self.game_board.nodes[loc]
            allowed_moves = []
            for move in possible_moves:
                if self.game_board.remaining_space[move]>0:
                    allowed_moves.append(str(move))
            resp['message'] = 'Possible Moves:\n'+'\n'.join(allowed_moves)
            return resp
        elif action_type=='checkHand':
            resp['message'] = '\n'.join(self.player_hands[player])
            return resp
        elif action_type=='makeSuggestion':
            loc = self.game_board.player_locs[character]
            if loc in self.hallways:
                resp['status'] = 'Rejected'
                resp['message'] = 'The murder did not occur in a hallway, so you cannot make a suggestion here'
                return resp

            weapon = action_info['weapon']
            suspect = action_info['suspect']
            self.game_board.move_char(suspect, loc)
            
            message = character+' has suggested that '+suspect+' performed the murder in the '+loc+' using the '+weapon
            self.GameServer.broadcast({'recipients':'all','message_type':'announcement','message':message})
            cardlist = [weapon, suspect, loc]
            for responder, hand in self.player_hands.items():
                intersection = self._intersection(hand, cardlist)
                if len(intersection)==0:
                    self.GameServer.broadcast({'recipients':responder,'message_type':'announcement','needs_acknowledgment':True,'message':responder+' does not have any cards which refute the suggestion of '+player})
                elif len(intersection)==1:
                    refutation = intersection[0]
                    self.GameServer.broadcast({'recipients':responder,'message_type':'announcement','needs_acknowledgment':True,'message':responder+' has the card '+refutation+' which refutes the suggestion of '+player})
                elif len(intersection)>=2:
                    self.GameServer.broadcast({'recipients':responder,'message_type':'prompt_suggestion_response','message':'you have multiple cards which can refute the suggestion, pick one to show to '+player})

            # every player must either acknowledge the response above, or if
            # has multiple cards, select one card to show. Information is not
            # disclosed until all other players have acknowledged or responded.
            awaiting_player_response = {p:True for p in self.player_list if p!=player}
            while(any(awaiting_player_response.values())):
                sugg_resps, awaiting_player_response = self.GameServer.get_sugg_resps()
                sleep(10)
            
            message = 'Each player responded in the following way:\n'
            for player, r in sugg_resps:
                message = message+player+': '+r
            resp['message'] = message
            return resp
            # TODO: fill out gameserver code, player interface, to make suggestion response section above make sense. Then use as template for remaining game state options.

        elif action_type=='makeAccusation':
            pass
        elif action_type=='moveChar':
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

    def rollover_turn(self):
        self.turn_counter += 1
        self.current_character = self.character_order[self.turn_counter % len(self.character_order)]
        self.current_player = self.player_order[self.turn_counter % len(self.player_order)]
        
    def _intersection(self, lst1, lst2):
        return list(set(lst1) & set(lst2))

class GameBoard:
    def __init__(self,rooms, hallways, secret_passages, players, player_chars, char_players):
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
        self.char_players = char_players
        for p, r in self.player_locs:
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
    
    def move_char(self, char,new_room):
        # at present presumes that validity of the move is already verified
        self.remaining_space[self.player_locs[char]]+=1
        self.player_locs[char] = new_room
        self.remaining_space[self.player_locs[char]]-=1