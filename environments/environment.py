from enum import Enum
from pygame import Vector3

class PieceType(Enum):
    CUBE = 1
    CONE = 2

class Piece():

    def __init__(self, pos):
        self.pos = pos

class Environment:

    def __init__(self):
        pass

    def update(self, time_elapsed):
        pass