"""Interface to support player actions."""

import logging
import time
from game.messages.messages import MessageInterface, MOVE, ACCUSE, GUESS
from game.messages.messages import Start, DISPLAY, FAILURE, TURN
from game.messages.messages import Suggest, Accuse

logger = logging.getLogger(__name__)

# TODO: response is required from other players while still
# in current player's server_loop.  If message is to be
# received by current player's server_loop, keep as below,
# however, if refutation can only be parsed by
# that player's server_loop, then create a class attribute
# for refutations and have each responding player modify
# entries in refutations from within their own server loop.
# Refutation will require knowledge of the player's hand.
class PlayerInterface:
    """Class that creates/processes actions for the player."""

    def __init__(self, name=None):
        """Initialize PlayerInterface."""
        print("initialized")
        self.name = name

    def gather_intel(self):
        information = {}
        information['player'] = input("Who do you suspect of the muder? (input the name only)\n")
        information['weapon'] = input("What weapon did he/she use? (input the weapon only)\n")
        information['location'] = input("Where did this happen? (input the location only)\n")
        return information

    def take_turn(self):
        rsp = None
        action = input("It is your turn!\nSelect from the following: Move, Guess, Accuse\n")
        # TODO check to see if the user input is a valid option ("move", "guess", "accusation")
        # if move, process move, if guess, process guess, if accusation, process accusation
        if "MOVE" in action.upper():
            logger.debug("eventually - player will be sending a move location")
            rsp = None
        elif "GUESS" in action.upper():
            guess = self.gather_intel()
            rsp = Suggest(player=guess['player'], location=guess['location'], weapon=guess['weapon'])
        elif "ACCUSE" in action.upper():
            accuse = self.gather_intel()
            rsp = Accuse(player=accuse['player'], location=accuse['location'], weapon=accuse['weapon'])
        else:
            logger.info("Invalid choice, try again") #@TODO deal with this 
        return rsp
    # return message to be sent to game server
    # msg - message class obj
    def process_msg(self, msg, query=False):
        rsp = None
        #process the type
        if msg.function == TURN and msg.player_name == self.name:
            logger.debug("Taking turn")
            rsp = self.take_turn()
        elif msg.function == DISPLAY:
            logger.debug("display message")
            logger.info(msg.text)
        elif msg.function == UPDATE:
            logger.debug("update message")
        else:
            logger.debug(msg)
        return rsp
