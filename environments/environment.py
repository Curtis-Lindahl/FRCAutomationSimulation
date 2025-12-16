# nuttpmamous natvogtion
# algerithm

import sys, pathlib
parent_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)
from enum import Enum
from pygame import Vector3
from constants import FIELD_CONSTANTS
import constants

class MatchMode(Enum):
        AUTO = 0
        TELEOP = 1
        DISABLED = 2

class Environment:

    def __init__(self, robots, startingPieces):
        self.robots = robots
        self.pieces = startingPieces
        for robot in robots:
            self.pieces.append(robot.pieceHeld)
        # expose scoring locations from constants on the environment
        try:
            self.scoring_locations = FIELD_CONSTANTS.SCORING_LOCATIONS
        except Exception:
            self.scoring_locations = []
        self.timeRemaining = 0
        self.scoring = ScoringManager()
        self.mode = MatchMode.DISABLED

    def endAuto(self):
        self.scoring.updateEndOfAuto()
        self.initTeleop()

    def startMatch(self):
        self.timeRemaining = 15
        self.mode = MatchMode.AUTO

    def initTeleop(self):
        self.timeRemaining = 135
        self.mode = MatchMode.TELEOP

    def endMatch(self):
        self.mode = MatchMode.DISABLED
        
    def flipPoint(self, point: Vector3):
        return Vector3(point.x, constants.FIELD_HEIGHT - point.y, point.z)

    def update(self, time_elapsed):
        for robot in self.robots:
            robot.update(time_elapsed)
            self.checkIntake(robot)

    def checkIntake(self, robot):
        if robot.intaking:
            for piece in self.pieces:
                robot.intake(piece)

    def movePieces(self, time_elapsed):
        for piece in self.pieces:
            shouldreturn = False
            if self.pieceOnRobot(piece):
                return
            
            piece.pos.x += piece.vel.x * time_elapsed
            piece.pos.y = piece.vel.y * time_elapsed
            piece.pos.z += max(piece.pos.z - piece.vel.z * time_elapsed, 0)

            if piece.pos.z != 0:
                piece.vel.z -= 9.8 * time_elapsed
            else:
                piece.vel = Vector3(0, 0, 0)

    def checkScoring(self, piece):
        for scoringNodeIndex in len(constants.FIELD_CONSTANTS.SCORING_LOCATIONS):
            if piece.pos: # idk just if it's right
                self.grid[scoringNodeIndex // 3][scoringNodeIndex % 3] += 1
            
    def pieceOnRobot(self, piece):
        for robot in self.robots:
            if robot.pieceHeld == piece:
                return True
        return False

class ScoringManager:

    def __init__(self):
        self.score = {"Red": 0, "Blue": 0}
        self.grid = {"Red": [[0, 0, 0, 0, 0, 0, 0, 0, 0], # top row
                            [0, 0, 0, 0, 0, 0, 0, 0, 0], # middle row
                            [0, 0, 0, 0, 0, 0, 0, 0, 0]], # bottom row
                    "Blue": [[0, 0, 0, 0, 0, 0, 0, 0, 0], # top row
                            [0, 0, 0, 0, 0, 0, 0, 0, 0], # middle row
                            [0, 0, 0, 0, 0, 0, 0, 0, 0]]} # bottom row
        self.chargeStationScore = {"Red": [0, 0], "Blue": [0, 0]} # first value is auto, second is endgame
        self.autoScores = {"Red":  {"Leaves":  (False, False, False), "PiecesScoredBonus": 0, "chargeStationScore": 0}, 
                                            "Blue":  {"Leaves":  (False, False, False), "PiecesScoredBonus": 0, "chargeStationScore": 0}}
        
    def updateEndOfAuto(self, evnironment: Environment):
        for robot in evnironment.robots:
            if robot.pos > FIELD_CONSTANTS.chargeStationBottomLeft and robot.pos < FIELD_CONSTANTS.chargeStationTopRights:
                if evnironment.robots.indexof(robot) < 3:
                    self.autoScores["Red"]["chargeStationScore"] = 8
                else:
                    self.autoScores["Blue"]["chargeStationScore"] = 12
            if robot.pos > FIELD_CONSTANTS.chargeStationBalancedBottomLeft and robot.pos < FIELD_CONSTANTS.chargeStationBalancedTopRight:
                if evnironment.robots.indexof(robot) < 3:
                    self.autoScores["Red"]["chargeStationScore"] = 6
                else:
                    self.autoScores["Blue"]["chargeStationScore"] = 10

    def getScore(self):
        newScore = {"Red": 0, "Blue": 0}
        newScore["Red"] += sum(self.chargeStationScore["Red"])
        newScore["Blue"] += sum(self.chargeStationScore["Blue"])

    def calculateGridScore(self):
        score = {"Red": 0, "Blue": 0}
        for level in [0, 1, 2]:
            pointValue = 4-level
            if level == 0:
                pointValue = 5

            for alliance in ["Red", "Blue"]:
                for node in self.grid[alliance][level]:
                    if node > 0:
                        score[alliance] += pointValue
        
        links = self.calculateLinks()
        score["Red"] += 5 * links["Red"]
        score["Blue"] += 5 * links["Blue"]

        for alliance in ["Red", "Blue"]:
            if links[alliance] == 9:
                for row in self.grid[alliance]:
                    for node in row:
                        if node > 1:
                            score[alliance] += 3

    def calculateLinks(self):
        links = {"Red": 0, "Blue": 0}
        for alliance in ["Red", "Blue"]:
            for level in [0, 1, 2]:
                used = [False] * 9
                for i in range(7):
                    if (self.grid[alliance][level][i] > 0 and 
                    self.grid[alliance][level][i+1] > 0 and 
                    self.grid[alliance][level][i+2] > 0 and
                    not any(used[i:i+3])):
                        links[alliance] += 1
                    used[i:i+3] = [True, True, True]
        return links