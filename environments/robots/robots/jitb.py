from robot import Robot
from pygame import Vector2, Vector3
import subsystems.elevator, subsystems.pivot
from environments.piece import Piece

# Telescoping arm on a wrist with low rear pivot
class JITBRobot(Robot):

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece):
        Robot.__init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece)
        self.pivot = subsystems.pivot.Pivot(Vector3(-10, 0, 8), 16, 45, 0, 180, 180, 250, 0)
        self.telescope = subsystems.elevator.Elevator(self.pivot.pos + Vector3(0, 0, -5), 75, 200, 450, self.pivot.angle)
        self.wrist = subsystems.pivot.Pivot(self.telescope.getEndPosition(), 4.5, 90, 0, 180, 360, 500, 0)

    def update(self, time_elapsed):
        self.pivot.update(time_elapsed)
        self.telescope.pos = self.pivot.getEndPosition()
        self.telescope.angle = self.pivot.angle
        self.telescope.update(time_elapsed)
        self.wrist.pos = self.telescope.getEndPosition()
        self.wrist.update(time_elapsed)
        # Update base robot physics (position/velocity/rotation)
        super().update(time_elapsed)

        if self.pieceHeld is not None:
            self.pieceHeld.pos = self.wrist.getEndPosition().rotate(self.theta, Vector3(0, 0, 1)) + Vector3(self.pos.x, self.pos.y, 0)

    # returns 2 positions that represent two vertices of the box of which if a piece is in it would intake
    def getIntakeZone(self):
        endPoint = self.wrist.getEndPosition()
        point1 = endPoint - Vector3(7, 4, 2)
        point2 = endPoint + Vector3(7, 4, 2)
        return point1, point2
    
    
    def moveWithVel(self, targetVel: Vector2):
        super().setTargetVel(targetVel)

    def rotateWrist(self, targetVel):
        self.wrist.setTargetVel(targetVel)
    
    def setTelescopeVel(self, targetVel):
        self.telescope.setTargetVel(targetVel)

    def setPivotVel(self, targetVel):
        self.telescope.setTargetVel(targetVel)