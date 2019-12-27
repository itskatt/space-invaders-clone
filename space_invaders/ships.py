import random

import pygame

from .assets import get_sprite
from .constants import (DEATH_EVENT, ENEMI_SHIP_HEALTH,
                        ENEMI_SHIP_SHOOT_INTERVAL, ENEMI_SHIP_SPEED,
                        LEFT_MOVEMENT_KEYS, RED, RIGHT_MOVEMENT_KEYS,
                        SHIP_HEALTH, SHIP_SPAWN_EVENT, SHIP_SPEED, SHOOT_KEY)
from .lasers import AutoLaser, BasicLaser


def get_damaged(img):
    img = img.copy()
    img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
    return img


class BaseShip(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.last_hit_time = 0

    def fire(self):
        raise NotImplementedError

    def on_collision(self, damage):
        raise NotImplementedError


class Ship(BaseShip):
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
        
        self.health = 0
        self.awarded_points = 1

        self.last_shoot_time = self.game.loop_time

    def _get_image_name(self):
        raise NotImplementedError

    def fire(self):
        raise NotImplementedError

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


class EnemiShip(BaseEnemiShip):
    def __init__(self, game, scene, original_x_position):
        super().__init__(game, scene, original_x_position)

        self.speed = ENEMI_SHIP_SPEED
        self.shoot_interval = random.randint(*ENEMI_SHIP_SHOOT_INTERVAL) / 10

        self.health = random.randint(*ENEMI_SHIP_HEALTH)

        # self.is_sliding = False

    def _get_image_name(self):
        return "enemi-ship"

    def fire(self):
        self.scene.lasers.add(AutoLaser.create(self.game, self.scene, self.rect.midbottom, True))
