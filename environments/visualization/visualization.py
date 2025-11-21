"""Minimal Pygame simulation templates for visualizing an Elevator or a Pivot.

Run this file directly to launch either simulation:
  python visualization.py elevator   # Elevator only
  python visualization.py pivot      # Pivot only

Controls (Elevator mode):
  W / S : extend / retract (set target velocity)
  R     : reset height
  ESC or window close: quit

Controls (Pivot mode):
  A / D : rotate CCW / CW (set target angular velocity)
  R     : reset angle
  ESC or window close: quit

These templates do NOT instantiate a Robot; they use the existing subsystem classes.
You can later compose them into a robot visualization.
"""

import os
import sys
import math
import pygame
from pygame import Vector2, Vector3
from robots.subsystems.elevator import Elevator
from robots.subsystems.pivot import Pivot

def world_to_screen(origin_px: Vector2, ppu: float, world: Vector2) -> Vector2:
	"""Convert math-style (y up) world coords to Pygame screen (y down)."""
	return Vector2(origin_px.x + world.x * ppu, origin_px.y - world.y * ppu)


class ElevatorSim:
    """Visualizes a single Elevator extending along its mounted angle."""

    def __init__(self, elevator: Elevator, screen_size=(640, 480), pixels_per_unit=4):

        # Elevator mounted at base point with angle 90 deg (pointing up) for intuitive W=extend.
        base_point = Vector3(0, 0, 0)
        self.elevator = elevator
        self.elevator.setTargetVel(0)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        vel = 0
        speed = 200  # units/sec target
        if keys[pygame.K_w]:
            vel += speed
        if keys[pygame.K_s]:
            vel -= speed
        self.elevator.setTargetVel(vel)

    def update(self, dt):
        self.handle_input()
        self.elevator.update(dt)
        # Bound height within [0, maxheight]
        self.elevator.height = max(0, min(self.elevator.height, self.elevator.maxheight))

    def draw(self, origin, ppu, screen):
        # self.screen.fill((25, 28, 34))
        base_world = Vector2(self.elevator.pos.x, self.elevator.pos.y)
        base_screen = world_to_screen(origin, ppu, base_world)

        # Rail (full travel path)
        rail_dir = Vector2(0, self.elevator.maxheight).rotate(self.elevator.angle)
        rail_end_screen = world_to_screen(origin, ppu, base_world + rail_dir)
        pygame.draw.line(screen, (110, 110, 160), base_screen, rail_end_screen, 3)

        # Carriage current position
        carriage_dir = Vector2(0, self.elevator.height).rotate(self.elevator.angle)
        carriage_world = base_world + carriage_dir
        carriage_screen = world_to_screen(origin, ppu, carriage_world)
        pygame.draw.line(screen, (80, 200, 255), base_screen, carriage_screen, 8)
        pygame.draw.circle(screen, (255, 255, 255), base_screen, 6)
        pygame.draw.circle(screen, (80, 200, 255), carriage_screen, 8)

        # HUD
        font = pygame.font.SysFont("consolas", 18)
        lines = [
            f"Height: {self.elevator.height:6.1f} / {self.elevator.maxheight}",
            f"Velocity: {self.elevator.dheight:6.1f} tgt {self.elevator.targetVel:6.1f}",
            f"Angle: {self.elevator.angle:6.1f} deg",  # static here
            "W/S extend/retract, R reset, ESC quit",
        ]
        y = 10
        for ln in lines:
            surf = font.render(ln, True, (230, 230, 230))
            screen.blit(surf, (10, y))
            y += 20

    def reset(self):
        self.elevator.height = 0
        self.elevator.dheight = 0
        self.elevator.setTargetVel(0)


class PivotSim:
    """Visualizes a single Pivot rotating an arm of fixed length."""

    def __init__(self, pivot: Pivot):

        pivot_point = Vector3(0, 0, 0)
        self.pivot = pivot
        self.pivot.setTargetVel(0)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        vel = 0
        speed = 180  # deg/sec
        if keys[pygame.K_a]:
            vel += speed  # CCW
        if keys[pygame.K_d]:
            vel -= speed  # CW
        self.pivot.setTargetVel(vel)

    def update(self, dt):
        self.handle_input()
        self.pivot.update(dt)
        # Clamp angle manually since Pivot.update doesn't enforce min/max
        self.pivot.angle = max(self.pivot.minAngle, min(self.pivot.angle, self.pivot.maxAngle))

    def draw(self, origin, ppu, screen):
        # self.screen.fill((20, 22, 26))
        base_world = Vector2(self.pivot.pos.x, self.pivot.pos.y)
        base_screen = world_to_screen(origin, ppu, base_world)

        # Arm end
        arm_dir = Vector2(self.pivot.length, 0).rotate(self.pivot.angle)
        end_world = base_world + arm_dir
        end_screen = world_to_screen(origin, ppu, end_world)
        pygame.draw.line(screen, (255, 170, 60), base_screen, end_screen, 10)
        pygame.draw.circle(screen, (255, 240, 200), base_screen, 8)
        pygame.draw.circle(screen, (255, 170, 60), end_screen, 10)

        font = pygame.font.SysFont("consolas", 18)
        lines = [
            f"Angle: {self.pivot.angle:7.2f} deg (min {self.pivot.minAngle}, max {self.pivot.maxAngle})",
            f"TurnRate: {self.pivot.turnRate:7.2f} tgt {self.pivot.targetVel:7.2f}",
            "A/D rotate, R reset, ESC quit",
        ]
        y = 10
        for ln in lines:
            surf = font.render(ln, True, (235, 235, 235))
            screen.blit(surf, (10, y))
            y += 20

    def reset(self):
        self.pivot.angle = 0
        self.pivot.turnRate = 0
        self.pivot.setTargetVel(0)


class Sim():

    def __init__(self, simList, screen_size=(640, 480), pixels_per_unit=4):
        pygame.display.set_caption("Pivot Simulation")
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.ppu = pixels_per_unit
        self.origin = Vector2(screen_size[0] // 2, int(screen_size[1] * 0.65))

        self.sims = simList
        self.running = True
        self.clock = pygame.time.Clock()

    def draw(self):
        self.screen.fill((20, 22, 26))
        for sim in reversed(self.sims):
                sim.draw(self.origin, self.ppu, self.screen)

    def loop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_r:
                        self.reset()
            
            for sim in reversed(self.sims):
                sim.update(dt)
            self.draw()

            pygame.display.flip()
        pygame.quit()


def main():
    # Choose mode based on first CLI argument; default elevator.
    pygame.init()
    sim = PivotSim(Pivot(Vector3(0, 0, 0), 50, 50, 0, 150, 200, 400))
    sim2 = ElevatorSim(Elevator(Vector3(0, 0, 0), 100, 200, 500, 0))
    realSim = Sim([sim, sim2])
    realSim.loop()



if __name__ == "__main__":
	main()
