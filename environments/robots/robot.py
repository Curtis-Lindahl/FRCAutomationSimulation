from pathlib import Path
import sys
parent_dir = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)
from pygame import Vector2

from piece import Piece

class Robot:

    def __init__(self, x, y, theta, maxaccel, maxvel, frame_size: tuple, piece: Piece):
        self.pos = Vector2(x, y)
        self.theta = theta
        self.velocity = Vector2(0, 0)
        self.dtheta = 0
        self.maxaccel = maxaccel
        self.maxvel = maxvel
        self.frame = frame_size
        self.targetVel = Vector2(0, 0)
        self.pieceHeld = piece
        self.intaking = False

    def update(self, time_elapsed):

        delta = self.targetVel - self.velocity
        if delta.length() == 0:
            accel = Vector2(0, 0)
        else:
            accel = delta.normalize() * self.maxaccel

        step = accel * time_elapsed

        if step.length() >= delta.length():
            self.velocity = Vector2(self.targetVel)
        else:
            self.velocity += step

        # integrate position and rotation
        self.pos.x += self.velocity.x * time_elapsed
        self.pos.y += self.velocity.y * time_elapsed
        self.theta += self.dtheta * time_elapsed

    def setTargetVel(self, targetVel: Vector2):
        self.targetVel = Vector2(targetVel)
        if self.targetVel.length() > self.maxvel:
            self.targetVel = self.targetVel.normalize() * self.maxvel

    def setTargetRotSpeed(self, targetVel):
        self.dtheta = targetVel

    def canIntake(self, piece: Piece):
        point1, point2 = self.getIntakeZone()
        min_x, max_x = sorted((point1.x, point2.x))
        min_y, max_y = sorted((point1.y, point2.y))
        min_z, max_z = sorted((point1.z, point2.z))
        # use inclusive bounds: min <= coord <= max
        return (min_x <= piece.pos.x <= max_x and
                min_y <= piece.pos.y <= max_y and
                min_z <= piece.pos.z <= max_z)
    
    def intake(self, piece: Piece):
        if self.pieceHeld is not None:
            return False
        if piece.scored:
            return False
        if self.canIntake(piece):
            self.pieceHeld = piece
            self.intaking = False
            return True
        return False
    
    def drop(self):
        self.pieceHeld = None
    
    def runIntake(self):
        self.intaking = True