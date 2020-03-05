import os
import pygame
from clue_room import ClueRoom
class ClueGameDisplay():
    def __init__(self):
        pygame.init()
        width = 320
        height = 320
        self.cwd = os.path.dirname(__file__)
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Clue")

        self.clock=pygame.time.Clock()
        self.loadSprites()

    def loadSprites(self):
        self.room = pygame.image.load(f"{self.cwd}/mockroom.png")
        self.verthall = pygame.image.load(f"{self.cwd}/mockhall.png")
        self.horizhall = pygame.transform.rotate(pygame.image.load(f"{self.cwd}/mockhall.png"), 90)


    def drawInitState(self):
        for x in range(3):
            for y in range(3):
                self.display.blit(self.room, [(x)*128, y*(128)])
                self.display.blit(self.horizhall, [(x)*128+64, y*128])

                if y == 2:
                    break
                self.display.blit(self.verthall, [(x)*128, y*128 + 64])

    def update(self):
        self.clock.tick(60)
        self.display.fill(0)
        self.drawInitState()

        for event in pygame.event.get():
        #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()

        #update the screen
        pygame.display.flip()

class ClueGameState():
    def __init__(self):
        self.study = ClueRoom("library", {"east": "empty",
                                    "south": "prof"}, secret=self.kitchen)
        self.hall = ClueRoom("hall", {"west": "empty",
                                    "east": "scarlet"})
        self.lounge = ClueRoom("lounge", {"west": "scarlet",
                                    "south": "mustard"}, secret=self.conservatory)
        self.library = ClueRoom("library", {"north": "plum",
                            "south": "peacock", "east": "empty"})
        self.billard_room = ClueRoom("billard_room", {"north": "empty",
                            "south": "empty", "east": "empty", "west": "empty"})
        self.dining_room = ClueRoom("dining_room", {"north": "mustard",
                            "south": "empty", "west": "empty"})
        self.conservatory = ClueRoom("conservatory", {"north": "peacock",
                            "east": "green"}, secret=self.lounge)
        self.ballroom = ClueRoom("ballroom", {"west": "green",
                            "east": "white"})
        self.kitchen = ClueRoom("kitchen", {"west": "white",
                            "north": "empty"}, secret=self.study)

cg=ClueGame() #__init__ is called right here
while 1:
    cg.update()