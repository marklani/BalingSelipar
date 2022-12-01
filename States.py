from enum import Enum

class GameState(Enum):
    Start = 1
    AngleSelection = 2
    PowerSelection = 3
    SlipperReleased = 4
    TowerDown = 5
    Reset = 6
    StartMenu = 7

class KeyState(Enum):
    SpaceKeyPressed = 1
    SpaceKeyReleased = 2
    SpaceKeyLongPressed = 3