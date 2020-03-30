"""Interface to support player actions."""

from game.messages.messages import MessageInterface, MOVE, ACCUSE, GUESS


class PlayerInterface:
    """Class that creates/processes actions for the player."""

    def __init__(self, name=None):
        """Initialize PlayerInterface."""
        print("initialized")
        self.name = name

    def take_turn(self):
        action = input("It is your turn!\nSelect from the following: Move, Guess, Accuse\n")
        # TODO check to see if the user input is a valid option ("move", "guess", "accusation")
        # if move, process move, if guess, process guess, if accusation, process accusation
        if "MOVE" in action.upper():
            function = MOVE
        elif "GUESS" in action.upper():
            function = GUESS
        elif "ACCUSE" in action.upper():
            function = ACCUSE
        else:
            print("Invalid choice, try again")
            return self.take_turn()    # this is the worst hack of all time
        return MessageInterface.create_message(function, action)

    def process_text(self, msg):
        print("text message")
        print(msg.data)
        action = input("Your response?\nPress enter if None\n")
        if len(action) == 0:
            action = None
        return action

    # return message to be sent to game server
    # msg - message class obj
    def process_msg(self, msg, query=False):
        print("process msg")
        rsp = None
        #process the type
        print(self.name)
        print(msg.data)
        if msg.data in self.name and query:
            rsp = self.take_turn()
        elif msg.function == 6:
            rsp = self.process_text(msg)
        else:
            print(msg)
        return rsp
