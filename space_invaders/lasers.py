import pygame

from .assets import get_sprite
from .constants import LASER_SPEED, WHITE


class BaseLaser(pygame.sprite.Sprite):
    def __init__(self, game, original_position):
        super().__init__()
        self._get_image()

        self.game = game

        self.rect = self.image.get_rect(center=original_position)

        self.speed = LASER_SPEED

    def _get_image(self):
        pass

    def _move(self):
        pass

    def is_colliding(self):
        return False

    def update(self):
        # first we see if the projectile has left the screen or is colliding
        if (not self.rect.colliderect(self.game.screen_rect)) or self.is_colliding():
            self.kill()

        self._move()


class Laser(BaseLaser):
    def _get_image(self):
        self.image = get_sprite("laser")

    def _move(self):
        self.rect.y = self.rect.y - self.speed

    def is_colliding(self):
        collisions = pygame.sprite.spritecollide(self, self.game.enemi_ships, False)
        if collisions and pygame.sprite.spritecollideany(self, collisions, pygame.sprite.collide_mask):
            [c.on_collision() for c in collisions]
            return True
        return False


class EnemiLaser(BaseLaser):
    def _get_image(self):
        self.image = get_sprite("enemi-laser")

    def _move(self):
        self.rect.y = self.rect.y + self.speed

    def is_colliding(self):
        collision = pygame.sprite.spritecollide(self, [self.game.ship], False)
        if pygame.sprite.spritecollideany(self, collision, pygame.sprite.collide_mask):
            self.game.ship.on_collision()
            return True
        return False
