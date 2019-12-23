import functools
import math
import random

import pygame

from ..assets import get_sprite, pixeled
from ..constants import (BG_SCROOL_SPEED, BLACK, BLUE,
                         ENEMI_SHIP_SPAWN_INTERVAL, FONT_SIZE, SHIP_HEALTH,
                         SHIP_SPAWN_EVENT, WHITE)
from ..ships import EnemiShip
from . import GameScene


class MainScene(GameScene):
    def __init__(self, game):
        super().__init__(game)

        # shortcuts
        self.ship = game.ship
        self.score = game.score

        # background
        self.bg_img = get_sprite("background")
        self.bg_rect = self.bg_img.get_rect(topleft=(0, 0))
        self.bg_img_y_pos = 0.0

        # status text
        self.status_text_bg = pygame.Surface((
                self.game.screen_width / 7,
                self.game.screen_height / 7
        ))

        # sprites
        self.lasers = pygame.sprite.Group()
        self.enemi_ships = pygame.sprite.Group()

        self.objects = [  # TODO: change to custom class for ex ?
            self.lasers,
            self.enemi_ships
        ]

        # scene action init
        self.spawn_enemi_ships(5)
        pygame.time.set_timer(SHIP_SPAWN_EVENT, ENEMI_SHIP_SPAWN_INTERVAL)

    def cleanup(self):
        for obj in self.objects:
            obj.empty()
        pygame.time.set_timer(SHIP_SPAWN_EVENT, 0)  # disable the timer

    def process_event(self, event):
        if event.type == SHIP_SPAWN_EVENT:
            self.spawn_enemi_ships(random.randint(2, 3))

        self.ship.get_event(event)

    def update(self):
        self.ship.update()
        for obj in self.objects:
            obj.update()

    def clear_screen(self):
        self.draw_bg()  # also clears off the screen

    def draw(self):
        self.ship.draw(self.screen)
        for obj in self.objects:
            obj.draw(self.screen)

        self.draw_status_box()
        self.display_fps()

    def spawn_enemi_ships(self, count):
        # this func is a mess
        pad = round(self.game.screen_width / 20)
        spawn_aera = (
            self.game.screen_width - pad,
            round(self.game.screen_height / 11.25)
        )
        xpositions = random.sample(range(pad, spawn_aera[0], math.ceil(spawn_aera[0] / count)), count)
        for pos in xpositions:
            self.enemi_ships.add(EnemiShip(
                self.game, self,
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

        health_txt = font.render(f"Health: {health}", False, BLACK)
        health_rect = health_txt.get_rect(center=(centerx, round(height / 4 * 2.5)))

        bg.blit(score, score_rect)
        bg.blit(health_txt, health_rect)

        linew = round(height / 13)
        pygame.draw.line(
            bg, BLUE,
            (0, height - linew / 2),
            (round((health * width) / SHIP_HEALTH), height - linew / 2),
            linew
        )

        return bg

    def draw_status_box(self):
        bg = self._get_status_box(self.game.score, self.ship.health)

        self.game.screen.blit(bg, (
            self.game.screen_width - bg.get_width(),
            self.game.screen_height - bg.get_height()
        ))

    @functools.lru_cache(5)
    def _get_fps_text(self, fps):
        font = pixeled(round(FONT_SIZE / 2))
        fps_text = font.render(f"FPS: {round(fps)}", False, WHITE)
        return fps_text

    def display_fps(self):
        fps_text = self._get_fps_text(round(self.game.clock.get_fps()))
        self.game.screen.blit(fps_text, (0, 0))

    def draw_bg(self):
        self.bg_img_y_pos += BG_SCROOL_SPEED
        if self.bg_img_y_pos >= self.game.screen_height:
            self.bg_img_y_pos = self.game.screen_height - self.bg_img.get_height()

        self.bg_rect.y = self.bg_img_y_pos

        if self.bg_rect.y > 0:
            self.game.screen.blit(self.bg_img, (0, self.bg_rect.y - self.game.screen_height))

        # sub = self.bg_img.subsurface((0, 0), self.screen_size)  TODO: subsurface?
        self.game.screen.blit(self.bg_img, self.bg_rect)
