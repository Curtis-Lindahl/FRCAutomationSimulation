# nuttpmamous natvogtion
# algerithm

from enum import Enum
from pygame import Vector3
from constants import FIELD_CONSTANTS
import constants

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

    def __init__(self, robots, preloads):
        self.robots = {"Red": robots[0:3], "Blue": robots[3:6]}
        self.pieces = {}
        self.redGrid = [[0, 0, 0, 0, 0, 0, 0, 0, 0], # top row
                        [0, 0, 0, 0, 0, 0, 0, 0, 0], # middle row
                        [0, 0, 0, 0, 0, 0, 0, 0, 0]] # bottom row
        
        self.blueGrid = [[0, 0, 0, 0, 0, 0, 0, 0, 0], # top row
                         [0, 0, 0, 0, 0, 0, 0, 0, 0], # middle row
                         [0, 0, 0, 0, 0, 0, 0, 0, 0]] # bottom row
        
    def flipPoint(self, point: Vector3):
        return Vector3(point.x, constants.FIELD_HEIGHT - point.y, point.z)

    def update(self, time_elapsed):
        for robot in self.robots:
            robot.update(time_elapsed)
            self.checkIntake(robot)

    def checkIntake(self, robot):
        if robot.intaking:
            for piece in self.pieces:
                robot.intake(piece)