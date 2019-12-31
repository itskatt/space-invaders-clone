import pygame

from ..assets import get_sprite
from ..constants import BASE_LASER_SPEED


def _friendly_move(self):
    self.rect.y = self.rect.y - self.speed * self.game.delta


def _friendly_is_colliding(self):
    collisions = pygame.sprite.spritecollide(
        self, self.scene.enemi_ships, False)
    if collisions and pygame.sprite.spritecollideany(self, collisions, pygame.sprite.collide_mask):
        [c.on_collision(self.damage) for c in collisions]
        return True
    return False


def _enemi_move(self):
    self.rect.y = self.rect.y + self.speed * self.game.delta


def _enemi_is_colliding(self):
    collision = pygame.sprite.spritecollide(self, [self.game.ship], False)
    if pygame.sprite.spritecollideany(self, collision, pygame.sprite.collide_mask):
        self.game.ship.on_collision(self.damage)
        return True
    return False


_friendly_dict = {
    "move": _friendly_move,
    "is_coliding": _friendly_is_colliding
}

_enemi_dict = {
    "move": _enemi_move,
    "is_coliding": _enemi_is_colliding
}


class BaseLaserTeam:
    pass


class BaseLaser(pygame.sprite.Sprite):
    def __init__(self, game, scene, original_position):
        super().__init__()
        self.image = get_sprite(
            ("enemi-" if self.__class__.__name__.startswith("Enemi") else "") + self._get_image_name()
        )

        self.game = game
        self.scene = scene

        self.rect = self.image.get_rect(center=original_position)

        self.speed = BASE_LASER_SPEED

        if not hasattr(self, "damage"):  # TODO: change/remove
            self.damage = 0

    def _get_image_name(self):
        pass

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
            laser = type("Enemi" + cls.__name__, (cls, BaseLaserTeam), _enemi_dict)
        else:
            laser = type("Friendly" + cls.__name__, (cls, BaseLaserTeam), _friendly_dict)
        return laser(game, scene, original_position)  # FIXME: overwriting is not happening proprely
