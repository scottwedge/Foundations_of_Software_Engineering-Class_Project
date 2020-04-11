"""Multithreaded socket server."""

import socket
import threading
import logging
import sys

from time import sleep
from copy import deepcopy

from game.messages.messages import *
from game.server.game_state import GameState, GameBoard

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.CRITICAL)

# List of available characters that new players may select from. The dict
# constructor here allows indexing in the form 1: "Mrs. White", which helps
# users easily select a character.
avail_characters = dict([
    (1, "Mrs. White"),
    (2, "Mr. Green"),
    (3, "Mrs. Peacock"),
    (4, "Professor Plum"),
    (5, "Miss Scarlet"),
    (6, "Colonel Mustard")
])


class ThreadedServer(object):
    """Threaded server for socket interaction, management."""

    def __init__(self, host, port):
        """Initialize."""
        # Turn will always begin with the first connected client
        self.turn = 0

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        # List of tuples of (<character name>, <socket object>) added in
        # chronological order
        self.connections = []
        self.game_state = GameState()
        self.setting_up_game = True

    def listen(self):
        """Listen."""
        # Listen for a max of 6 players
        self.sock.listen(6)
        clientcounter = 0

        # Accept connections in the order they arrive, timing out if no
        # activity for 60 seconds
        while True:
            client, address = self.sock.accept()
            logger.info(" Client: " + str(client) + " connected.")
            clientcounter = clientcounter + 1
            client.settimeout(60)

            # Initiate a new thread, when a client connects, such that that
            # client is managed carefully
            threading.Thread(
                target=self.listenToClient,
                args=(client, address, clientcounter)).start()

    def listenToClient(self, client, address, clientcounter):
        """Listen to a specific client."""
        logger.info("Available characters: " + str(avail_characters))

        # The initial register message of a client has an empty player name
        initmsg = MessageInterface.recv_message(client)

        # Check to make sure this is a valid client registration message
        if initmsg.function == REGISTER and initmsg.player == "":
            # Let the client know what characters are available
            MessageInterface.send_message(client, Display(avail_characters))

        # This next register message from the client contains the integer
        # index of what character the client selected
        registered_char = MessageInterface.recv_message(client)

        # Remove that option from the list and if its already taken,
        # kick the client out
        new_player = avail_characters.pop(int(registered_char.player))

        # pop() will return none if the key does not exist in the dict,
        # which means that player has already been selected
        if new_player is None:
            MessageInterface.send_message(client, Failure())
            client.close()
            return False
        else:
            MessageInterface.send_message(client, Success(clientcounter))

            # Connections is a chronological list of players in the game. Once
            # three or more (up to 6) players have joined, gameplay may begin
            self.connections.append((new_player, client))
            logger.info("Player " + new_player + " added to connections.")

        logger.info("Available characters: " + str(avail_characters))

        if clientcounter == 1:
            # The first client connected is the "lobby leader"

            # waiting to receive message that lobby leader starts game.
            start = MessageInterface.recv_message(client)

            if start.function == START:
                game_state.setup_game()
                
                # game_state randomizes character order by randomizing
                # connection order.
                # However, Miss Scarlet is always guaranteed to be first
                self.player_order = game_state.player_order
                cdict = dict(self.connections)
                self.connections = [(p,cdict[p]) for p in self.player_order]
                self.setting_up_game = False
                MessageInterface.send_broadcast(self.connections, Turn(player_order[0]))
        else:
            while self.setting_up_game:
                # delay starting server loop until lobby leader starts game
                MessageInterface.send_message(client, 'Currently waiting for lobby leader to start game')
                sleep(15)

        # Run the game until end
        self.server_loop(client, new_player)

        logger.debug("Client shutting down...")
        return False

    def server_loop(self, client, character):
        """
        Server interaction loop.  A separate server loop exists for each client
        thread, one of which exists for each client.  

        TODO: Fill in this portion here with messaging/game state logic
        """
        
        while True:
            try:
                msg = MessageInterface.recv_message(client)

                # TODO: Winston/Nick, this is where the main game logic will
                # happen. Assuming GameState is initiated early on in the
                # server's execution (maybe in __init__?) this `msg` could
                # be handled by calling something like:
                # GameManager.handle_turn(msg)
                # You can assume that recv and send (through the message
                # interface) will always go to the correct person if you
                # use the local variable <client> to send

                # When a client is done with their turn, they will notify the
                # server, who will then increment the turn index and broadcast
                # the new turn to all players
                if msg.function == VIEWHAND:
                    player_hand = game_state.check_hand(character)
                    MessageInterface.send_message(client, Display(player_hand))
                elif msg.function == VIEWMOVES:
                    allowed_moves = game_state.check_available_moves(character)
                    MessageInterface.send_message(client, Display(allowed_moves))
                elif msg.function == MOVE:
                    resp = game_state.move_char(character, destination)
                    if resp['status']=='Invalid':
                        MessageInterface.send_message(client, Display(resp['message']))
                    else:
                        MessageInterface.send_broadcast(self.connections, Display(resp['message']))
                elif msg.function == SUGGEST:
                    suspect = msg.player
                    weapon = msg.weapon
                    loc = msg.location
                    resp = check_suggestion(character, suspect, weapon, loc)
                    if resp['status'] is 'Invalid':
                        # reject invalid suggestion, try again
                        MessageInterface.send_message(client, Display(resp['message']))
                        continue

                    others = [c for c in self.connections if client not in c]
                    # TODO: response is required from other players while still
                    # in current player's server_loop.  If message is to be
                    # received by current player's server_loop, keep as below,
                    # however, if refutation can only be parsed by
                    # that player's server_loop, then create a class attribute
                    # for refutations and have each responding player modify
                    # entries in refutations from within their own server loop.
                    # Refutation will require knowledge of the player's hand.
                    refutations = {c:None for c in others}
                    MessageInterface.send_broadcast(others, Display(resp['message']))

                    # polls each client other than the one to which this server
                    # loop belongs to for a response to the suggestion.
                    # TODO: This probably should be moved into its own
                    # msg.function elif block tbh.
                    while not all(refutations.values()):
                        for char in refutations.keys():
                            refute = MessageInterface.recv_message(char[1])
                            refutation = refute.refutation
                            # card name if refuted, None if no refutation made

                            if refute.function==REFUTE and refutation:
                                MessageInterface.send_message(client, refutation)

                elif msg.function == ACCUSE:
                    suspect = msg.player
                    weapon = msg.weapon
                    loc = msg.location
                    resp = make_accusation(character, weapon, suspect, loc)

                    resp.send_broadcast(self.connections, Display(resp['message']))

                    if resp['status'] is 'Incorrect':
                        self.connections.remove((character, client))
                        client.close()
                        return False
                    else:
                        # TODO: Insert shutdown sequence here
                        pass

                elif msg.function == ENDTURN:
                    self.turn = (self.turn + 1) % len(self.connections)
                    self.game_state.rollover_turn()

                    # Player name is the first element in the connections tuple
                    # [("Professor Plum", <socket object>), etc]
                    player = self.connections[self.turn][0]
                    MessageInterface.send_broadcast(self.connections, Turn(player))

            except SystemError:
                client.close()
                return False


if __name__ == "__main__":
    # Set optional verbose debugging level
    if len(sys.argv) > 1 and sys.argv[1] == "-V":
        logger.setLevel(logging.DEBUG)

    # Initiate the server
    ThreadedServer('', 4443).listen()
