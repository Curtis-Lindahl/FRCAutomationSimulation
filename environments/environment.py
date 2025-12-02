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

    def __init__(self, type: PieceType, pos):
        self.pos = pos
        self.type = type

class Environment:

    def __init__(self, robots):
        self.robots = robots

    def update(self, time_elapsed):
        for robot in self.robots:
            robot.update(time_elapsed)