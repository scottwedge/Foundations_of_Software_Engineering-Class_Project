"""Message protocol."""

import json

# Message functions
FUNCTIONS = {
    "NULL": 0,
    "SUGGEST": 1,
    "ACCUSE": 2,
    "REFUTE": 3,
    "MOVE": 4,
    "UPDATE": 5,
    "DISPLAY": 6,
    "TURN": 7,
    "REGISTER": 8,
    "QUERY": 9,
    "START": 10,
    "GUESS": 11
}


class MessageInterface:
    """Exposes functionality to create and use messages."""

    @staticmethod
    def create_message(function: int, data: object):
        """Create a new message and serialize its content."""
        msg = Message(function, data)

        # Serialize the object into the form {"x": 1, "y": 2}
        return json.dumps(msg.__dict__)

    @staticmethod
    def process_message(serialdata, query=False):
        """
        Deserialize data and prepare a python object.

        TODO: Finish building new message from incoming serial data
        """
        msg = Message()
        obj = json.loads(serialdata)
        if query:
            msg.data = obj["turn"]
        return msg


class Message:
    """Base class for all messages between client and server."""

    def __init__(self, function: int = 0, data: object = None):
        """
        Initialize Message object.

        Message provides two standardized fields; function and checksum,
        in addition to data, a content field determined by the message
        function.
        """
        # One of the 12 options listed with FUNCTIONS
        self.function = function

        # Hash of Message object and its contents, guarantees integrity
        self.checksum = None

        # Data may be 12 different object types, but will match directly with
        # function. For example, if this message is of type SUGGEST, then the
        # function field will be 1 and the data field will contain the
        # following information: player, location, weapon
        self.data = data

    def get_data(self):
        """Get function-based data object."""
        return self.data

    def set_data(self, data: object):
        """
        Set the data object.

        The data object can be one of the following objects from the list
        below.
        """
        self.data = data


class Suggest:
    """Make a clue suggestion."""

    def __init__(self, player, location, weapon):
        """Set suggestion."""
        self.player = player
        self.location = location
        self.weapon = weapon


class Accuse:
    """Make a clue accusation."""

    def __init__(self, player, location, weapon):
        """Set accusation."""
        self.player = player
        self.location = location
        self.weapon = weapon


class Refute:
    """Refute an accusation."""

    def __init__(self):
        """TODO."""
        pass


class Move:
    """Make a move."""

    def __init__(self):
        """TODO."""
        pass


class Update:
    """Board state update."""

    def __init__(self, board):
        """TODO."""
        pass


class Display:
    """Display text."""

    def __init__(self, text):
        """Set display text for client."""
        self.text = text


class Turn:
    """Take a turn."""

    def __init__(self, source, destination):
        """Set move from source to destination."""
        self.source = source
        self.destination = destination


class Register:
    """Register a player."""

    def __init__(self, player, id):
        """Add a new player with unique ID."""
        self.player = player
        self.id = id


class Query:
    """Query."""

    def __init__(self):
        """Query."""
        pass


class Start:
    """Start."""

    def __init__(self):
        """Start."""
        pass


class Guess:
    """Guess."""

    def __init__(self):
        """Guess."""
        pass
