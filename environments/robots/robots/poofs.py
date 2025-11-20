import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1,)

from robot import Robot
from pygame import Vector2, Vector3
import subsystems.elevator

class PoofsRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size)
        self.elevator = subsystems.elevator.Elevator(Vector3(-11, 0, 5), 42, 120, 120, 0)
        self.laterator = subsystems.elevator.Elevator(Vector3(self.elevator.getEndPosition()), 60, 40, 40, Vector3(0, 15, 0))

    def update(self, time_elapsed):
        self.laterator.pos = self.elevator.getEndPosition()
        super().update(time_elapsed)
        self.elevator.update(time_elapsed)
        self.laterator.update(time_elapsed)

    # returns 2 positions that represent two vertices of the box of which if a piece is in it would intake
    # we will assume 8 wide, 4 tall, and 6 deep
    def getIntakeZone(self):
        endPoint = self.laterator.getEndPosition()
        point1 = endPoint - Vector3(4, 3, 2)
        point2 = endPoint + Vector3(4, 3, 2)
        return point1, point2
    
    def canIntake(self, gamePiecePosition):
        point1, point2 = self.getIntakeZone()
        min_x, max_x = sorted((point1.x, point2.x))
        min_y, max_y = sorted((point1.y, point2.y))
        min_z, max_z = sorted((point1.z, point2.z))
        # use inclusive bounds: min <= coord <= max
        return (min_x <= gamePiecePosition.x <= max_x and
                min_y <= gamePiecePosition.y <= max_y and
                min_z <= gamePiecePosition.z <= max_z)
    
    def intake(self, gamePiecePosition):
        if super().hasPiece:
            return False
        if self.canIntake(gamePiecePosition):
            super().hasPiece = True
            return True
        return False
    
    def moveWithVel(self, targetVel: Vector2):
        super().setTargetVel(targetVel)
    
    def setElevatorVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)

    def setLateratorVel(self, targetVel):
        self.laterator.setTargetVel(targetVel)