"""Single threaded client."""

import socket
import logging
import sys
import pprint
from time import sleep

from game.client.player_interface import PlayerInterface
from game.messages.messages import MessageInterface, Register, EndTurn
from game.messages.messages import Start, DISPLAY, FAILURE, TURN

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.CRITICAL)


class Client:
    """Client object."""

    def __init__(self):
        """Initialize."""
        self.player = None
        self.player_interface = None

    def startup(self, sock):
        """Start the connection to the server."""
        # Notify the server there is a new player who would like to select
        # a character
        MessageInterface.send_message(sock, Register(""))

        # Wait for the list of available characters from the server
        char_list = MessageInterface.recv_message(sock)

        # Make sure this is a "display" message, then present the contents
        # to the user and capture their character selection
        if char_list.function == DISPLAY:
            pprint.pprint(char_list.text)
        char_select = str(input("Select a character by index: "))

        # <player> is one of the pre-defined Clue character names
        self.player = char_list.text[char_select]
        print("You have selected: " + self.player)

        # Notify the server of the character selection so that it can be
        # removed from the list of available characters
        # Note: send the index, rather than the character name, so that its
        # easier for the server to remove from the list of available
        MessageInterface.send_message(sock, Register(char_select))

        # Check the server's response (if the character was taken) and display
        status = MessageInterface.recv_message(sock)
        if status.function == FAILURE:
            print("That character has already been chosen. Please re-connect")
            return
        else:
            print("Welcome to Clue, " + self.player)

        # Create a new instance of the PlayerInterface
        # TODO: Genny: Once the message logic is setup in this module, its
        # all on you to decide how the game is played from the perspective of
        # the client.
        self.player_interface = PlayerInterface(self.player)

        # Determine if the players are ready. The first client connected is
        # the "lobby leader" and responsible for starting the game
        if status.clientcounter == 1:
            self.confirm_ready()

            # When the lobby leader has decided the lobby is ready, notify
            # the server to start the game
            MessageInterface.send_message(sock, Start())

        # Run the game indefinitely
        self.client_loop(sock)

        logger.debug("Game shutting down...")
        return

    def client_loop(self, sock):
        """
        Game interaction loop.

        TODO: Fill in this portion here with messaging/PlayerInterface logic
        """
        msg_counter = 0
        while sock:
            # Get the message from the server
            logger.info("Waiting for new message from server...")
            msg = MessageInterface.recv_message(sock)
            logger.info("Msg#: " + str(msg_counter) + " " + str(msg.__dict__))

            # Call into the player interface here and handle things
            rsp = self.player_interface.process_msg(msg)
            # if there is a response, send it back to the server
            # rsp is created in the player interface to be a Message type object
            if rsp is not None:
                logger.info("sending message to server")
                MessageInterface.send_message(sock, rsp)
            # At the end of the turn, you MUST tell the server
            if rsp is not None or (msg.function == TURN and msg.player_name == self.name):
                logger.info("ending turn")
                MessageInterface.send_message(sock, EndTurn())

            msg_counter = msg_counter + 1

    def confirm_ready(self):
        """Loop until lobby is ready."""
        while True:
            reply = str(input("Is the lobby ready? (y/n): ")).lower().strip()
            if reply[0] == 'y':
                return True


if __name__ == "__main__":
    # Set optional verbose debugging level
    if len(sys.argv) > 1 and sys.argv[1] == "-V":
        logger.setLevel(logging.DEBUG)

    # Attempt the connection to the server
    logger.info("Attempting connection to server.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((socket.gethostname(), 4443))
    except InterruptedError:
        sock.close()

    client = Client()
    logger.info("")
    client.startup(sock)
