"""Robot position visualization using existing Robot subclasses and subsystem variables.

This provides a `RobotPositionVisualizer` class that can:
  * Render any Robot subclass (frame rectangle, orientation) from `environments/robots/robots/*`.
  * Auto-detect attached subsystem instances (Elevator, Pivot) by introspecting attributes.
  * Draw each subsystem with distinct colors and show endpoints.
  * Basic keyboard control of currently selected robot (translation + rotation).
  * Cycle between robots with number keys 1-5 if available.

Controls:
  Arrow Keys : Move current robot (X/Y)  (Up increases Y; Down decreases Y)
  Q / E      : Rotate robot CCW / CW
  TAB        : Cycle to next robot
  1..5       : Jump to specific robot index
  R          : Reset all robots to origin
  SPACE      : Toggle drawing of subsystem endpoints only vs full arms/rails
  ESC / Close: Quit

You can import and embed `RobotPositionVisualizer` elsewhere or run this file directly.
"""

from __future__ import annotations
import math
import pygame
from pygame import Vector2, Vector3
from pathlib import Path
import sys
parent_dir = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)
from robots.robot import Robot


def world_to_screen(origin_px: Vector2, ppu: float, world: Vector2) -> Vector2:
	"""Convert math-style y-up coordinates to Pygame y-down screen coordinates."""
	return Vector2(origin_px.x + world.x * ppu, origin_px.y - world.y * ppu)


class RobotPositionVisualizer:
    """Visualize positions and subsystem geometry for multiple robots."""

    FRAME_COLOR = (90, 110, 150)
    SUBSYSTEM_COLORS = {
        'Elevator': (80, 200, 255),
        'Pivot': (255, 170, 60),
    }

    def __init__(self, robots: list[Robot] | None = None, screen=None, screen_size=(1050, 700), pixels_per_unit=4):
        # If an external screen is provided (embedding), reuse it to avoid resetting display.
        if screen is None:
            pygame.init()
            pygame.display.set_caption("Robot Position Visualizer")
            self.screen = pygame.display.set_mode(screen_size)
        else:
            self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.ppu = pixels_per_unit
        self.origin = Vector2(screen_size[0] // 2, int(screen_size[1] * 0.75))
        self.draw_full_subsystems = True
		
        self.robots = robots

        self.current_index = 0 if self.robots else -1

	# ----------------------------- Input & Update -----------------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.current_index < 0:
            return
        # Apply the same input targets to all robots so they move together.
        move_speed = 180
        target_vel = Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            target_vel.x -= move_speed
        if keys[pygame.K_RIGHT]:
            target_vel.x += move_speed
        if keys[pygame.K_UP]:
            target_vel.y += move_speed
        if keys[pygame.K_DOWN]:
            target_vel.y -= move_speed

        for robot in self.robots:
            robot.setTargetVel(target_vel)

        rot_speed = 120
        if keys[pygame.K_q]:
            for robot in self.robots:
                robot.setTargetRotSpeed(rot_speed)
        elif keys[pygame.K_e]:
            for robot in self.robots:
                robot.setTargetRotSpeed(-rot_speed)
        else:
            for robot in self.robots:
                robot.setTargetRotSpeed(0)

    def update(self, dt: float):
        for robot in self.robots:
            # Subsystems may need manual positional chaining (already handled in subclass update logic)
            robot.update(dt)

    # ----------------------------- Drawing Helpers ----------------------------
    def draw_robot_frame(self, robot: Robot):
        base_world = Vector2(robot.pos.x, robot.pos.y)
        base_screen = world_to_screen(self.origin, self.ppu, base_world)
        w, h = robot.frame if isinstance(robot.frame, (tuple, list)) else (26, 26)
        w2 = w / 2
        h2 = h / 2
        # Corners pre-rotation (y up coord system)
        corners = [Vector2(-w2, -h2), Vector2(w2, -h2), Vector2(w2, h2), Vector2(-w2, h2)]
        # Rotate by theta (degrees) then translate
        rotated = [world_to_screen(self.origin, self.ppu, base_world + c.rotate(robot.theta)) for c in corners]
        pygame.draw.polygon(self.screen, self.FRAME_COLOR, rotated, width=2)
        pygame.draw.circle(self.screen, (255, 255, 255), base_screen, 4)

    def draw_robot(self, robot: Robot, index: int):
        self.draw_robot_frame(robot)

        # Label
        font = pygame.font.SysFont('consolas', 16)
        label = f"{index}:{robot.__class__.__name__}" + (" *" if index == self.current_index else "")
        base_world = Vector2(robot.pos.x, robot.pos.y)
        base_screen = world_to_screen(self.origin, self.ppu, base_world)
        text_surf = font.render(label, True, (230, 230, 230))
        self.screen.blit(text_surf, (base_screen.x + 10, base_screen.y - 10))

    def draw_hud(self):
        font = pygame.font.SysFont('consolas', 18)
        lines = [
            f"Robots: {len(self.robots)} | Current index: {self.current_index}",
            "Controls: Arrows move, Q/E rotate, TAB/1-5 switch, SPACE toggle detail, R reset, ESC quit",
        ]
        y = 10
        for ln in lines:
            surf = font.render(ln, True, (235, 235, 235))
            self.screen.blit(surf, (10, y))
            y += 22

    # ----------------------------- State Ops ---------------------------------
    def reset(self):
        for r in self.robots:
            r.pos.x = 0
            r.pos.y = 0
            r.theta = 0

    def cycle_robot(self):
        if not self.robots:
            return
        self.current_index = (self.current_index + 1) % len(self.robots)

    def select_robot(self, idx: int):
        if 0 <= idx < len(self.robots):
            self.current_index = idx

    # ----------------------------- Main Loop ---------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_TAB:
                        self.cycle_robot()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_SPACE:
                        self.draw_full_subsystems = not self.draw_full_subsystems
                    elif pygame.K_1 <= event.key <= pygame.K_5:
                        # Map key code to index 0..4
                        idx = event.key - pygame.K_1
                        self.select_robot(idx)

            self.handle_input()
            self.update(dt)

            self.screen.fill((30, 32, 38))
            for i, r in enumerate(self.robots):
                self.draw_robot(r, i)
                print(i)
            self.draw_hud()
            pygame.display.flip()
        pygame.quit()

    # Convenience API for embedding in other visualizations
    def draw(self, screen: pygame.Surface, origin: Vector2, ppu: float):
        """Draw all robots (perimeter only) at provided origin and scale."""
        if not self.robots:
            return
        for robot in self.robots:
            base_world = Vector2(robot.pos.x, robot.pos.y)
            w, h = robot.frame if isinstance(robot.frame, (tuple, list)) else (26, 26)
            w2, h2 = w / 2, h / 2
            corners = [Vector2(-w2, -h2), Vector2(w2, -h2), Vector2(w2, h2), Vector2(-w2, h2)]
            rotated = [base_world + c.rotate(robot.theta) for c in corners]
            pts = [Vector2(origin.x + p.x * ppu, origin.y - p.y * ppu) for p in rotated]
            pygame.draw.polygon(screen, (90, 110, 150), pts, width=2)
            front = base_world + Vector2(w2, 0).rotate(robot.theta)
            pygame.draw.line(screen, (255, 255, 255), Vector2(origin.x + base_world.x * ppu, origin.y - base_world.y * ppu),
                            Vector2(origin.x + front.x * ppu, origin.y - front.y * ppu), 2)


def main():
	viz = RobotPositionVisualizer()
	viz.run()


if __name__ == '__main__':
	main()

