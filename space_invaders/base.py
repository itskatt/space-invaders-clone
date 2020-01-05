import pygame


class BaseSprite(pygame.sprite.Sprite):
    def set_default(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)
