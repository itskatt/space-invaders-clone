from random import randint

import pygame

from ..assets import get_sprite
from ..base import BaseSprite
from ..constants import (BASE_SCREEN_SIZE, DEFAULT_ENEMI_SHIP_HEALTH,
                         DEFAULT_ENEMI_SHIP_SPEED, DAMAGED_EFFECT_STAY_TIME)
from ..filters import get_damaged, get_rotated


class BaseShip(BaseSprite):
    image: pygame.Surface

    def __init__(self, game, image):
        super().__init__()

        self.game = game

        self.normal_img = self.image = image
        self.damaged_img = get_damaged(image)

        self.last_hit_time = 0

    def fire(self):
        pass

    def on_collision(self, damage):
        self.health -= damage  # pylint: disable=no-member
        self.image = self.damaged_img
        self.last_hit_time = self.game.loop_time

    def update(self):
        # can we remove the damage effect, if there is any
        if self.image == self.damaged_img and (self.game.loop_time - self.last_hit_time) >= DAMAGED_EFFECT_STAY_TIME:
            self.image = self.normal_img


class BaseEnemiShip(BaseShip):
    def __init__(self, game, scene, original_x_position):
        super().__init__(
            game,
            get_rotated(get_sprite("ships", self.image_name), 180)
        )
        self.scene = scene

        self.rect = self.image.get_rect(midbottom=(original_x_position, 0))

        self.direction = randint(0, 1)

        # default values
        self.set_default("health", DEFAULT_ENEMI_SHIP_HEALTH)
        self.set_default("speed", DEFAULT_ENEMI_SHIP_SPEED)

        self.awarded_points = 1

    def move(self):
        if self.direction == 0:  # left
            self.rect.x -= (self.speed * self.game.screen_width / BASE_SCREEN_SIZE[0]) * self.game.delta

        elif self.direction == 1:  # right
            self.rect.x += (self.speed * self.game.screen_width / BASE_SCREEN_SIZE[0]) * self.game.delta

    def turn(self):
        # has the sprite reached the border? if so, reverse time
        if (self.rect.topleft[0] < 0) or (self.rect.topright[0] > self.game.screen_width):
            self.direction = int(not self.direction)
            return True
        return False

    def on_collision(self, damage):
        super().on_collision(damage)

        if self.health <= 0:  # pylint: disable=no-member
            self.game.score += self.awarded_points
            self.kill()

    def update(self):
        super().update()

        # move the sprite
        self.move()

        # make it change direction if it touches the border
        self.turn()


class BaseFireingShip(BaseEnemiShip):
    def __init__(self, game, scene, pos):
        super().__init__(game, scene, pos)

        self.last_shoot_time = self.game.loop_time
        self.set_default("shoot_interval", randint(8, 12) / 10)

    def fire(self):
        self.scene.lasers.add(self.laser_type.create(self.game, self.scene, self.rect.midbottom, True))

    def update(self):
        super().update()

        # is the ship fully spawned? if not, move it down and don't shoot
        if self.rect.centery <= self.game.screen_height / 11.25:
            self.rect.y += 1 * self.game.delta
            return

        # should it shoot
        if (self.game.loop_time - self.last_shoot_time) > self.shoot_interval:
            self.fire()
            self.last_shoot_time = self.game.loop_time


class BaseRamingship(BaseEnemiShip):
    def __init__(self, game, scene, pos):
        super().__init__(game, scene, pos)
        self.imgs = [
            get_rotated(self.image, -90),
            get_rotated(self.image, 90)
        ]
        self.image = self.imgs[self.direction]

    def turn(self):
        if super().turn():
            self.image = self.imgs[self.direction]

    def update(self):
        super().update()

        # and down goes the ship
        self.rect.y += self.y_speed * self.game.delta

        # has it gone out of the screen ?
        if self.rect.y > self.game.screen_height:
            self.kill()

        # damage the ship when we collid with them
        collision = pygame.sprite.spritecollide(self, [self.game.ship], False)
        if pygame.sprite.spritecollideany(self, collision, pygame.sprite.collide_mask):
            self.game.ship.on_collision(self.damage)
            self.kill()
