import pygame

from ..assets import get_sprite
from ..constants import (DEATH_EVENT, LEFT_MOVEMENT_KEYS, RIGHT_MOVEMENT_KEYS,
                         SHIP_HEALTH, SHIP_SPEED, SHOOT_KEY)
from ..filters import get_healed
from ..lasers import AutoLaser, BasicLaser
from ..utils import clamp
from ..weapons import BasicShooter
from .base import BaseEnemiShip, BaseFireingShip, BaseRamingship, BaseShip


class Ship(BaseShip):  # TODO: cleanup this class like the others
    def __init__(self, game):
        sprite = get_sprite("ships", "ship")
        super().__init__(game, sprite)
        self.healed_img = get_healed(sprite)

        self.speed = SHIP_SPEED

        self.rect = self.image.get_rect(center=[
            self.game.screen_width / 2,
            self.game.screen_height / 1.11
        ])
        self.mask = pygame.mask.from_surface(self.image)

        self.weapon = BasicShooter(self, "midtop")

        self.health = SHIP_HEALTH

    def heal(self, amount):
        self.image = self.healed_img
        self.last_hit_time = self.game.loop_time

        new = self.health + amount
        self.health = clamp(0, SHIP_HEALTH, new)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == SHOOT_KEY:  # fire
                self.weapon.fire()

    def on_collision(self, damage):
        super().on_collision(damage)

        if self.health <= 0:
            pygame.event.post(pygame.event.Event(DEATH_EVENT))

    def update(self):
        super().update()

        # lets try moving the ship according to input
        if any([self.game.pressed_keys[key] for key in LEFT_MOVEMENT_KEYS]):
            if not self.rect.topleft[0] < 0:
                self.rect.x -= self.speed * self.game.delta

        elif any([self.game.pressed_keys[key] for key in RIGHT_MOVEMENT_KEYS]):
            if not self.rect.topright[0] > self.game.screen_width:
                self.rect.x += self.speed * self.game.delta

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class EnemiShip(BaseFireingShip, BaseEnemiShip):
    speed = 3.5
    health = 4
    laser_type = AutoLaser
    image_name = "enemi-ship"


class HeavyEnemiShip(BaseFireingShip):
    speed = 2.5
    health = 6
    laser_type = BasicLaser
    image_name = "enemi-heavy-ship"


class RamShip(BaseRamingship):
    speed = 5
    y_speed = 1.5
    health = 2
    damage = 10
    image_name = "enemi-ram-ship"
