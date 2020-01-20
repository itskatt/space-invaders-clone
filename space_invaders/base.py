import pygame


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game

    def set_default(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)
