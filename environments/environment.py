# nuttpmamous natvogtion
# algerithm

import sys, pathlib
parent_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, parent_dir)
from enum import Enum
from pygame import Vector3
from constants import FIELD_CONSTANTS
import constants
from piece import NodeType, Piece, PieceType
import time

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
        self.scoring_locations = FIELD_CONSTANTS.SCORING_LOCATIONS
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

    def update(self, time_elapsed):
        for robot in self.robots:
            robot.update(time_elapsed)
            self.checkIntake(robot)
            self.checkBorders(robot)
            for piece in self.pieces:
                self.checkScoring(piece)
            self.scoring.update()

    def checkBorders(self, robot):
        # edges
        if robot.pos.x + robot.frame[0]/2 > constants.FIELD_WIDTH:
            robot.pos.x = constants.FIELD_WIDTH - robot.frame[0]/2
        if robot.pos.x - robot.frame[0]/2 < 0:
            robot.pos.x = robot.frame[0]/2
        if robot.pos.y + robot.frame[1]/2 > constants.FIELD_HEIGHT:
            robot.pos.y = constants.FIELD_HEIGHT - robot.frame[1]/2
        if robot.pos.y - robot.frame[1]/2 < 0:
            robot.pos.y = robot.frame[1]/2

        # divider between alliance safe areas
        if robot.pos.y - robot.frame[0]/2 < 132.25 or robot.pos.y + robot.frame[0]/2 > constants.FIELD_HEIGHT - 132.25:
            if robot.pos.x + robot.frame[0]/2 > 216 and robot.pos.x < 216:
                robot.pos.x = 216 - robot.frame[0]/2
            if robot.pos.x - robot.frame[0]/2 < 216 and robot.pos.x > 216:
                robot.pos.x = 216 + robot.frame[0]/2

        LEFT_EDGE_POS = 60
        RIGHT_EDGE_POS = 157
        CHARGE_LOW_POS = 120
        CHARGE_HIGH_POS = 190

        # charge station edges
        if (robot.pos.y - robot.frame[0]/2 < CHARGE_HIGH_POS and robot.pos.y + robot.frame[0]/2 > CHARGE_LOW_POS) or ((robot.pos.y + robot.frame[0]/2 > constants.FIELD_HEIGHT - CHARGE_HIGH_POS and robot.pos.y - robot.frame[0]/2 < constants.FIELD_HEIGHT - CHARGE_LOW_POS)):
            if robot.pos.x + robot.frame[0]/2 > LEFT_EDGE_POS and robot.pos.x < LEFT_EDGE_POS:
                robot.pos.x = LEFT_EDGE_POS - robot.frame[0]/2
            if robot.pos.x - robot.frame[0]/2 < LEFT_EDGE_POS and robot.pos.x > LEFT_EDGE_POS:
                robot.pos.x = LEFT_EDGE_POS + robot.frame[0]/2

        if (robot.pos.y - robot.frame[0]/2 < CHARGE_HIGH_POS and robot.pos.y + robot.frame[0]/2 > CHARGE_LOW_POS) or (robot.pos.y + robot.frame[0]/2 > constants.FIELD_HEIGHT - CHARGE_HIGH_POS and robot.pos.y - robot.frame[0]/2 < constants.FIELD_HEIGHT - CHARGE_LOW_POS):
            if robot.pos.x + robot.frame[0]/2 > RIGHT_EDGE_POS and robot.pos.x < RIGHT_EDGE_POS:
                robot.pos.x = RIGHT_EDGE_POS - robot.frame[0]/2
            if robot.pos.x - robot.frame[0]/2 < RIGHT_EDGE_POS and robot.pos.x > RIGHT_EDGE_POS:
                robot.pos.x = RIGHT_EDGE_POS + robot.frame[0]/2

        # grid front
        if robot.pos.x < 216:
            if robot.pos.y - robot.frame[0]/2 < 56:
                robot.pos.y = 56 + robot.frame[0]/2
            if robot.pos.y + robot.frame[0]/2 > constants.FIELD_HEIGHT - 56:
                robot.pos.y = constants.FIELD_HEIGHT - (56 + robot.frame[0]/2)

    def checkIntake(self, robot):
        if robot.intaking:
            for piece in self.pieces:
                robot.intake(piece)

    def movePieces(self, time_elapsed):
        for piece in self.pieces:
            if piece.scored:
                continue

            shouldreturn = False
            if self.pieceOnRobot(piece):
                continue
            
            piece.pos.x += piece.vel.x * time_elapsed
            piece.pos.y += piece.vel.y * time_elapsed
            piece.pos.z = max(piece.pos.z + piece.vel.z * time_elapsed, 0)

            if piece.pos.z > 0:
                piece.vel.z -= 9.8 * time_elapsed
            else:
                piece.vel = Vector3(0, 0, 0)

        self.addPieces()

    def addPieces(self):
        for spot in [constants.FIELD_CONSTANTS.BLUE_SUBSTATION_LEFT, constants.FIELD_CONSTANTS.BLUE_SUBSTATION_RIGHT, constants.FIELD_CONSTANTS.RED_SUBSTATION_LEFT, constants.FIELD_CONSTANTS.RED_SUBSTATION_RIGHT]:
            toadd = True
            for piece in self.pieces:
                if (spot.x - 10 <= piece.pos.x <= spot.x + 10 and
                spot.y - 15 <= piece.pos.y <= spot.y + 15 and
                spot.z - 10 <= piece.pos.z <= spot.z + 10):
                    toadd = False
                    piece.pos.z = spot.z
            if toadd:
                self.pieces.append(Piece(PieceType.CUBE, spot))

    def checkScoring(self, piece):
        for scoringNodeIndex in range(len(constants.FIELD_CONSTANTS.SCORING_LOCATIONS)):
            if piece.scored or self.pieceOnRobot(piece):
                continue
            if constants.FIELD_CONSTANTS.SCORING_LOCATIONS[scoringNodeIndex][1] != NodeType.HYBRID and constants.FIELD_CONSTANTS.SCORING_LOCATIONS[scoringNodeIndex][1].value != piece.type.value:
                continue
            spot = constants.FIELD_CONSTANTS.SCORING_LOCATIONS[scoringNodeIndex][0]
            if (piece.pos.x - 10 < spot.x and piece.pos.x + 10 > spot.x and
                piece.pos.y - 8 < spot.y and piece.pos.y + 8 > spot.y and
                piece.pos.z - 5 < spot.z and piece.pos.z + 5 > spot.z):
                self.scoring.grid["Red"][scoringNodeIndex // 9][scoringNodeIndex % 3] += 1
                piece.scored = True
                print("scored")
            
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
        return score

    def update(self):
        self.score = self.calculateGridScore()

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