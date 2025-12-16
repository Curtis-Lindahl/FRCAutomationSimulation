"""Combined visualization: Robot position (center) + separate subsystem demos (side).

- Center: draw robot frame outline (perimeter square/rectangle), using existing Robot class.
- Side: draw standalone Elevator and Pivot using existing subsystem classes, controlled by keys.

Controls:
    Robot (center)
		Arrows : move (Up = +Y, Down = -Y)
		Q / E  : rotate CCW / CW

    Subsystems (left side)
		W / S  : Elevator extend / retract
		A / D  : Pivot CCW / CW

    Global
		R      : Reset all
		ESC    : Quit
"""

from __future__ import annotations
import os
import sys
import pygame
from pygame import Vector2, Vector3


def _add_paths_for_imports():
	"""Make sure we can import robot, elevator, and pivot from the project layout."""
	here = os.path.dirname(__file__)  # .../environments/visualization
	env_dir = os.path.dirname(here)   # .../environments
	robots_dir = os.path.join(env_dir, "robots")
	subsystems_dir = os.path.join(robots_dir, "subsystems")
	for p in (robots_dir, subsystems_dir):
		if p not in sys.path:
			sys.path.append(p)


_add_paths_for_imports()
from elevator import Elevator  # type: ignore
from pivot import Pivot  # type: ignore
from robotvisualization import RobotPositionVisualizer  # relative import within visualization pkg
from subsystemvisualization import SubsystemVisualizer


def world_to_screen(origin_px: Vector2, ppu: float, v: Vector2) -> Vector2:
	"""Map math-style (y up) coords to screen (y down)."""
	return Vector2(origin_px.x + v.x * ppu, origin_px.y - v.y * ppu)


class CombinedVisualizer:
	def __init__(self, subsystems, robots, screen_size=(1200, 720), pixels_per_unit=4):
		pygame.init()
		pygame.display.set_caption("Robot + Subsystems Visualization")
		self.screen = pygame.display.set_mode(screen_size)
		self.clock = pygame.time.Clock()
		self.running = True
		self.ppu = pixels_per_unit

		w, h = screen_size
		# Layout: left panel for subsystems, center for robot
		self.side_origin = Vector2(int(w * 0.18), int(h * 0.78))
		self.center_origin = Vector2(int(w * 0.60), int(h * 0.75))

		# Robot visualizer (reuse RobotPositionVisualizer for drawing and input)
		self.robot_viz = RobotPositionVisualizer(robots)

		# Subsystems visualizer (reuse SubsystemVisualizer)
		self.subsystems_viz = SubsystemVisualizer(subsystems=subsystems, origin=self.side_origin, pixels_per_unit=self.ppu)

	# ---------------- Input ----------------
	def handle_input(self):
		self.robot_viz.handle_input()
		self.subsystems_viz.handle_input()

	# ---------------- Update --------------
	def update(self, dt: float):
		# Update robot and subsystems via their visualizers
		self.robot_viz.update(dt)
		self.subsystems_viz.update(dt)

	# ---------------- Drawing -------------
	def draw_robot(self):
		# Delegate drawing to the robot visualizer (perimeter only)
		self.robot_viz.draw(self.screen, origin=self.center_origin, ppu=self.ppu)

	def draw_subsystems_panel(self):
		# Delegate drawing to the subsystem visualizer
		self.subsystems_viz.draw(self.screen)

	def draw_center_hud(self):
		font = pygame.font.SysFont("consolas", 18)
		# Current robot info from visualizer
		if self.robot_viz.robots and self.robot_viz.current_index >= 0:
			rob = self.robot_viz.robots[self.robot_viz.current_index]
			pos_line = f"Pos=({rob.pos.x:.1f}, {rob.pos.y:.1f}) theta={rob.theta:.1f}"
		else:
			pos_line = "No robots loaded"
		lines = [
			"Robot (center): Arrows move, Q/E rotate, R reset, ESC quit",
			pos_line,
		]
		w = self.screen.get_width()
		x = int(w * 0.38)
		y = 10
		for ln in lines:
			surf = font.render(ln, True, (235, 235, 235))
			self.screen.blit(surf, (x, y))
			y += 20

	# ---------------- Main Loop -----------
	def run(self):
		while self.running:
			dt = self.clock.tick(60) / 1000.0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.running = False
					elif event.key == pygame.K_r:
						self.reset()

			self.handle_input()
			self.update(dt)

			self.screen.fill((28, 30, 36))
			# Vertical divider between panels
			pygame.draw.line(self.screen, (70, 75, 85), (int(self.screen.get_width()*0.35), 0),
							(int(self.screen.get_width()*0.35), self.screen.get_height()), 2)

			self.draw_subsystems_panel()
			self.draw_robot()
			self.draw_center_hud()
			pygame.display.flip()

		pygame.quit()

	# ---------------- Utilities -----------
	def reset(self):
		# Reset robot via RobotPositionVisualizer defaults
		for r in self.robot_viz.robots:
			r.pos.update(0, 0)
			r.theta = 0
			r.velocity.update(0, 0)
			r.dtheta = 0
			r.targetVel.update(0, 0)

		# Reset subsystems (iterate through visualizer list)
		for s in self.subsystems_viz.subsystems:
			if isinstance(s, Elevator):
				s.height = 0
				s.dheight = 0
				s.setTargetVel(0)
			elif isinstance(s, Pivot):
				s.angle = 0
				s.turnRate = 0
				s.setTargetVel(0)


from robots.robot import Robot
def main():
	elevator = Elevator(low_pos=Vector3(-20, 0, 0), maxheight=120, maxVel=160, maxAccel=300, mountedAngle=90)
	elevator.setTargetVel(0)
	pivot = Pivot(pivot_point=Vector3(30, 0, 0), length=90, startAngle=0, minAngle=-180, maxAngle=180, maxTurnRate=240, accel=480)
	pivot.setTargetVel(0)
	robots = Robot(24, 24, 24, 24, 24, [24, 24])
	robot2 = Robot(28, 28, 28, 28, 28, [28, 28])
	viz = CombinedVisualizer([elevator, pivot], [robots, robot2])
	viz.run()


if __name__ == "__main__":
	main()

