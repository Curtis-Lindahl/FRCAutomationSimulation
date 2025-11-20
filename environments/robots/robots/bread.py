from environment import PieceType
from robot import Robot
from subsystems.elevator import Elevator
from subsystems.pivot import Pivot
from pygame import Vector2, Vector3

class BreadRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size)
        self.elevator = Elevator(Vector3(0, 9, 15), 40, 60, 60, 38)
        self.manipulatorPivot = Pivot(self.elevator.getEndPosition(), 12, 110, -45, 110, 180, 180)
        self.intakePivot = Pivot(Vector3(0, -12, 12), 15, 0, 0, 90, 150, 150)

    def update(self, time_elapsed):
        self.intakePivot.update()
        self.elevator.update()
        self.manipulatorPivot.pos = self.elevator.getEndPosition()
        self.manipulatorPivot.update()
        super().update(time_elapsed)

    # returns 2 positions that represent two vertices of the box of which if a piece is in it would intake
    # we will assume 8 wide, 4 tall, and 6 deep
    def getIntakeZone(self, piece: PieceType): #TODO fix
        if PieceType is PieceType.CONE:
            endPoint = self.manipulatorPivot.getEndPosition()
            point1 = endPoint - Vector3(4, 3, 2)
            point2 = endPoint + Vector3(4, 3, 2)
            return point1, point2
        if self.intakePivot.angle < 80:
            return Vector3(0, 0, 0), Vector3(0, 0, 0)
        point1 = Vector3(13, -16, 12)
        point2 = Vector3(-13, -26, 0)
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