import pygame

from .assets import get_sprite
from .base import BaseSprite
from .constants import BASE_SCREEN_SIZE


class BasePowerup(BaseSprite):
    def __init__(self, game, scene, pos):
        super().__init__(game)

        self.image = get_sprite("powerups", self.image_name)
        self.rect = self.image.get_rect(center=pos)

        self.scene = scene

    def action(self, target):
        pass

    def is_colliding(self):
        collision = pygame.sprite.spritecollide(self, [self.game.ship], False)
        if pygame.sprite.spritecollideany(self, collision, pygame.sprite.collide_mask):
            self.action(self.game.ship)
            return True
        return False

    def update(self):
        # first we see if the power-up has left the screen or is colliding
        if (not self.rect.colliderect(self.game.screen_rect)) or self.is_colliding():
            self.kill()

        # now we move it down
        self.rect.y += (self.speed * self.game.screen_height / BASE_SCREEN_SIZE[1]) * self.game.delta


class BaseHealthBoost(BasePowerup):
    def action(self, target):
        target.heal(self.amount)


class HealthBoost(BaseHealthBoost):
    amount = 5
    speed = 5
    image_name = "heart"
