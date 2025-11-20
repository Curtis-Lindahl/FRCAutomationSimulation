from pygame import Vector2, Vector3
from robot import Robot
import subsystems.pivot

class OPRobot(Robot):
    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size):
        super().__init__(x, y, theta, maxaccel, maxvel, frame_size)
        self.shoulder = subsystems.pivot.Pivot(Vector3(0, 4, 35), 30, -35, -35, 135, 100, 150)
        self.elbow = subsystems.pivot.Pivot(self.shoulder.getEndPosition(), 20, self.shoulder.angle + 135, self.shoulder.angle, self.shoulder.angle + 135, 150, 200)

    def update(self, time_elapsed):
        self.shoulder.update(time_elapsed)
        self.elbow.pos = self.shoulder.getEndPosition()
        self.elbow.minAngle = self.shoulder.angle
        self.elbow.maxAngle = self.shoulder.angle + 135
        self.elbow.angle += self.shoulder.turnRate * time_elapsed
        self.elbow.update()

    def getIntakeZone(self):
        endPoint = self.elbow.getEndPosition()
        point1 = endPoint - Vector3(4, 3, 3)
        point2 = endPoint + Vector3(4, 3, 3)
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
    
    def setShoulderVelocity(self, targetVel):
        self.shoulder.setTargetVel(targetVel)

    def setElboxVelocity(self, targetVel):
        self.shoulder.setTargetVel(targetVel)