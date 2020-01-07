import functools
import logging
import math
import queue
import random
from collections import Counter
from itertools import chain

import pygame

from ..assets import get_sprite, pixeled
from ..constants import (BG_SCROOL_SPEED, BLACK, BLUE,
                         ENEMI_SHIP_SPAWN_INTERVAL, FONT_SIZE, SHIP_HEALTH,
                         SHIP_SPAWN_EVENT, WHITE)
from ..ships import EnemiShip, HeavyEnemiShip, RamShip
from . import BaseScene

log = logging.getLogger(__name__)


class GameScene(BaseScene):
    pass  # TODO: move some methods to this class


class MainScene(GameScene):
    def __init__(self, game):
        super().__init__(game)

        # shortcuts
        self.ship = game.ship

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

        # wave managing
        self.wave_count = 1
        self.wave_data = self.get_wave_data()
        self.current_wave_queue = queue.Queue()
        self.create_wave(self.wave_data[1])

        # scene action init
        self.spawn_enemi_ships(5)
        pygame.time.set_timer(SHIP_SPAWN_EVENT, ENEMI_SHIP_SPAWN_INTERVAL)

    def cleanup(self):
        for obj in self.objects:
            obj.empty()
        self._get_status_box.cache_clear()
        self._get_fps_text.cache_clear()
        pygame.time.set_timer(SHIP_SPAWN_EVENT, 0)  # disable the timer

    def process_event(self, event):
        if event.type == SHIP_SPAWN_EVENT:
            self.spawn_enemi_ships(random.randint(2, 4))

        self.ship.get_event(event)

    def get_wave_data(self):
        waves = {  # TODO: probably move to own file or something similar
            1: (
                lambda score: (score ** 2) / 80 + 5,  # cap func
                ((EnemiShip, 20),)  # ship type, count
            ),
            2: (
                lambda score: ((score - 20) ** 2) / 80 + 10,
                ((EnemiShip, 15), (HeavyEnemiShip, 10)),
            ),
            3: (
                lambda score: ((score - 30) ** 2) / 80 + 10,
                ((EnemiShip, 10), (HeavyEnemiShip, 15), (RamShip, 5)),
            ),
            4: (
                lambda score: (score * 0.5) / 3,
                ((EnemiShip, 15), (HeavyEnemiShip, 15), (RamShip, 10)),
            ),
            5: (
                lambda score: math.cos(score) * 6 + 15,
                ((EnemiShip, 30), (HeavyEnemiShip, 25),)
            ),
            "final": (
                lambda score: ((score - 40) ** 2) / 80 + 15,
                ((EnemiShip, 500), (HeavyEnemiShip, 500))  # TEMPORARY
            )
        }
        return waves.get(self.wave_count, waves["final"])

    def create_wave(self, ships):
        wave = []
        for ship_type, count in ships:
            wave.extend((ship_type for _ in range(count)))

        random.shuffle(wave)

        for ship_type in wave:
            self.current_wave_queue.put_nowait(ship_type)

    def spawn_enemi_ships(self, count):
        # ajust the count according to the current enemy cap
        cap = self.wave_data[0](self.game.score)
        ships = len(self.enemi_ships)
        if ships + count > cap:
            count = round(cap - ships)
        if count <= 0:
            return

        # consume items from the queue
        wave = []
        is_empty = False
        try:
            for _ in range(count):
                wave.append(self.current_wave_queue.get_nowait())
        except queue.Empty:
            is_empty = True

        # spawn the ships
        for ship_type, ship_count in Counter(wave).items():
            self.spawn_enemi_ships_type(ship_count, ship_type)

        # if the queue is empty, so lets move to the next wave
        if is_empty:
            self.wave_count += 1
            log.info(f"Moving to wave {self.wave_count}")  # TODO: handle final wave case
            self.wave_data = self.get_wave_data()
            self.create_wave(self.wave_data[1])

    def spawn_enemi_ships_type(self, count, ship_type):
        # define the spawn aera
        pad = round(self.game.screen_width / 20)
        spawn_aera = self.game.screen_width - pad

        # first avoid errors
        possible_positions = range(pad, spawn_aera, math.ceil(spawn_aera / count))
        poss_pos_len = len(possible_positions)
        q, r = divmod(count, poss_pos_len)
        if q != 0:
            counts = [poss_pos_len] * q + [r]
        else:
            counts = [r]

        # now place the ships
        log.debug(f"Spawning {count} ships of type {ship_type}")
        for pos in chain.from_iterable([random.sample(possible_positions, c) for c in counts if c]):
            self.enemi_ships.add(ship_type(self.game, self, pos))

    def update(self):
        self.ship.update()
        for obj in self.objects:
            obj.update()

    def clear_screen(self):
        self.bg_img_y_pos += BG_SCROOL_SPEED * self.game.delta
        if self.bg_img_y_pos >= self.game.screen_height:
            self.bg_img_y_pos = self.game.screen_height - self.bg_img.get_height()

        self.bg_rect.y = self.bg_img_y_pos

        if self.bg_rect.y > 0:
            self.game.screen.blit(self.bg_img, (0, self.bg_rect.y - self.game.screen_height))

        # sub = self.bg_img.subsurface((0, 0), self.screen_size)  TODO: subsurface?
        self.game.screen.blit(self.bg_img, self.bg_rect)

    def draw(self):
        self.ship.draw(self.screen)
        for obj in self.objects:
            obj.draw(self.screen)

        self.draw_status_box()
        self.display_fps()

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

        bg.blits(((score, score_rect), (health_txt, health_rect)))

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

    @functools.lru_cache(4)
    def _get_fps_text(self, fps):
        font = pixeled(round(FONT_SIZE / 2))
        fps_text = font.render(f"FPS: {round(fps)}", True, WHITE)
        return fps_text

    def display_fps(self):
        fps_text = self._get_fps_text(round(self.game.clock.get_fps()))
        self.game.screen.blit(fps_text, (0, 0))
