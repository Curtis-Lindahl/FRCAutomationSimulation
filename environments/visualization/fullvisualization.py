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
from piece import Piece, PieceType  # type: ignore
from environment import Environment
from elevator import Elevator  # type: ignore
from pivot import Pivot  # type: ignore
from robotvisualization import RobotPositionVisualizer  # type: ignore
from subsystemvisualization import SubsystemVisualizer  # type: ignore


PIECE_COLORS = {
    PieceType.CUBE: (140, 110, 255),
    PieceType.CONE: (255, 210, 80),
}


def world_to_screen(origin_px: Vector2, ppu: float, v: Vector2) -> Vector2:
    return Vector2(origin_px.x + v.x * ppu, origin_px.y - v.y * ppu)


class EnvironmentVisualizer:
    def __init__(self, env: Environment, screen_size=(1280, 760), pixels_per_unit=3):
        pygame.init()
        pygame.display.set_caption("Environment Visualizer")
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.env = env
        self.ppu = pixels_per_unit

        w, h = screen_size
        self.field_origin = Vector2(int(w * 0.60), int(h * 0.78))
        self.subsystem_origin = Vector2(int(w * 0.18), int(h * 0.78))

        # Robot visualizer (reuse; no extra window created because we pass screen)
        self.robot_viz = RobotPositionVisualizer(robots=self.env.robots, screen=self.screen, screen_size=screen_size, pixels_per_unit=self.ppu)

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

    def update(self, dt: float):
        # Apply motion via env update (robots will consume target velocities from robot_viz input)
        if hasattr(self.env, 'update'):
            self.env.update(dt)
        if hasattr(self.env, 'movePieces'):
            try:
                self.env.movePieces(dt)
            except TypeError:
                # movePieces might not accept dt; ignore
                try:
                    self.env.movePieces()
                except Exception:
                    pass

    # -------------- Drawing --------------
    def draw_pieces(self):
        for piece in self._iter_pieces():
            if not isinstance(piece, Piece):
                continue
            # Project x,z plane for field
            try:
                planar = Vector2(piece.pos.x, piece.pos.y)
            except Exception:
                # skip pieces with unexpected position format
                continue
            scr = world_to_screen(self.field_origin, self.ppu, planar)
            color = PIECE_COLORS.get(piece.type, (200, 200, 200))

            # Fixed visual size (prevents expansion over time). Use a base size
            # in pixels; scale slightly by ppu if user wants larger visuals.
            base_size = 10
            size = max(4, int(base_size))

            # Draw cones as triangles and cubes as squares (screen-space)
            if piece.type == PieceType.CONE:
                # triangle pointing up on screen
                p1 = (int(scr.x), int(scr.y - size))
                p2 = (int(scr.x - size), int(scr.y + size))
                p3 = (int(scr.x + size), int(scr.y + size))
                pygame.draw.polygon(self.screen, color, [p1, p2, p3])
            elif piece.type == PieceType.CUBE:
                s = size
                rect = pygame.Rect(int(scr.x - s), int(scr.y - s), int(2 * s), int(2 * s))
                pygame.draw.rect(self.screen, color, rect)
            else:
                # fallback to a small circle
                pygame.draw.circle(self.screen, color, (int(scr.x), int(scr.y)), size)

    def draw_divider(self):
        x = int(self.screen.get_width() * 0.35)
        pygame.draw.line(self.screen, (70, 75, 85), (x, 0), (x, self.screen.get_height()), 2)

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
        self.draw_divider()
        self.subsys_viz.draw(self.screen)
        self.draw_pieces()
        self.robot_viz.draw(self.screen, origin=self.field_origin, ppu=self.ppu)
        self.draw_hud()
        pygame.display.flip()

    # -------------- Main Loop --------------
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
            self.draw()

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
    print(env.pieces)
    viz = EnvironmentVisualizer(env)
    viz.run()


if __name__ == "__main__":
    main()
