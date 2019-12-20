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

        # background
        self.bg_img = get_sprite("background")
        self.bg_rect = self.bg_img.get_rect(topleft=(0, 0))
        self.bg_img_y_pos = 0.0

        # status text
        self.status_text_bg = pygame.Surface((
                self.screen_width / 7,
                self.screen_height / 7
        ))

        # sprites
        self.lasers = pygame.sprite.Group()
        self.enemi_ships = pygame.sprite.Group()

        self.objects = [  # TODO: change to custom class for ex ?
            self.lasers,
            self.enemi_ships
        ]
        self.ship = Ship(self)
        self.score = 0

        # time
        self.clock = pygame.time.Clock()

        self.loop_time = time.time()
        self.start_time = self.loop_time

        self.is_paused = False

        # keys
        self.pressed_keys = defaultdict(bool)

        # game init
        self.spawn_enemi_ships(5)
        pygame.time.set_timer(SHIP_SPAWN_EVENT, ENEMI_SHIP_SPAWN_INTERVAL)

        for event in BLOCKED_EVENTS:
            pygame.event.set_blocked(event)

    def spawn_enemi_ships(self, count):
        # this func is a mess
        if self.is_paused:
            return
        pad = round(self.screen_width / 20)
        spawn_aera = (
            self.screen_width - pad,
            round(self.screen_height / 11.25)
        )
        xpositions = random.sample(range(pad, spawn_aera[0], math.ceil(spawn_aera[0] / count)), count)
        for pos in xpositions:
            self.enemi_ships.add(EnemiShip(
                self,
                (pos, spawn_aera[1]),
                random.choice((0, 1))
            ))

    @functools.lru_cache(1)  # TODO: change probably ?
    def _get_status_box(self, score, health):
        bg = self.status_text_bg
        bg.fill(WHITE)
        bg.set_alpha(255 / 2)

        width = bg.get_width()
        height = bg.get_height()
        centerx = width / 2
        font = pixeled(FONT_SIZE)

        score = font.render(f"Score: {score}", False, BLACK)
        score_rect = score.get_rect(center=(centerx, round(height / 4)))

        health = font.render(f"Health: {health}", False, BLACK)
        health_rect = health.get_rect(center=(centerx, round(height / 4 * 2.5)))

        bg.blit(score, score_rect)
        bg.blit(health, health_rect)

        linew = round(height / 13)
        pygame.draw.line(
            bg, BLUE,
            (0, height - linew / 2),
            (round((self.ship.health * width) / SHIP_HEALTH), height - linew / 2),
            linew
        )

        return bg

    def draw_status_box(self):
        bg = self._get_status_box(self.score, self.ship.health)

        self.screen.blit(bg, (
            self.screen_width - bg.get_width(),
            self.screen_height - bg.get_height()
        ))

    @functools.lru_cache(5)
    def _get_fps_text(self, fps):
        font = pixeled(round(FONT_SIZE / 2))
        fps_text = font.render(f"FPS: {round(fps)}", False, WHITE)
        return fps_text

    def display_fps(self):
        fps_text = self._get_fps_text(round(self.clock.get_fps()))
        self.screen.blit(fps_text, (0, 0))

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

    def update_bg(self):
        self.bg_img_y_pos += BG_SCROOL_SPEED
        if self.bg_img_y_pos >= self.screen_height:
            self.bg_img_y_pos = self.screen_height - self.bg_img.get_height()

        self.bg_rect.y = self.bg_img_y_pos

        if self.bg_rect.y > 0:
            self.screen.blit(self.bg_img, (0, self.bg_rect.y - self.screen_height))

        # sub = self.bg_img.subsurface((0, 0), self.screen_size)  TODO: subsurface?
        self.screen.blit(self.bg_img, self.bg_rect)

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
                    key = event.key

                    self.pressed_keys[key] = True

                    if key == pygame.K_ESCAPE:
                        if self.ship.health > 0:
                            self.is_paused = not self.is_paused

                elif event.type == SHIP_SPAWN_EVENT:
                    self.spawn_enemi_ships(random.randint(2, 3))

                self.ship.get_event(event)

            if not self.is_paused:
                if pause_screen_drawn:
                    pause_screen_drawn = False

                self.update_bg()  # also clears off the screen

                # updating
                self.ship.update()
                for obj in self.objects:  # TODO: change ?
                    obj.update()

                # drawing
                self.ship.draw(self.screen)
                for obj in self.objects:
                    obj.draw(self.screen)

                self.draw_status_box()
                self.display_fps()

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
