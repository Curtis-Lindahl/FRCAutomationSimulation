from pathlib import Path
import sys
parent_dir = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)

from pygame import Vector3

from piece import Piece, PieceType
from fullvisualization import EnvironmentVisualizer


from environment import Environment
from subsystemvisualization import SubsystemsSim, ElevatorSim, PivotSim
from robots.robots.poofs import PoofsRobot
from robots.robots.jitb import JITBRobot
from robots.robots.krawler import KrawlerBot
from robots.robots.bread import BreadRobot
from robots.robots.op import OPRobot

# robot = PoofsRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([ElevatorSim(robot.elevator), ElevatorSim(robot.laterator)])

# robot = JITBRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([PivotSim(robot.pivot), ElevatorSim(robot.telescope), PivotSim(robot.wrist)])

poof = PoofsRobot(100, 100, 0, 5000, 200, (28, 28), Piece(PieceType.CONE, Vector3(20, 20, 20)))
jitb = JITBRobot(200, 200, 0, 5000, 170, (26, 26), Piece(PieceType.CUBE, Vector3(-20, 20, 20)))
krawler = KrawlerBot(150, 200, 0, 5000, 200, (25, 25), Piece(PieceType.CONE, Vector3()))
bread = BreadRobot(300, 100, 0, 5000, 220, (30, 30), Piece(PieceType.CONE, Vector3()))
op = OPRobot(400, 200, 0, 5000, 190, (30, 30), Piece(PieceType.CUBE, Vector3()))
# sim = SubsystemsSim([ElevatorSim(robot.elevator), ElevatorSim(robot.laterator), PivotSim(robot2.pivot), ElevatorSim(robot2.telescope), PivotSim(robot2.wrist)])

robots = [jitb, poof, krawler, bread, op]
robots = [poof]

# sim.addRobots(robots)


# robotvisualization is used inside EnvironmentVisualizer; do not instantiate
# a standalone RobotPositionVisualizer here (it was created with a single
# robot and could cause confusion). EnvironmentVisualizer will create its
# own RobotPositionVisualizer bound to the full `robots` list below.

env = Environment(robots=robots, startingPieces=[Piece(PieceType.CONE, Vector3(30, 90, 30)), Piece(PieceType.CUBE, Vector3(40, 30, 30))])
viz = EnvironmentVisualizer(env, screen_size=(1280, 800))
viz.run()