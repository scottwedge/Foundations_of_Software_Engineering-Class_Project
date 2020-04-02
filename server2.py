"""Multithreaded socket server."""

import socket
import threading
import logging
import sys

from game.messages.messages import MessageInterface
from game.messages.messages import REGISTER, START, ENDTURN
from game.messages.messages import Failure, Success, Turn, Display

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

# List of tuples of (<character name>, <socket object>) added in chronological
# order
connections = []


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
            connections.append((new_player, client))
            logger.info("Player " + new_player + " added to connections.")

        logger.info("Available characters: " + str(avail_characters))

        # The first client connected is the "lobby leader"
        if clientcounter == 1:
            # Lobby leader has indicated the game can begin
            start = MessageInterface.recv_message(client)
            if start.function == START:
                MessageInterface.send_broadcast(connections, Turn(new_player))

        # Run the game until end
        self.server_loop(client)

        logger.debug("Client shutting down...")
        return False

    def server_loop(self, client):
        """
        Server interaction loop.

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
                if msg.function == ENDTURN:
                    self.turn = (self.turn + 1) % len(connections)

                    # Player name is the first element in the connections tuple
                    # [("Professor Plum", <socket object>), etc]
                    player = connections[self.turn][0]
                    MessageInterface.send_broadcast(connections, Turn(player))

            except SystemError:
                client.close()
                return False


if __name__ == "__main__":
    # Set optional verbose debugging level
    if len(sys.argv) > 1 and sys.argv[1] == "-V":
        logger.setLevel(logging.DEBUG)

    # Initiate the server
    ThreadedServer('', 4443).listen()