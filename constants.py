from environments.environment import NodeType
from pygame import Vector3

class CONSTANTS_2023:
    FIELD_WIDTH = 315.5
    FIELD_HEIGHT = 651.25

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