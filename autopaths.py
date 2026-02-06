from pygame import Vector2


class Pathfollow:
    def __init__(self, robot):
        self.robot = robot

    def driveToTarget(self, target):
        delta = target - self.robot.pos

        self.robot.targetVel = delta.scale_to_length(self.robot.maxvel)