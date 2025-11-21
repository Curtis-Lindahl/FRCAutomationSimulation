from pygame import Vector2

class Robot:

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size: tuple):
        self.pos = Vector2(x, y)
        self.theta = theta
        self.velocity = Vector2(0, 0)
        self.dtheta = 0
        self.ddtheta = 0
        self.maxaccel = maxaccel
        self.maxvel = maxvel
        self.frame = frame_size
        self.hasPiece = True
        self.targetVel = Vector2(0, 0)

    def update(self, time_elapsed):

        if self.velocity.x > self.targetVel.x:
            self.velocity.x -= self.maxaccel.x * time_elapsed
            if self.velocity.x < self.targetVel.x:
                self.velocity.x = self.targetVel.x

        if self.velocity.x < self.targetVel.x:
            self.velocity.x += self.maxaccel.x * time_elapsed
            if self.velocity.x > self.targetVel.x:
                self.velocity.x = self.targetVel.x

        if self.velocity.y > self.targetVel.y:
            self.velocity.y -= self.maxaccel.y * time_elapsed
            if self.velocity.y < self.targetVel.y:
                self.velocity.y = self.targetVel.y

        if self.velocity.y < self.targetVel.y:
            self.velocity.y += self.maxaccel.y * time_elapsed
            if self.velocity.y > self.targetVel.y:
                self.velocity.y = self.targetVel.y

        self.pos.x += self.velocity.x * time_elapsed
        self.pos.y += self.velocity.y * time_elapsed
        self.theta += self.dtheta * time_elapsed

    def setTargetVel(self, targetVel: Vector2):
        self.targetVel = targetVel
        if targetVel.magnitude() > self.maxvel:
            self.targetVel = self.targetVel.normalize() * self.maxvel

    def setTargetRotSpeed(self, targetVel):
        self.dtheta = targetVel