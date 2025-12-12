from pygame import Vector2, Vector3
from robot import Robot
import subsystems.pivot
from piece import Piece

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
        self.elbow.angle += self.shoulder.turnRate * time_elapsed
        self.elbow.update()
        if super().pieceHeld is not None:
            super().pieceHeld.pos = self.elbow.getEndPosition() + Vector3(super().pos.x, super().pos.y, 0)

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
        self.shoulder.setTargetVel(targetVel)