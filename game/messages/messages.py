"""Message protocol."""

import json
import logging
import struct

# Message functions
NULL = 0
SUGGEST = 1
ACCUSE = 2
REFUTE = 3
MOVE = 4
VIEWHAND = 5
VIEWMOVES = 6
UPDATE = 7
DISPLAY = 8
TURN = 9
REGISTER = 10
QUERY = 11
START = 12
ENDTURN = 13
SUCCESS = 14
FAILURE = 15
ENDGAME = 16

message_db = {}

logger = logging.getLogger(__name__)


class MessageInterface:
    """Exposes functionality to create and use messages."""

    @staticmethod
    def send_broadcast(socklist, data):
        """
        Send a new broadcast message.

        Requires the list of connections and a python object.
        """
        # Create a json dict of the message
        msg = MessageInterface.create_message(data)

        for player, sock in socklist:
            # Send message size (in bytes) first
            sock.sendall(struct.pack("!I", len(bytes(msg, "utf-8"))))

            # Send the message
            sock.sendall(bytes(msg, "utf-8"))

    @staticmethod
    def send_message(sock, data):
        """
        Send a message.

        Requires a valid socket object and a python object.
        """
        # Create a json dict of the message
        msg = MessageInterface.create_message(data)

        # Send message size (in bytes) first
        sock.sendall(struct.pack("!I", len(bytes(msg, "utf-8"))))

        # Send the message
        sock.sendall(bytes(msg, "utf-8"))

    @staticmethod
    def recv_message(sock):
        """
        Recieve a message.

        Requires a valid socket object and bytes length to accept. Will return
        a valid object.
        """
        # The size of any message is a 4-byte field
        msgsize = sock.recv(4)

        # Pull out the message size
        (length,) = struct.unpack("!I", msgsize)

        # Recieve the message
        msg = sock.recv(length).decode("utf-8")
        msg = json.loads(msg)

        return MessageInterface.process_message(msg)

    @staticmethod
    def create_message(message_obj: object):
        """Prepare a message object to send."""
        # Serialize the object into the form {"x": 1, "y": 2}
        logger.debug(json.dumps(message_obj.__dict__))
        return json.dumps(message_obj.__dict__)

    @staticmethod
    def process_message(serialdata):
        """
        Deserialize data and prepare a python object.

        TODO: Finish building new message from incoming serial data
        """
        cls = message_db.get(serialdata["function"])
        inst = cls()
        inst.deserialize(serialdata)

        logger.debug("After deserialize of JSON data")
        logger.debug(inst.__dict__)

        return inst

    @staticmethod
    def register_message(new_message: object, function: int):
        """
        Register a new class for new message type.

        Added for each new message type as they are defined in messages.py.
        """
        message_db[function] = new_message


class Message:
    """Base class for all messages between client and server."""

    def __init__(self, function: int = 0):
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


class Suggest(Message):
    """Make a clue suggestion."""

    def __init__(self, player=None, location=None, weapon=None):
        """Set suggestion."""
        self.player = player
        self.location = location
        self.weapon = weapon

        super(Suggest, self).__init__(SUGGEST)

    def deserialize(self, obj):
        """Deserialize from json object."""
        self.player = obj["player"]
        self.location = obj["location"]
        self.weapon = obj["weapon"]


MessageInterface.register_message(Suggest, SUGGEST)


class Accuse(Message):
    """Make a clue accusation."""

    def __init__(self, player=None, location=None, weapon=None):
        """Set accusation."""
        self.player = player
        self.location = location
        self.weapon = weapon

        super(Accuse, self).__init__(ACCUSE)

    def deserialize(self, obj):
        """Deserialize from json object."""
        self.player = obj["player"]
        self.location = obj["location"]
        self.weapon = obj["weapon"]


MessageInterface.register_message(Accuse, ACCUSE)


class Refute(Message):
    """Refute an accusation."""

    def __init__(self):
        """TODO."""
        super(Refute, self).__init__(REFUTE)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Refute, REFUTE)


class Move(Message):
    """Make a move."""

    def __init__(self):
        """TODO."""
        super(Move, self).__init__(MOVE)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Move, MOVE)


class ViewHand(Message):
    """Make a move."""

    def __init__(self):
        """TODO."""
        super(ViewHand, self).__init__(ViewHand)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(ViewHand, VIEWHAND)


class ViewMoves(Message):
    """Make a move."""

    def __init__(self):
        """TODO."""
        super(ViewMoves, self).__init__(ViewMoves)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(ViewMoves, VIEWMOVES)


class Update(Message):
    """Board state update."""

    def __init__(self, board=None):
        """TODO."""
        self.board = board
        super(Update, self).__init__(UPDATE)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Update, UPDATE)


class Display(Message):
    """Display text."""

    def __init__(self, text=None):
        """Set display text for client."""
        self.text = str(text)

        super(Display, self).__init__(DISPLAY)

    def deserialize(self, obj):
        """TODO."""
        self.text = obj["text"]


MessageInterface.register_message(Display, DISPLAY)


class Turn(Message):
    """Take a turn."""

    def __init__(self, player_name=""):
        """Set move from source to destination."""
        self.player_name = player_name
        super(Turn, self).__init__(TURN)

    def deserialize(self, obj):
        """TODO."""
        self.player_name = obj["player_name"]


MessageInterface.register_message(Turn, TURN)


class Register(Message):
    """Register a player."""

    def __init__(self, player=""):
        """Add a new player."""
        self.player = player

        super(Register, self).__init__(REGISTER)

    def deserialize(self, obj):
        """TODO."""
        self.player = obj["player"]


MessageInterface.register_message(Register, REGISTER)


class Query(Message):
    """Query."""

    def __init__(self):
        """Query."""
        super(Query, self).__init__(QUERY)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Query, QUERY)


class Start(Message):
    """Start."""

    def __init__(self):
        """Start."""
        super(Start, self).__init__(START)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Start, START)


class Failure(Message):
    """Failure."""

    def __init__(self):
        """Fail."""
        super(Failure, self).__init__(FAILURE)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(Failure, FAILURE)


class Success(Message):
    """Success."""

    def __init__(self, clientcounter=0):
        """Success."""
        self.clientcounter = clientcounter
        super(Success, self).__init__(SUCCESS)

    def deserialize(self, obj):
        """TODO."""
        self.clientcounter = obj["clientcounter"]


MessageInterface.register_message(Success, SUCCESS)


class EndTurn(Message):
    """End turn."""

    def __init__(self):
        """End turn."""
        super(EndTurn, self).__init__(ENDTURN)

    def deserialize(self, obj):
        """TODO."""
        pass


MessageInterface.register_message(EndTurn, ENDTURN)
