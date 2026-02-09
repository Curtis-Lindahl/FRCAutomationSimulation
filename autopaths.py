from pygame import Vector2, Vector3


class Pathfollow:
    def __init__(self, robot):
        self.robot = robot
        self.targetPoints = []
        self.index = 0

    def addPath(self, targetPos, targetRot):
        self.targetPoints.append((targetPos, targetRot))

    def driveToTarget(self):

        target = self.targetPoints[self.index][0]
        rot = self.targetPoints[self.index][1]

        if isinstance(target, Vector3):
            target = Vector2(target.x, target.y)

        delta = target - self.robot.pos

        

        delta *= 1.5
        self.robot.setTargetVel(delta)

        angDelta = rot - self.robot.theta
        angDelta *= 2
        self.robot.setTargetRotSpeed(angDelta)

        if delta.magnitude() < 1.5 and abs(angDelta) < 3:
            self.index += 1

        if self.index == len(self.targetPoints):
            return False
        return True