from enum import Enum
from pygame import Vector3

class PieceType(Enum):
    CUBE = 1
    CONE = 2

class NodeType(Enum):
    CUBE = 1
    CONE = 2
    HYBRID = 3

class Piece: 

    def __init__(self, type: PieceType, pos: Vector3):
        self.pos = pos
        self.type = type
        self.vel = Vector3(0, 0, 0)