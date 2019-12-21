import argparse
import functools
import logging
import math
import os
import random
import sys
import time
import traceback
from collections import defaultdict
from contextlib import contextmanager

import pygame

from .assets import get_sprite, load_assets, pixeled
from .constants import (BG_SCROOL_SPEED, BLACK, BLOCKED_EVENTS, BLUE,
                        ENEMI_SHIP_SPAWN_INTERVAL, FONT_SIZE, SCREEN_SIZE,
                        SHIP_HEALTH, SHIP_SPAWN_EVENT, WHITE, WINDOW_TITLE)
from .scenes import MainScene
from .ships import EnemiShip, Ship

log = logging.getLogger(__name__)

# see: https://stackoverflow.com/questions/6395923/any-way-to-speed-up-python-and-pygame

class Game:
    FPS = 60

    def __init__(self, *, timeout=None):
        self.timeout = timeout

        # screen
        self.screen_size = self.screen_width, self.screen_height = SCREEN_SIZE

        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()

        self.screen.set_alpha(None)  # possible performance improvement, remove if troube is caused

        # ship
        self.ship = Ship(self)
        self.score = 0

        # time
        self.clock = pygame.time.Clock()

        self.loop_time = time.time()
        self.start_time = self.loop_time

        self.is_paused = False

        # keys
        self.pressed_keys = defaultdict(bool)

        # blocked events
        for event in BLOCKED_EVENTS:
            pygame.event.set_blocked(event)

        # scene + init
        self.scene = MainScene(self)

    def switch_scene(self, scene, *, save=False):
        if save:
            scene.last_scene = scene
        else:
            self.scene.cleanup()
        self.scene = scene

    def pause(self, text):
        screen = pygame.Surface(SCREEN_SIZE)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))

        font = pixeled(FONT_SIZE * 2)

        pause_text = font.render(text, True, WHITE)
        pause_txt_rect = pause_text.get_rect(center=(
            self.screen_width / 2,
            self.screen_height / 2
        ))
        self.screen.blit(pause_text, pause_txt_rect)

    def mainloop(self):
        pause_screen_drawn = False
        running = True
        while running:
            self.loop_time = time.time()

            for event in pygame.event.get():  # NOTE: check BOCKED_EVENTS before messing with new events
                if event.type == pygame.QUIT:
                    log.info("Quitting")
                    running = False

                elif event.type == pygame.KEYUP:
                    self.pressed_keys[event.key] = False

                elif event.type == pygame.KEYDOWN:
                    self.pressed_keys[event.key] = True

                    if event.key == pygame.K_ESCAPE:
                        if self.ship.health > 0:
                            self.is_paused = not self.is_paused
                
                self.scene.process_event(event)

            if not self.is_paused:
                if pause_screen_drawn:
                    pause_screen_drawn = False

                self.scene.update()
                self.scene.draw()

                pygame.display.flip()

            else:
                if not pause_screen_drawn:
                    self.pause("You died" if self.ship.health <= 0 else "Paused")
                    pygame.display.flip()
                    pause_screen_drawn = True

            if self.timeout and (self.loop_time - self.start_time) >= self.timeout:
                sys.exit()

            self.clock.tick(self.FPS)


@contextmanager
def setup_log():  # FIXME
    try:
        loggers = [
            log,
            # logging.getLogger("space_invaders.assets")
        ]
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("[{levelname:^7}] {name}: {message}", style="{")
        handler.setFormatter(fmt)
        for log_ in loggers:
            log_.setLevel(logging.INFO)
            log_.addHandler(handler)

        yield
    finally:
        for log_ in loggers:
            for hnd in log_.handlers:
                hnd.close()
                log_.removeHandler(hnd)


def parse_args():
    parser = argparse.ArgumentParser(
        WINDOW_TITLE,
        description="The game's cli"
    )
    parser.add_argument(
        "--no-reports",
        help="Don't save crash reports when the game crashes.",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--timeout",
        help="Stop the game after the amount of time provided. Usefull when profiling",
        type=int,
        default=None
    )
    return parser.parse_args()


def main():
    with setup_log():
        args = parse_args()

        os.environ["SDL_VIDEO_CENTERED"] = "1"  # place the game window at the center of the screen
        status = pygame.init()
        log.info(f"Pygame init status {status}")

        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF)

        try:
            load_assets(SCREEN_SIZE)

            game = Game(timeout=args.timeout)
            game.mainloop()
        except Exception:
            log.exception("An exception occured:")

            if not args.no_reports:
                with open(f"crash_{round(time.time())}.txt", "w", encoding="utf=8") as f:
                    traceback.print_exc(file=f)
                    log.info("Created crash report")

        pygame.quit()
