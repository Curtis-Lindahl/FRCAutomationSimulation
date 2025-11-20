from pygame import Vector2, Vector3

class Pivot:
    def __init__(self, pivot_point: Vector3, length, startAngle, minAngle, maxAngle, maxTurnRate, accel, angleOffset:Vector3=Vector3(0,0,0)):
        self.pos = pivot_point
        self.length = length
        self.angle = startAngle
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.maxTurnRate = maxTurnRate
        self.turnRate = 0
        self.angleOffest = angleOffset
        self.targetVel = 0
        self.accel = accel

    def update(self, time_elapsed):
        
        if self.turnRate > self.targetVel:
            self.turnRate -= self.accel * time_elapsed
            if self.turnRate < self.targetVel:
                self.turnRate = self.targetVel

        if self.turnRate < self.targetVel:
            self.turnRate += self.accel * time_elapsed
            if self.turnRate > self.targetVel:
                self.turnRate = self.targetVel

        if self.turnRate < -self.maxTurnRate:
            self.turnRate = -self.maxTurnRate
        if self.turnRate > self.maxTurnRate:
            self.turnRate = self.maxTurnRate

        self.angle += self.turnRate * time_elapsed

    def getEndPosition(self):
        return self.pos.add(Vector3(self.length, 0, 0).rotate(Vector3(self.angle, 0, 0)).rotate(self.angleOffset))
    
    def setTargetVel(self, targetVel):
        self.targetVel = targetVel