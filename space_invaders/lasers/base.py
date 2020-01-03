import pygame

from ..assets import get_sprite
from ..base import BaseSprite
from ..constants import DEFAULT_LASER_SPEED, DEFAULT_LASER_DAMAGE


class BaseLaserTeam:
    pass


def get_friendly_laser(laser):
    class FriendlyLaser(laser, BaseLaserTeam):
        def move(self):
            self.rect.y = self.rect.y - self.speed * self.game.delta

        def is_colliding(self):
            collisions = pygame.sprite.spritecollide(self, self.scene.enemi_ships, False)
            if collisions and pygame.sprite.spritecollideany(self, collisions, pygame.sprite.collide_mask):
                [c.on_collision(self.damage) for c in collisions]
                return True
            return False

    return FriendlyLaser


def get_enemi_laser(laser):
    class EnemiLaser(laser, BaseLaserTeam):
        def move(self):
            self.rect.y = self.rect.y + self.speed * self.game.delta

        def is_colliding(self):
            collision = pygame.sprite.spritecollide(self, [self.game.ship], False)
            if pygame.sprite.spritecollideany(self, collision, pygame.sprite.collide_mask):
                self.game.ship.on_collision(self.damage)
                return True
            return False

    return EnemiLaser


class BaseLaser(BaseSprite):
    def __init__(self, game, scene, original_position):
        super().__init__()
        self.image = get_sprite(
            ("enemi-" if self.__class__.__name__.startswith("Enemi") else "") + self._get_image_name()
        )  # TODO: change

        self.game = game
        self.scene = scene

        self.rect = self.image.get_rect(center=original_position)

        # defaults
        self.set_default("speed", DEFAULT_LASER_SPEED)
        self.set_default("damage", DEFAULT_LASER_DAMAGE)

    def _get_image_name(self):  # its a TODO, ofc
        return self.image_name

    def move(self):
        pass

    def is_colliding(self):
        return False

    def update(self):
        # first we see if the projectile has left the screen or is colliding
        if (not self.rect.colliderect(self.game.screen_rect)) or self.is_colliding():
            self.kill()

        self.move()

    @classmethod
    def create(cls, game, scene, original_position, is_enemi):
        if is_enemi:
            laser = get_enemi_laser(cls)
        else:
            laser = get_friendly_laser(cls)
        return laser(game, scene, original_position)
