from robot import Robot
from pygame import Vector2, Vector3
import subsystems.elevator, subsystems.pivot

# Telescoping arm on a wrist with low rear pivot
class JITBRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size)
        self.pivot = subsystems.pivot.Pivot(Vector3(-10, 0, 8), 16, 45, 0, 180, 180, 250)
        self.telescope = subsystems.elevator.Elevator(self.pivot.pos + Vector3(0, 0, -5), 75, 200, 450, self.pivot.angle)
        self.wrist = subsystems.pivot.Pivot(self.telescope.getEndPosition(), 4.5, 90, 0, 180, 360, 500)
        self.intaking = False

    def update(self, time_elapsed):
        self.pivot.update(time_elapsed)
        self.telescope.angle = self.pivot.angle
        self.telescope.update(time_elapsed)
        self.wrist.pos = self.telescope.getEndPosition()
        self.wrist.update(time_elapsed)

    # returns 2 positions that represent two vertices of the box of which if a piece is in it would intake
    def getIntakeZone(self):
        endPoint = self.wrist.getEndPosition()
        point1 = endPoint - Vector3(7, 4, 2)
        point2 = endPoint + Vector3(7, 4, 2)
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

    def rotateWrist(self, targetVel):
        self.wrist.setTargetVel(targetVel)
    
    def setTelescopeVel(self, targetVel):
        self.telescope.setTargetVel(targetVel)

    def setPivotVel(self, targetVel):
        self.telescope.setTargetVel(targetVel)