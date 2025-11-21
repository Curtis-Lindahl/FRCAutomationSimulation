from enum import Enum
from pygame import Vector3

class PieceType(Enum):
    CUBE = 1
    CONE = 2

class Piece():

    def __init__(self, type: PieceType, pos):
        self.pos = pos
        self.type =type

class Environment:

    def __init__(self):
        pass

    def update(self, time_elapsed):
        pass