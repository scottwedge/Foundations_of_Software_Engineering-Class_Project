"""Defines initial game board and prepares it for play."""

SUSPECTS = [
    "Colonel Mustard",
    "Miss Scarlet",
    "Professor Plum",
    "Mr. Green",
    "Mrs. White",
    "Mrs Peacock"
]

WEAPONS = [
    "Rope",
    "Lead Pipe",
    "Knife",
    "Wrench",
    "Candlestick",
    "Revolver"
]

ROOMS = [
    "Study",
    "Hall",
    "Lounge",
    "Library",
    "Billiard Room",
    "Dining Room",
    "Conservatory",
    "Ballroom",
    "Kitchen"
]


class Location:
    """Base class for Rooms and Hallways."""

    def __init__(self):
        """Initialize."""
        # All locations have valid moves for players to make
        self.validmoves = []


class Room(Location):
    """There are 9 possible Rooms."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        # A weapon may be placed at random into the room
        self.weapon = None

        # A room may have a secret passageway
        self.passageway = None

        # A room may have 0 or more players in it
        self.occupants = None

        super(Room, self).__init__(*args, **kwargs)


class Hallway(Location):
    """There are 12 possible Hallways."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        # A hallway may have 0 or 1 players in it
        self.occupied = None

        super(Hallway, self).__init__(*args, **kwargs)


class Board:
    """Constructs and manages game board."""

    def __init(self):
        pass
