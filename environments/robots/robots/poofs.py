from pathlib import Path
import sys

parent_dir = str(Path(__file__).resolve().parents[1])

sys.path.insert(0, parent_dir)
from robot import Robot # use the module name
from piece import Piece

from pygame import Vector2, Vector3
import subsystems.elevator

class PoofsRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece)
        self.elevator = subsystems.elevator.Elevator(Vector3(-11, 0, 5), 42, 120, 500, 0)
        self.laterator = subsystems.elevator.Elevator(self.elevator.getEndPosition(), 60, 150, 500, 75)

    def update(self, time_elapsed):
        super().update(time_elapsed)
        self.elevator.update(time_elapsed)
        self.laterator.pos = self.elevator.getEndPosition()
        self.laterator.update(time_elapsed)
        if self.pieceHeld is not None:
            self.pieceHeld.pos = self.laterator.getEndPosition().rotate(self.theta, Vector3(0, 0, 1)) + Vector3(self.pos.x, self.pos.y, 0)


    # returns 2 positions that represent two vertices of the box of which if a piece is in it would intake
    # we will assume 8 wide, 4 tall, and 6 deep
    def getIntakeZone(self):
        endPoint = self.laterator.getEndPosition()
        point1 = endPoint - Vector3(4, 3, 2)
        point2 = endPoint + Vector3(4, 3, 2)
        return point1, point2
    
    
    
    def moveWithVel(self, targetVel: Vector2):
        super().setTargetVel(targetVel)
    
    def setElevatorVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)

    def setLateratorVel(self, targetVel):
        self.laterator.setTargetVel(targetVel)