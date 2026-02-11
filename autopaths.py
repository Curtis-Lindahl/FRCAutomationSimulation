from pygame import Vector2, Vector3

from environments.piece import PieceType

class Pathfollow:
    def __init__(self, robot, env):
        self.env = env
        self.robot = robot
        self.commands = []
        self.index = 0

    def addPath(self, targetPos, targetRot):
        self.commands.append((targetPos, targetRot))

    def addMoveArm(self, height, dist):
        self.commands.append((dist, height))

    def addDrop(self, time):
        self.commands.append((None, time))
        self.dropTime = 0

    def changePiece(self, newPiece):
        self.commands.append((newPiece, None))

    def runCommand(self):
        if isinstance(self.commands[self.index][0], Vector3) or isinstance(self.commands[self.index][0], Vector2):
            self.driveToTarget()

        elif isinstance(self.commands[self.index][0], float):
            self.moveArm()

        elif self.commands[self.index][0] is None:
            self.drop()

        elif isinstance(self.commands[self.index][0], PieceType):
            self.changePieceType()

        if self.index == len(self.commands):
            return False
        return True

    def driveToTarget(self):

        target = self.commands[self.index][0]
        rot = self.commands[self.index][1]

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

        if self.index == len(self.commands):
            return False
        return True
    
    def moveArm(self):
        self.robot.elevator.height = self.commands[self.index][1]
        self.robot.laterator.height = self.commands[self.index][0]

        self.index += 1

    def drop(self):
        self.robot.drop()
        self.dropTime += 1
        if self.dropTime > self.commands[self.index][1]:
            self.index += 1
            self.robot.runIntake()

    def changePieceType(self):
        self.env.pieceToAdd = self.commands[self.index][0]
        self.index += 1