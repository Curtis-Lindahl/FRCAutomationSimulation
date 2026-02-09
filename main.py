from pathlib import Path
import sys

from autopaths import Pathfollow
parent_dir = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)

from pygame import Vector2, Vector3

from environments.piece import Piece, PieceType
from environments.visualization.fullvisualization import EnvironmentVisualizer


from environments.environment import Environment
from environments.robots.robots.poofs import PoofsRobot
from environments.robots.robots.jitb import JITBRobot
from environments.robots.robots.krawler import KrawlerBot
from environments.robots.robots.bread import BreadRobot
from environments.robots.robots.op import OPRobot

import time

import constants

# robot = PoofsRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([ElevatorSim(robot.elevator), ElevatorSim(robot.laterator)])

# robot = JITBRobot(0, 0, 0, 0, 0, (20, 20))
# sim = Sim([PivotSim(robot.pivot), ElevatorSim(robot.telescope), PivotSim(robot.wrist)])

def run():
    startTime = time.time()
    while pathing.driveToTarget():
        viz.run()
    print("Final Time:", time.time() - startTime)

    viz.quit()

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

env = Environment(robots=robots, startingPieces=[Piece(PieceType.CONE, Vector3(20.5, 14.25, 46)), Piece(PieceType.CUBE, Vector3(40, 30, 30))])
viz = EnvironmentVisualizer(env, screen_size=(1280, 800))


pathing = Pathfollow(robots[0])
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[8][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[7][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[6][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[5][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[4][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[3][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[2][0].x, 70), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[1][0].x, 70), 0)
pathing.addPath(Vector2(100, 250), 0)
pathing.addPath(constants.pickupSpot(constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT), 180)
pathing.addPath(Vector2(constants.FIELD_CONSTANTS.SCORING_LOCATIONS[0][0].x, 70), 0)
run()