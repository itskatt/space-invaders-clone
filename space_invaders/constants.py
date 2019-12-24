import pathlib
import sys

import pygame


# have we been pyinstalled ?
PYINSTALLER = getattr(sys, "frozen", False)

# paths
if PYINSTALLER:
    DIR = pathlib.Path(getattr(sys, "_MEIPASS"))
else:
    DIR = pathlib.Path(__file__).parents[0]

ASSETS_DIR = DIR / "assets"

# window
BASE_SCREEN_SIZE = (800, 450)  # 16:9

SCREEN_SIZE = tuple([round(val * 1.5) for val in BASE_SCREEN_SIZE])
WINDOW_TITLE = "Space Invaders"

# display flags
DISPLAY_FLAGS = pygame.DOUBLEBUF

# speed
BASE_FPS = 60
GAME_SPEED_INFLUENCER = 1000 / BASE_FPS # the higher, the slower

BG_SCROOL_SPEED = 1 * SCREEN_SIZE[1] / BASE_SCREEN_SIZE[1]
TEXT_BLINK_SPEED = 5
TEXT_RESIZE_SPEED = 0.5

# font
FONT_SIZE = round(14 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0])

# our ship
SHIP_SPEED = 6 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0]
SHIP_HEALTH = 10

# the other ship(s)
ENEMI_SHIP_HEALTH = (2, 4)
ENEMI_SHIP_SPEED = 4 * SCREEN_SIZE[0] / BASE_SCREEN_SIZE[0]
ENEMI_SHIP_SHOOT_INTERVAL = (8, 12)  # 1/10th of a second
ENEMI_SHIP_NO_SHOOT_TIME = (5, 14)  # 1/10th of a second
ENEMI_SHIP_SPAWN_INTERVAL = 3 * 1000

# lasers
LASER_SPEED = 5 * SCREEN_SIZE[1] / BASE_SCREEN_SIZE[1]

# custom events
SHIP_SPAWN_EVENT = pygame.USEREVENT + 1
DEATH_EVENT = pygame.USEREVENT + 2

# blocked events
BLOCKED_EVENTS = [  # events not in use, blocked for performance
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

# keybinds
PAUSE_KEY = pygame.K_ESCAPE
FULLSCREEN_KEY = pygame.K_F11
SHOOT_KEY = pygame.K_SPACE
RESTART_KEY = pygame.K_r
START_KEY = pygame.K_RETURN

LEFT_MOVEMENT_KEYS = [pygame.K_LEFT, pygame.K_a]
RIGHT_MOVEMENT_KEYS = [pygame.K_RIGHT, pygame.K_d]

# colors
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(51, 207, 255)
