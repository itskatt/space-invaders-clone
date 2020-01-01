import pygame

from ..assets import get_sprite
from ..constants import (DEATH_EVENT, ENEMI_SHIP_SPEED, LEFT_MOVEMENT_KEYS,
                         RIGHT_MOVEMENT_KEYS, SHIP_HEALTH, SHIP_SPEED,
                         SHOOT_KEY)
from ..filters import get_damaged
from ..lasers import AutoLaser, BasicLaser
from .base import BaseFireingShip, BaseEnemiShip


class ShipShare:  # TODO: remove
    def __init__(self):
        self._dict = {}

    def add_ship(self, ship_type, perc):
        if ship_type not in self._dict:
            self.modify_ship(ship_type, perc)

    def modify_ship(self, ship_type, perc):
        self._dict[ship_type] = perc
        self._ajust()

    def remove_ship(self, ship_type):
        del self._dict[ship_type]
        self._ajust()

    def get_shares(self, count):
        d = {}
        for k in self._dict.keys():
            d[k] = round(count * self._dict[k] / 100)

        return d.items()

    def _ajust(self):
        total = sum(self._dict.values())
        if total != 100:
            for k in self._dict.keys():
                self._dict[k] = self._dict[k] * 100 / total


class Ship(BaseFireingShip):
    def __init__(self, game):
        super().__init__(game)

        self.speed = SHIP_SPEED

        self.normal_img = get_sprite("ship")
        self.damaged_img = get_damaged(self.normal_img)

        self.image = self.normal_img
        self.rect = self.image.get_rect(center=[
            self.game.screen_width / 2,
            self.game.screen_height / 1.11
        ])
        self.mask = pygame.mask.from_surface(self.image)

        self.health = SHIP_HEALTH

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == SHOOT_KEY:  # fire
                self.fire()

    def fire(self):
        self.game.scene.lasers.add(BasicLaser.create(self.game, self.game.scene, self.rect.midtop, False))

    def on_collision(self, damage):
        self.health -= damage
        self.image = self.damaged_img
        self.last_hit_time = self.game.loop_time
        if self.health <= 0:
            pygame.event.post(pygame.event.Event(DEATH_EVENT))

    def update(self):
        # lets try moving the ship according to input
        if any([self.game.pressed_keys[key] for key in LEFT_MOVEMENT_KEYS]):
            if not self.rect.topleft[0] < 0:
                self.rect.x -= self.speed * self.game.delta

        elif any([self.game.pressed_keys[key] for key in RIGHT_MOVEMENT_KEYS]):
            if not self.rect.topright[0] > self.game.screen_width:
                self.rect.x += self.speed * self.game.delta

        # can we remove the damage effect, if there is any ?
        if self.image == self.damaged_img and (self.game.loop_time - self.last_hit_time) >= 0.1:
            self.image = self.normal_img

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class EnemiShip(BaseFireingShip, BaseEnemiShip):
    speed = ENEMI_SHIP_SPEED
    laser_type = AutoLaser
    image_name = "enemi-ship"


class HeavyEnemiShip(BaseFireingShip, BaseEnemiShip):  # TODO: temporary, for testing
    speed = ENEMI_SHIP_SPEED / 2
    laser_type = BasicLaser
    image_name = "enemi-heavy-ship"
