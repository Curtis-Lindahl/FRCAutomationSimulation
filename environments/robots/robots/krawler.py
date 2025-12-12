import robot
from subsystems.pivot import Pivot
from subsystems.elevator import Elevator
from pygame import Vector2, Vector3
from piece import Piece

class KrawlerBot(robot.Robot):
    
    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size, piece):
        super().__init__(x, y, theta, maxaccel, maxvel, frame_size, piece)
        self.elevator = Elevator(Vector3(0, -3, 8), 75, 50, 75, 55)
        self.wrist = Pivot(self.elevator.getEndPosition() + Vector3(0, 5, 0), 6, 90, -45, 90, 180, 180)

    def update(self, time_elapsed):
        super().update(time_elapsed)
        self.elevator.update(time_elapsed)
        self.wrist.update(time_elapsed)
        if super().pieceHeld is not None:
            super().pieceHeld.pos = self.wrist.getEndPosition() + Vector3(super().pos.x, super().pos.y, 0)

    def getIntakeZone(self):
        endPoint = self.wrist.getEndPosition()
        point1 = endPoint - Vector3(5, 7, 2)
        point2 = endPoint + Vector3(5, 7, 2)
        return point1, point2
    
    
    def setElevatorVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)

    def setWristVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)