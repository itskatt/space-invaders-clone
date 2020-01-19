from operator import attrgetter

from .lasers import BasicLaser


class BaseWeapon:
    def __init__(self, ship, is_enemi):
        self.game = ship.game
        self.ship = ship
        self.is_enemi = is_enemi

    def fire(self):
        pass


class BaseSingleBarrel(BaseWeapon):
    def __init__(self, ship, is_enemi, laser_type, pos):
        super().__init__(ship, is_enemi)

        self.laser_type = laser_type
        self.get_pos = attrgetter(pos)

    def fire(self):
        self.game.scene.lasers.add(self.laser_type.create(
            self.game, self.game.scene, self.get_pos(self.ship.rect), self.is_enemi
        ))


class BasicShooter(BaseSingleBarrel):
    def __init__(self, ship, pos):
        super().__init__(ship, False, BasicLaser, pos)
