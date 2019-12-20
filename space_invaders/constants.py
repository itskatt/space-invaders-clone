import pathlib
import sys

import pygame


# pyinstaller and paths
PYINSTALLER = getattr(sys, "frozen", False)

if PYINSTALLER:
    ASSETS_DIR = pathlib.Path(getattr(sys, "_MEIPASS")) / "assets"
else:
    ASSETS_DIR = pathlib.Path(__file__).parents[0] / "assets"

# window
BASE_SCREEN_SIZE = (800, 450)  # 16:9

SCREEN_SIZE = tuple([round(val * 1.5) for val in BASE_SCREEN_SIZE])
WINDOW_TITLE = "Space Invaders"

# misc
BG_SCROOL_SPEED = 1 * SCREEN_SIZE[1] / BASE_SCREEN_SIZE[1]

# font
FONT_SIZE = round(14 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0])

# game
LASER_SPEED = 5 * SCREEN_SIZE[1] / BASE_SCREEN_SIZE[1]

SHIP_SPEED = 6 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0]
SHIP_HEALTH = 10

ENEMI_SHIP_SPEED = 4 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0]
ENEMI_SHIP_SPAWN_INTERVAL = 3 * 1000

# events
SHIP_SPAWN_EVENT = pygame.USEREVENT + 1

BLOCKED_EVENTS = [  # events not in use blocked for performance
    pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEBUTTONUP,
    pygame.MOUSEMOTION,
    # pygame.MOUSEWHEEL,
    pygame.JOYAXISMOTION,
    pygame.JOYBALLMOTION,
    pygame.JOYBUTTONDOWN,
    pygame.JOYBUTTONUP,
    pygame.JOYHATMOTION,
    pygame.VIDEORESIZE  # TODO: remove when screen resizing suport is added
]

# colors
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(51, 207, 255)
