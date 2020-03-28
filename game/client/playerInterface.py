"""
"""
import select
import socket
import sys
import time
sys.path.append('../messages')
from messages import Message

class PlayerInterface:
    """Class that creates/processes actions for the player."""
    def __init__(self, name=None):
        print("initialized")
        self.name = "temp"

    def take_turn(self):
        action = input("It is your turn!\nSelect from the following: Move, Guess, Accusation\n")
        # TODO check to see if the user input is a valid option ("move", "guess", "accusation")
        # if move, process move, if guess, process guess, if accusation, process accusation
        return action

    def process_text(self, msg):
        print("text message")
        print(msg.data)
        action = input("Your response?\nPress enter if None\n")
        if len(action) == 0:
            action = None
        return action

    # return message to be sent to game server
    # msg - message class obj
    def process_msg(self, msg):
        print("process msg")
        rsp = None
        #process the type
        if msg.function == 7:
            rsp = self.take_turn()
        elif msg.function == 6:
            rsp = self.process_text(msg)
        else:
            print(msg)
        return rsp