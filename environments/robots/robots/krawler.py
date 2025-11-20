import robot
from subsystems.pivot import Pivot
from subsystems.elevator import Elevator
from pygame import Vector2, Vector3

class KrawlerBot(robot.Robot):
    
    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size):
        super().__init__(x, y, theta, maxaccel, maxvel, frame_size)
        self.elevator = Elevator(Vector3(0, -3, 8), 75, 50, 75, 55)
        self.wrist = Pivot(self.elevator.getEndPosition() + Vector3(0, 5, 0), 6, 90, -45, 90, 180, 180)

    def update(self, time_elapsed):
        super().update(time_elapsed)
        self.elevator.update(time_elapsed)
        self.wrist.update(time_elapsed)

    def getIntakeZone(self):
        endPoint = self.wrist.getEndPosition()
        point1 = endPoint - Vector3(5, 7, 2)
        point2 = endPoint + Vector3(5, 7, 2)
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
    
    def setElevatorVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)

    def setWristVel(self, targetVel):
        self.elevator.setTargetVel(targetVel)