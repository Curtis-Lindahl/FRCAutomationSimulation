from environments.piece import NodeType
from pygame import Vector2, Vector3

FIELD_WIDTH = 315.5
FIELD_HEIGHT = 651.25

def flipPoint(point: Vector3):
    return Vector3(point.x, FIELD_HEIGHT - point.y, point.z)

def pickupSpot(point: Vector3):
    return Vector3(point.x, point.y - 20, point.z)

class POOFS_BOT:
    MAX_ACCEL = 10
    FRAME_SIZE = 26

class FIELD_CONSTANTS:
    SCORING_LOCATIONS = [
    [Vector3(20.5, 14.25, 46), NodeType.CONE],
    [Vector3(42.5, 14.25, 35.5), NodeType.CUBE],
    [Vector3(64.5, 14.25, 46), NodeType.CONE],
    [Vector3(85.125, 14.25, 46), NodeType.CONE],
    [Vector3(107.125, 14.25, 35.5), NodeType.CUBE],
    [Vector3(129.125, 14.25, 46), NodeType.CONE],
    [Vector3(149.75, 14.25, 46), NodeType.CONE],
    [Vector3(171.75, 14.25, 35.5), NodeType.CUBE],
    [Vector3(193.75, 14.25, 46), NodeType.CONE],

    [Vector3(20.5, 31, 34), NodeType.CONE],
    [Vector3(42.5, 31, 23.5), NodeType.CUBE],
    [Vector3(64.5, 31, 34), NodeType.CONE],
    [Vector3(85.125, 31, 34), NodeType.CONE],
    [Vector3(107.125, 31, 23.5), NodeType.CUBE],
    [Vector3(129.125, 31, 34), NodeType.CONE],
    [Vector3(149.75, 31, 34), NodeType.CONE],
    [Vector3(171.75, 31, 23.5), NodeType.CUBE],
    [Vector3(193.75, 31, 34), NodeType.CONE],
    
    [Vector3(20.5, 47, 0), NodeType.HYBRID],
    [Vector3(42.5, 47, 0), NodeType.HYBRID],
    [Vector3(64.5, 47, 0), NodeType.HYBRID],
    [Vector3(85.125, 47, 0), NodeType.HYBRID],
    [Vector3(107.125, 47, 0), NodeType.HYBRID],
    [Vector3(129.125, 47, 0), NodeType.HYBRID],
    [Vector3(149.75, 47, 0), NodeType.HYBRID],
    [Vector3(171.75, 47, 0), NodeType.HYBRID],
    [Vector3(193.75, 47, 0), NodeType.HYBRID]
    ]

    BLUE_SUBSTATION_LEFT = Vector3(240, 7, 42)
    BLUE_SUBSTATION_RIGHT = Vector3(280, 7, 42)
    RED_SUBSTATION_LEFT = flipPoint(BLUE_SUBSTATION_LEFT)
    RED_SUBSTATION_RIGHT = flipPoint(BLUE_SUBSTATION_RIGHT)

    chargeStationTopRight = Vector2(156.64, 191.125) # heres the top right
    chargeStationBottomLeft = Vector2(59.39, 115) # heres the bottom left
    chargeStationBalancedTopRight = Vector2(156.64, 173.06)
    chargeStationBalancedBottomLeft = Vector2(59.39, 133.06)