from pygame import Vector2, Vector3
from robot import Robot
import subsystems.pivot
from environments.piece import Piece

class OPRobot(Robot):
    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece):
        super().__init__(x, y, theta, maxaccel, maxvel, frame_size, piece)
        self.shoulder = subsystems.pivot.Pivot(Vector3(0, 4, 35), 30, -35, -35, 135, 100, 150)
        self.elbow = subsystems.pivot.Pivot(self.shoulder.getEndPosition(), 20, self.shoulder.angle + 135, self.shoulder.angle, self.shoulder.angle + 135, 150, 200)

    def update(self, time_elapsed):
        self.shoulder.update(time_elapsed)

        self.elbow.pos = self.shoulder.getEndPosition()
        self.elbow.minAngle = self.shoulder.angle
        self.elbow.maxAngle = self.shoulder.angle + 135
        # self.elbow.angle += self.shoulder.turnRate * time_elapsed
        self.elbow.update(time_elapsed)
        super().update(time_elapsed)
        print(self.shoulder.getEndPosition())
        print(self.elbow.pos)
        if self.pieceHeld is not None:
            print(self.pieceHeld)
            self.pieceHeld.pos = self.elbow.getEndPosition().rotate(self.theta, Vector3(0, 0, 1)) + Vector3(self.pos.x, self.pos.y, 0)

    def getIntakeZone(self):
        endPoint = self.elbow.getEndPosition()
        point1 = endPoint - Vector3(4, 3, 3)
        point2 = endPoint + Vector3(4, 3, 3)
        return point1, point2
    
    def moveWithVel(self, targetVel: Vector2):
        super().setTargetVel(targetVel)
    
    def setShoulderVelocity(self, targetVel):
        self.shoulder.setTargetVel(targetVel)

    def setElboxVelocity(self, targetVel):
        self.elbow.setTargetVel(targetVel)