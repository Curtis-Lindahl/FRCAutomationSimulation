from pygame import Vector2, Vector3

class Elevator:
    def __init__(self, low_pos: Vector3, maxheight, maxVel, maxAccel, mountedAngle):
        self.pos = low_pos
        self.height = 0
        self.maxheight = maxheight
        self.dheight = 0
        self.maxVel = maxVel
        self.accel = maxAccel
        self.angle = mountedAngle
        self.targetVel = 0

    def update(self, time_elapsed):

        if self.dheight > self.targetVel:
            self.dheight -= self.accel * time_elapsed
            if self.dheight < self.targetVel:
                self.dheight = self.targetVel

        if self.dheight < self.targetVel:
            self.dheight += self.accel * time_elapsed
            if self.dheight > self.targetVel:
                self.dheight = self.targetVel

        if self.dheight < -self.maxVel:
            self.dheight = -self.maxVel
        if self.dheight > self.maxVel:
            self.dheight = self.maxVel


        self.height += self.dheight * time_elapsed

    def getEndPosition(self) -> Vector3:
        return Vector2(0, self.height).rotate(self.angle)
    
    def setTargetVel(self, targetVel):
        self.targetVel = targetVel