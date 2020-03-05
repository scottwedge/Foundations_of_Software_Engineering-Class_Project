class ClueHall:
	def __init__(self, occupant, rooms)
		self.occupant = None
		self.rooms = rooms

	def isBlocked():
		for exit in rooms:
			if exit.occupant = None:
				return False
		return True

	def setRooms(rooms):
		self.rooms = rooms

class ClueRoom:
	"""A class that contains state info about rooms"""

	def __init__(self, room_name, halls, secret=None):
		self._room_name = room_name
		self.halls = halls
		self.occupant = None
		self._secret = secret

	def isBlocked():
		for exit in halls:
			if exit.occupant = None:
				return False
		return True

	def setHalls(halls):
		self.halls = halls

	