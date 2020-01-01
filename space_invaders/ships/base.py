import random

import pygame

from ..assets import get_sprite
from ..constants import ENEMI_SHIP_HEALTH, ENEMI_SHIP_SHOOT_INTERVAL, RED
from ..filters import get_damaged


class BaseShip(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.last_hit_time = 0

    def fire(self):
        raise NotImplementedError

    def on_collision(self, damage):
        raise NotImplementedError

class BaseEnemiShip(BaseShip):
    def __init__(self, game, scene, original_x_position):
        super().__init__(game)
        self.scene = scene

        self.normal_img = pygame.transform.rotate(
            get_sprite(self._get_image_name()), 180)  # TODO: change?
        self.damaged_img = get_damaged(self.normal_img)

        self.image = self.normal_img
        self.rect = self.image.get_rect(midbottom=(original_x_position, 0))
        
        self.direction = random.randint(0, 1)
        self.last_shoot_time = self.game.loop_time
        
        # default values
        self.health = random.randint(*ENEMI_SHIP_HEALTH)
        self.shoot_interval = random.randint(*ENEMI_SHIP_SHOOT_INTERVAL) / 10
        self.awarded_points = 1

    def _get_image_name(self):
        return self.image_name

    def fire(self):
        pass

    def move(self):
        if self.direction == 0:  # left
            self.rect.x -= self.speed * self.game.delta

        elif self.direction == 1:  # right
            self.rect.x += self.speed * self.game.delta

    def on_collision(self, damage):
        self.health -= damage
        self.image = self.damaged_img
        self.last_hit_time = self.game.loop_time

        if self.health <= 0:
            self.game.score += self.awarded_points
            self.kill()

    def update(self):
        # if self.is_sliding:
        #     self.is_sliding = False

        # has the sprite reached the border? if so, reverse time
        if (self.rect.topleft[0] < 0) or (self.rect.topright[0] > self.game.screen_width):
            self.direction = int(not self.direction)

        # move the sprite
        self.move()

        # can we remove the damage effect, if there is any
        if self.image == self.damaged_img and (self.game.loop_time - self.last_hit_time) >= 0.1:
            self.image = self.normal_img

        # is the ship fully spawned? if not, move it down and don't shoot
        if self.rect.centery <= self.game.screen_height / 11.25:
            self.rect.y += 1 * self.game.delta
            return

        # should it shoot
        if (self.game.loop_time - self.last_shoot_time) > self.shoot_interval:
            self.fire()
            self.last_shoot_time = self.game.loop_time

        # prevent ship stacking TODO: make it work eventually. yes, eventually
        # for ship in self.game.enemi_ships.sprites():
        #     if ship == self or ship.rect.x > self.rect.x:
        #         pass
        #     elif ship.is_sliding and not self.direction == 1:
        #         pass

        #     elif self.rect.colliderect(ship.rect) and self.direction == ship.direction:
        #         if not 0 <= self.rect.x >= self.game.screen_width:
        #             self.is_sliding = True
        #             self.move()


class BaseFireingShip(BaseEnemiShip):  # TODO: make Ship class inherit from this
    def fire(self):
        self.scene.lasers.add(self.laser_type.create(self.game, self.scene, self.rect.midbottom, True))
