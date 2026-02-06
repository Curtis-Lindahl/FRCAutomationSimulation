from environments.piece import Piece, PieceType
from robot import Robot
from subsystems.elevator import Elevator
from subsystems.pivot import Pivot
from pygame import Vector2, Vector3

class BreadRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece)
        self.elevator = Elevator(Vector3(0, 9, 15), 40, 60, 60, 38)
        self.manipulatorPivot = Pivot(self.elevator.getEndPosition(), 12, 110, -45, 110, 180, 180)
        self.intakePivot = Pivot(Vector3(0, -12, 12), 15, 0, 0, 90, 150, 150)
        # self.subssytems = [self.elevator, self.manipulatorPivot, self.intakePivot]

    def update(self, time_elapsed):
        self.intakePivot.update(time_elapsed)
        self.elevator.update(time_elapsed)
        self.manipulatorPivot.pos = self.elevator.getEndPosition()
        self.manipulatorPivot.update(time_elapsed)
        super().update(time_elapsed)
        if self.pieceHeld is not None:
            self.pieceHeld.pos = self.manipulatorPivot.getEndPosition().rotate(self.theta, Vector3(0, 0, 1)) + Vector3(self.pos.x, self.pos.y, 0)

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
    
    
    def moveWithVel(self, targetVel: Vector2):
        super().setTargetVel(targetVel)