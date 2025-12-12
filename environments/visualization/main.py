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

# robot = PoofsRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([ElevatorSim(robot.elevator), ElevatorSim(robot.laterator)])

# robot = JITBRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([PivotSim(robot.pivot), ElevatorSim(robot.telescope), PivotSim(robot.wrist)])

robot = PoofsRobot(0, 0, 0, 100, 100, (20, 20), Piece(PieceType.CONE, Vector3(20, 20, 20)))
robot2 = JITBRobot(0, 0, 0, 0, 0, (20, 20), Piece(PieceType.CUBE, Vector3(-20, 20, 20)))
sim = SubsystemsSim([ElevatorSim(robot.elevator), ElevatorSim(robot.laterator), PivotSim(robot2.pivot), ElevatorSim(robot2.telescope), PivotSim(robot2.wrist)])

robots = [robot, robot2]

sim.addRobots(robots)


from robotvisualization import RobotPositionVisualizer
visualization = RobotPositionVisualizer([robot])
# visualization.run()
# sim.loop()

env = Environment(robots=robots, startingPieces=[Piece(PieceType.CONE, Vector3(30, 30, 30)), Piece(PieceType.CUBE, Vector3(30, 30, 30))])
print(env.pieces)
viz = EnvironmentVisualizer(env)
viz.run()