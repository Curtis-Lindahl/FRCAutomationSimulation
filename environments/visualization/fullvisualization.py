"""EnvironmentVisualizer: shows Environment robots and game pieces using existing visualizers.

- Center panel: field view with all robots (perimeter outlines) and game pieces.
- Side panel: subsystem demo using SubsystemVisualizer (aggregated Elevators/Pivots from robots or provided list).

Controls:
  Robot controls (delegated to RobotPositionVisualizer):
    Arrows: move current robot (Up = +Y, Down = -Y)
    Q / E : rotate CCW / CW
    TAB / 1-5: switch robot (if robot visualizer is run standalone)

  Subsystems (delegated to SubsystemVisualizer):
    W / S : elevator extend / retract
    A / D : pivot CCW / CW

  Global:
    R     : reset robot poses and subsystem states
    ESC   : quit

Note: Environment.update will advance robot physics and intake checks; Environment.movePieces (if present)
will be called to animate free pieces. This visualizer avoids double-updating robots by delegating motion
commands to RobotPositionVisualizer (target velocities), then calling environment.update(dt) once per frame.
"""

from __future__ import annotations
import os
import sys
import pygame
from pygame import Vector2, Vector3
from typing import Iterable


def _augment_path():
    here = os.path.dirname(__file__)
    env_dir = os.path.dirname(here)
    robots_dir = os.path.join(env_dir, "robots")
    subsystems_dir = os.path.join(robots_dir, "subsystems")
    for p in (env_dir, robots_dir, subsystems_dir):
        if p not in sys.path:
            sys.path.append(p)


_augment_path()
from environments.piece import Piece, PieceType  # type: ignore
from environment import Environment
from environments.visualization.robotvisualization import RobotPositionVisualizer  # type: ignore
from environments.visualization.subsystemvisualization import SubsystemVisualizer  # type: ignore
from constants import FIELD_CONSTANTS
from environments.piece import NodeType
from subsystems.elevator import Elevator
from subsystems.pivot import Pivot


PIECE_COLORS = {
    PieceType.CUBE: (140, 110, 255),
    PieceType.CONE: (255, 210, 80),
    NodeType.CUBE: (140, 110, 255),
    NodeType.CONE: (255, 210, 80),
    NodeType.HYBRID: (0, 0, 0),
}


def world_to_screen(origin_px: Vector2, ppu: float, v: Vector2) -> Vector2:
    return Vector2(origin_px.x + v.x * ppu, origin_px.y - v.y * ppu)


class EnvironmentVisualizer:
    def __init__(self, env: Environment, screen_size=(1280, 1040), pixels_per_unit=3):
        pygame.init()
        pygame.display.set_caption("Environment Visualizer")
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.env = env
        # pixels_per_unit will be computed from the field image if available
        self.ppu = pixels_per_unit

        w, h = screen_size
        # divider for left subsystem panel vs right field panel
        self.divider_x = int(w * 0.35)
        self.divider_y = int(h * 0.73)  # horizontal divider for bottom side-view panel
        self.subsystem_origin = Vector2(int(w * 0.18), int(h * 0.57))
        # Side view (x-z) origin - will be set after field_origin is computed
        self.side_view_origin = Vector2(0, 0)  # placeholder

        # Try to load a field background image and scale it to represent
        # the real field in inches. Robot positions/dimensions are in inches,
        # so we use 324in (width) x 648in (height) as the field extent here.
        self.field_image = None
        self.field_image_rect = None
        field_image_path = os.path.join(os.path.dirname(__file__), "charged-up-field.jpg")
        # field dimensions in inches (width, height)
        field_units_w, field_units_h = 315.5, 651.5
        try:
            if os.path.exists(field_image_path):
                img = pygame.image.load(field_image_path).convert()
                # determine available width in right panel and scale image to fit
                right_width = w - self.divider_x - 20
                desired_field_px_w = int(right_width * 0.95)
                # maintain the field aspect ratio using units (inches)
                desired_field_px_h = int(desired_field_px_w * (field_units_h / field_units_w))
                # If the desired height is too tall for screen, cap by height
                max_field_h = int(h * 0.85)
                if desired_field_px_h > max_field_h:
                    desired_field_px_h = max_field_h
                    desired_field_px_w = int(desired_field_px_h * (field_units_w / field_units_h))

                self.field_image = pygame.transform.smoothscale(img, (desired_field_px_w, desired_field_px_h))
                # compute pixels-per-unit (pixels per inch) based on scaled image width
                self.ppu = desired_field_px_w / field_units_w

                # center field image within right panel horizontally and place it with bottom aligned to ~78% height
                field_left = self.divider_x + (right_width - desired_field_px_w) // 2 + 10
                field_top = int(h * .9) - desired_field_px_h
                self.field_image_rect = pygame.Rect(field_left, field_top, desired_field_px_w, desired_field_px_h)

                # set field origin (world 0,0) to bottom-left of the image
                self.field_origin = Vector2(self.field_image_rect.left, self.field_image_rect.top + self.field_image_rect.height)
                # set side view origin to align with field view (same x, at bottom of side panel)
                self.side_view_origin = Vector2(self.field_origin.x, self.divider_y + int((h - self.divider_y) * 0.95))
            else:
                # fallback origin roughly where the original code placed it
                self.field_origin = Vector2(int(w * 0.60), int(h * 0.78))
                self.side_view_origin = Vector2(self.field_origin.x, self.divider_y + int((h - self.divider_y) * 0.95))
        except Exception:
            print("Field not found")
            self.field_origin = Vector2(int(w * 0.60), int(h * 0.78))
            self.side_view_origin = Vector2(self.field_origin.x, self.divider_y + int((h - self.divider_y) * 0.95))

        # Robot visualizer (reuse; no extra window created because we pass screen)
        self.robot_viz = RobotPositionVisualizer(robots=self.env.robots, screen=self.screen, screen_size=screen_size, pixels_per_unit=self.ppu)

        # Scoring locations helper (attach to environment for programmatic access)
        # expose on environment for other systems/tests
        try:
            self.env.scoring_locations = self.scoring_locations
        except Exception:
            pass

        # Collect subsystems from robots plus any provided extras
        subsystems = list(self._collect_subsystems(self.env.robots))
        self.subsys_viz = SubsystemVisualizer(subsystems=subsystems, origin=self.subsystem_origin, pixels_per_unit=self.ppu)

    # -------------- Helpers --------------
    def _collect_subsystems(self, robots) -> Iterable:
        for r in robots:
            for attr in dir(r):
                if attr.startswith('_'):
                    continue
                try:
                    val = getattr(r, attr)
                except Exception:
                    continue
                if isinstance(val, (Elevator, Pivot)):
                    yield val

    def _iter_pieces(self):
        if isinstance(self.env.pieces, dict):
            return list(self.env.pieces.values())
        return list(self.env.pieces)

    # -------------- Input / Update --------------
    def handle_input(self):
        self.robot_viz.handle_input()
        self.subsys_viz.handle_input()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            for robot in self.env.robots:
                robot.drop()
                if robot.pieceHeld is None:
                    robot.runIntake()

    def update(self, dt: float):
        # Apply motion via env update (robots will consume target velocities from robot_viz input)
        # if hasattr(self.env, 'update'):
        self.env.update(dt)
        # if hasattr(self.env, 'movePieces'):
        #     try:
        #         self.env.movePieces(dt)
        #     except TypeError:
        #         # movePieces might not accept dt; ignore
        #         try:
        #             self.env.movePieces()
        #         except Exception:
        #             pass

    # -------------- Drawing --------------
    def draw_pieces(self):
        """Draw game pieces on the top-down field view (x-y plane)."""
        for piece in self._iter_pieces():
            if not (hasattr(piece, 'pos') and hasattr(piece, 'type')):
                continue
            # Project x-y plane for top-down field view
            try:
                planar = Vector2(piece.pos.x, piece.pos.y)
            except Exception:
                # skip pieces with unexpected position format
                continue
            scr = world_to_screen(self.field_origin, self.ppu, planar)
            
            color = PIECE_COLORS.get(piece.type, (200, 200, 200))

            # Piece size in pixels (scaled appropriately for visibility)
            base_size = 6  # increased for better visibility
            size = max(5, int(base_size))

            # Draw cones as triangles and cubes as squares (screen-space)
            if piece.type == PieceType.CONE:
                # triangle pointing up on screen
                p1 = (int(scr.x), int(scr.y - size))
                p2 = (int(scr.x - size), int(scr.y + size))
                p3 = (int(scr.x + size), int(scr.y + size))
                pygame.draw.polygon(self.screen, color, [p1, p2, p3])
                # Draw outline for better visibility
                pygame.draw.polygon(self.screen, (255, 255, 255), [p1, p2, p3], width=1)
            elif piece.type == PieceType.CUBE:
                s = size
                rect = pygame.Rect(int(scr.x - s), int(scr.y - s), int(2 * s), int(2 * s))
                pygame.draw.rect(self.screen, color, rect)
                # Draw outline for better visibility
                pygame.draw.rect(self.screen, (255, 255, 255), rect, width=1)
            else:
                # fallback to a small circle
                pygame.draw.circle(self.screen, color, (int(scr.x), int(scr.y)), size)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(scr.x), int(scr.y)), size, width=1)

    def draw_divider(self):
        x = int(self.screen.get_width() * 0.35)
        pygame.draw.line(self.screen, (70, 75, 85), (x, 0), (x, self.divider_y), 2)
        # horizontal divider for bottom panel
        pygame.draw.line(self.screen, (70, 75, 85), (0, self.divider_y), (self.screen.get_width(), self.divider_y), 2)

    def draw_subsystems_on_field(self):
        """Draw subsystems (elevators and pivots) on the main field view (x-y plane), rotated with their robot."""
        # Match each subsystem to its robot
        for robot in self.env.robots:
            for subsys in self.subsys_viz.subsystems:
                if not hasattr(subsys, 'pos'):
                    continue
                try:
                    # Find subsystem in robot's attributes
                    belongs_to_robot = False
                    for attr in dir(robot):
                        if not attr.startswith('_'):
                            try:
                                if getattr(robot, attr) is subsys:
                                    belongs_to_robot = True
                                    break
                            except:
                                pass
                    
                    if not belongs_to_robot:
                        continue
                    
                    if isinstance(subsys, Elevator):
                        # Get subsystem position relative to robot
                        local_pos = Vector2(subsys.pos.x, subsys.pos.y) if hasattr(subsys.pos, 'y') else Vector2(subsys.pos.x, 0)
                        # Rotate by robot angle and translate to robot position
                        rotated_pos = local_pos.rotate(robot.theta)
                        world_pos = Vector2(robot.pos.x, robot.pos.y) + rotated_pos
                        base_screen = world_to_screen(self.field_origin, self.ppu, world_pos)
                        
                        # Draw elevator carriage position projected onto field
                        car_dir = Vector2(0, subsys.height).rotate(subsys.angle + robot.theta)
                        car_world = world_pos + car_dir
                        car_screen = world_to_screen(self.field_origin, self.ppu, car_world)
                        
                        # Draw line from base to carriage
                        pygame.draw.line(self.screen, (100, 200, 255), base_screen, car_screen, 3)
                        pygame.draw.circle(self.screen, (100, 200, 255), car_screen, 5)
                    
                    elif isinstance(subsys, Pivot):
                        # Get subsystem position relative to robot
                        local_pos = Vector2(subsys.pos.x, subsys.pos.y) if hasattr(subsys.pos, 'y') else Vector2(subsys.pos.x, 0)
                        # Rotate by robot angle and translate to robot position
                        rotated_pos = local_pos.rotate(robot.theta)
                        world_pos = Vector2(robot.pos.x, robot.pos.y) + rotated_pos
                        base_screen = world_to_screen(self.field_origin, self.ppu, world_pos)
                        
                        # Draw pivot arm rotated with robot
                        arm_dir = Vector2(subsys.length, 0).rotate(subsys.angle + robot.theta)
                        end_world = world_pos + arm_dir
                        end_screen = world_to_screen(self.field_origin, self.ppu, end_world)
                        
                        # Draw line from base to end
                        pygame.draw.line(self.screen, (255, 170, 80), base_screen, end_screen, 4)
                        pygame.draw.circle(self.screen, (255, 170, 80), end_screen, 5)
                except Exception:
                    pass
    
    def draw_intake_zones(self):
        """Draw intake zones for all robots as semi-transparent rectangles."""
        for robot in self.env.robots:
            try:
                if hasattr(robot, 'getIntakeZone'):
                    point1, point2 = robot.getIntakeZone()
                    
                    # Get the bounding box in x-y plane
                    min_x = min(point1.x, point2.x)
                    max_x = max(point1.x, point2.x)
                    min_y = min(point1.y, point2.y)
                    max_y = max(point1.y, point2.y)
                    
                    # Convert to screen coordinates
                    top_left = world_to_screen(self.field_origin, self.ppu, Vector2(min_x, max_y))
                    bottom_right = world_to_screen(self.field_origin, self.ppu, Vector2(max_x, min_y))
                    
                    # Create a semi-transparent surface for the intake zone
                    width = int(abs(bottom_right.x - top_left.x))
                    height = int(abs(bottom_right.y - top_left.y))
                    
                    if width > 0 and height > 0:
                        intake_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                        intake_surface.fill((200, 255, 150, 80))  # Light green, semi-transparent
                        self.screen.blit(intake_surface, (int(min(top_left.x, bottom_right.x)), int(min(top_left.y, bottom_right.y))))
                        
                        # Draw a border around the intake zone
                        rect = pygame.Rect(int(min(top_left.x, bottom_right.x)), int(min(top_left.y, bottom_right.y)), width, height)
                        pygame.draw.rect(self.screen, (100, 200, 100), rect, 2)
            except Exception:
                pass

    def draw_side_view(self):
        """Draw x-z side view of robots and pieces (side profile)."""
        # Draw axis labels
        font = pygame.font.SysFont('consolas', 14)
        label = font.render('Side View (X-Z)', True, (180, 180, 180))
        self.screen.blit(label, (10, self.divider_y + 10))

        # Draw intake zones in side view
        for robot in self.env.robots:
            try:
                if hasattr(robot, 'getIntakeZone'):
                    point1, point2 = robot.getIntakeZone()
                    
                    # Get the bounding box in x-z plane
                    min_x = min(point1.x, point2.x)
                    max_x = max(point1.x, point2.x)
                    min_z = min(point1.z, point2.z)
                    max_z = max(point1.z, point2.z)
                    
                    # Convert to screen coordinates
                    top_left = world_to_screen(self.side_view_origin, self.ppu, Vector2(min_x, max_z))
                    bottom_right = world_to_screen(self.side_view_origin, self.ppu, Vector2(max_x, min_z))
                    
                    # Create a semi-transparent surface for the intake zone
                    width = int(abs(bottom_right.x - top_left.x))
                    height = int(abs(bottom_right.y - top_left.y))
                    
                    if width > 0 and height > 0:
                        intake_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                        intake_surface.fill((200, 255, 150, 80))  # Light green, semi-transparent
                        self.screen.blit(intake_surface, (int(min(top_left.x, bottom_right.x)), int(min(top_left.y, bottom_right.y))))
                        
                        # Draw a border around the intake zone
                        rect = pygame.Rect(int(min(top_left.x, bottom_right.x)), int(min(top_left.y, bottom_right.y)), width, height)
                        pygame.draw.rect(self.screen, (100, 200, 100), rect, 2)
            except Exception:
                pass

        # Draw robots in x-z plane
        for robot in self.env.robots:
            # project x (horizontal) and z (vertical on screen)
            world_xz = Vector2(robot.pos.x, 0)  # z is 0 for ground-level robots
            scr = world_to_screen(self.side_view_origin, self.ppu, world_xz)
            # draw simple rectangle for robot frame width
            w, h_frame = robot.frame if isinstance(robot.frame, (tuple, list)) else (26, 26)
            rect = pygame.Rect(int(scr.x - w/2 * self.ppu), int(scr.y - 10), int(w * self.ppu), 20)
            pygame.draw.rect(self.screen, (90, 110, 150), rect, width=2)

        # Draw pieces in x-z plane
        for piece in self._iter_pieces():
            if not isinstance(piece, Piece):
                continue
            try:
                # x horizontal, z vertical (height off ground)
                world_xz = Vector2(piece.pos.x, piece.pos.z if hasattr(piece.pos, 'z') else 0)
                scr = world_to_screen(self.side_view_origin, self.ppu, world_xz)
                color = PIECE_COLORS.get(piece.type, (200, 200, 200))
                pygame.draw.circle(self.screen, color, (int(scr.x), int(scr.y)), 4)
            except Exception:
                continue

    def draw_hud(self):
        font = pygame.font.SysFont("consolas", 18)
        lines = [
            "Env Viz: ESC quit, R reset",
            f"Robots: {len(self.env.robots)}  Pieces: {len(self._iter_pieces())}",
        ]
        y = 10
        for ln in lines:
            surf = font.render(ln, True, (235, 235, 235))
            self.screen.blit(surf, (10, y))
            y += 20

    def draw(self):
        self.screen.fill((28, 30, 36))
        
        # Draw field background if available (right panel only)
        if self.field_image is not None and self.field_image_rect is not None:
            self.screen.blit(self.field_image, (self.field_image_rect.left, self.field_image_rect.top))

        # Draw scoring nodes
        if hasattr(self, 'scoring_locations'):
            for loc in self.scoring_locations:
                pos = loc[0]
                screen_pos = world_to_screen(self.field_origin, self.ppu, Vector2(pos.x, pos.y) if hasattr(pos, "x") else Vector2(*pos))
                color = PIECE_COLORS.get(loc[1], (00, 0, 0))
                pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), 3)
        
        # Draw pieces and robots on top of the field image
        self.draw_pieces()
        self.draw_intake_zones()
        self.robot_viz.draw(self.screen, origin=self.field_origin, ppu=self.ppu)
        self.draw_subsystems_on_field()

        # Draw divider (separates left and right panels)
        self.draw_divider()

        # Draw subsystems on top (left panel) - drawn last so not covered
        self.subsys_viz.draw(self.screen)

        # Draw side view panel (bottom)
        self.draw_side_view()

        self.draw_hud()
        pygame.display.flip()

    # -------------- Main Loop --------------
    def run(self, dt):
        # dt = .05
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         self.running = False
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_ESCAPE:
        #             self.running = False
        #         elif event.key == pygame.K_r:
        #             self.reset()
        pygame.event.get()

        # self.handle_input()
        self.update(dt)
        self.draw()

    def quit(self):
        pygame.quit()

    # -------------- Reset --------------
    def reset(self):
        for r in self.env.robots:
            r.pos.update(0, 0)
            r.theta = 0
            if hasattr(r, "velocity"):
                r.velocity.update(0, 0)
            if hasattr(r, "dtheta"):
                r.dtheta = 0
            if hasattr(r, "targetVel"):
                r.targetVel.update(0, 0)

        for s in self.subsys_viz.subsystems:
            if isinstance(s, Elevator):
                s.height = 0
                s.dheight = 0
                s.setTargetVel(0)
            elif isinstance(s, Pivot):
                s.angle = 0
                s.turnRate = 0
                s.setTargetVel(0)


def main():
    # Minimal demo environment with no robots and no pieces; plug in your robots/pieces to see them.
    env = Environment(robots=[], startingPieces=[Piece(PieceType.CONE, Vector3(0, 0, 0)), Piece(PieceType.CUBE, Vector3(10, 10, 0))])
    viz = EnvironmentVisualizer(env)
    viz.run()


if __name__ == "__main__":
    main()
