"""Message protocol."""

import json

FUNCTIONS = [
    "SUGGEST",
    "ACCUSE",
    "REFUTE",
    "MOVE",
    "UPDATE",
    "DISPLAY",
    "TURN"
]


class MessageInterface:
    """Provides functionality to create and use messages."""

    @staticmethod
    def create_message(function, data):
        """Create a new direct message and serialize its content."""
        msg = Message()
        msg.function = function
        msg.data = data

        # Serializes the class into the form {"x": 1, "y": 2}
        return json.dumps(msg.__dict__)


class Message:
    """Base class for all messages between client and server."""

    def __init__(self):
        self.function = None
        self.checksum = None
        self.data = None
