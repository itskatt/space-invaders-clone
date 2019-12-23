import argparse
import logging
import os
import sys
import time
import traceback
from collections import defaultdict
from contextlib import contextmanager

import pygame

from .assets import load_assets
from .constants import (BLOCKED_EVENTS, DEATH_EVENT, DIR, DISPLAY_FLAGS,
                        FULLSCREEN_KEY, PAUSE_KEY, SCREEN_SIZE, WINDOW_TITLE)
from .scenes import DeathScene, PauseScene, WelcomeScene, MenuScene
from .scenes.game import MainScene
from .ships import Ship

log = logging.getLogger(__name__)

# see: https://stackoverflow.com/questions/6395923/any-way-to-speed-up-python-and-pygame


class Game:
    FPS = 60

    def __init__(self, *, timeout=None):
        self.timeout = timeout

        # screen
        self.display_info = pygame.display.Info()

        self.screen_size = self.screen_width, self.screen_height = SCREEN_SIZE

        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode(SCREEN_SIZE, DISPLAY_FLAGS)
        self.screen_rect = self.screen.get_rect()

        self.is_fullscreen = False

        self.screen.set_alpha(None)  # possible performance improvement, remove if troube is caused

        # load the assets
        load_assets(self.screen_size)

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

        # scene
        self.scene = WelcomeScene(self)

    def switch_scene(self, scene, *, scene_cleanup=True):
        if scene_cleanup:
            self.scene.cleanup()
        self.scene = scene

    def start_new_game(self):
        # reset vars
        self.ship = Ship(self)
        self.score = 0

        self.switch_scene(MainScene(self))

    def pause_game(self):
        if self.is_paused or self.ship.health <= 0 or isinstance(self.scene, MenuScene):
            return

        self.is_paused = True
        self.switch_scene(PauseScene(self, self.scene), scene_cleanup=False)

    def toggle_fullscreen(self):  # TODO: FIXME
        if self.is_fullscreen:
            flags = DISPLAY_FLAGS
            # self.screen_size = self.screen_width, self.screen_height = SCREEN_SIZE
        else:
            flags = DISPLAY_FLAGS | pygame.HWSURFACE | pygame.FULLSCREEN
            # self.screen_size = self.screen_width, self.screen_height = self.display_info.current_w, self.display_info.current_h

        self.screen = pygame.display.set_mode(self.screen_size, flags)
        self.screen_rect = self.screen.get_rect()

        self.is_fullscreen = not self.is_fullscreen

    def mainloop(self):
        running = True
        while running:
            self.loop_time = time.time()

            # event processing
            for event in pygame.event.get():  # NOTE: check BOCKED_EVENTS before messing with new events

                if event.type == pygame.QUIT:
                    log.info("Quitting")
                    running = False

                elif event.type == pygame.KEYUP:
                    self.pressed_keys[event.key] = False

                elif event.type == pygame.KEYDOWN:
                    self.pressed_keys[event.key] = True

                    if event.key == PAUSE_KEY and not self.is_paused:
                        self.pause_game()
                        continue  # we don't want the pause scene to catch this event

                    elif event.key == FULLSCREEN_KEY:
                        self.pause_game()
                        self.toggle_fullscreen()

                elif event.type == DEATH_EVENT:
                    self.switch_scene(DeathScene(self, self.scene), scene_cleanup=False)

                self.scene.process_event(event)

            # main logic
            self.scene.update()
            self.scene.clear_screen()
            self.scene.draw()

            self.scene.update_screen()

            # if self.timeout is set, check if we can quit the game
            if self.timeout and (self.loop_time - self.start_time) >= self.timeout:
                sys.exit()

            # tick-tock-tick-tock-tick-tock
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
        log.info(f"SDL version: {(pygame.get_sdl_version())}")

        try:
            game = Game(timeout=args.timeout)
            game.mainloop()
        except Exception:
            log.exception("An exception occured:")

            if not args.no_reports:
                with open(DIR / f"crash_{round(time.time())}.txt", "w", encoding="utf=8") as f:
                    traceback.print_exc(file=f)
                    log.info("Created crash report")

        pygame.quit()
