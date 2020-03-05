"""
Different classes that will be serialized as json obects
"""
class Move():
	def __init__(self, location):
		self.location = location

class Guess():
	def __init__(self, weapon, room):
		self.weapon = weapon
		self.location = room