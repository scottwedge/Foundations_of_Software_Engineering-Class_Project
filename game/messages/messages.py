"""Message protocol."""

import json

# Message functions
SUGGEST = 1
ACCUSE = 2
REFUTE = 3
MOVE = 4
UPDATE = 5
DISPLAY = 6
TURN = 7


class MessageInterface:
    """Provides functionality to create and use messages."""

    @staticmethod
    def create_message(function, data):
        """Create a new message and serialize its content."""
        msg = Message()
        msg.function = function
        msg.data = data

        # Serializes the class into the form {"x": 1, "y": 2}
        return json.dumps(msg.__dict__)

    @staticmethod
    def process_message(serialdata):
        """Deserialize data and prepare a python object."""
        msg = Message()
        msg = json.loads(serialdata)
        return msg


class Message:
    """Base class for all messages between client and server."""

    def __init__(self):
        self.function = None
        self.checksum = None
        self.data = None

    def get_data(self):
        return self.data

    def set_data(self, data):
        """
        SUGGEST:
            {
                "player":
                "location":
                "weapon":
            }

        ACCUSE:
            {
                "player":
                "location":
                "weapon":
            }
            
        REFUTE:
            {
                TBD
            }

        MOVE:
            {
                TBD
            }

        UPDATE:
            {
                <serialized entire gamestate>
            }

        DISPLAY:
            <data>

        TURN:
            <its your turn!>
        
        """
        self.data = data
