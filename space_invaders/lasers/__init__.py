from .base import BaseLaser


class BasicLaser(BaseLaser):
    damage = 2
    image_name = "basic-laser"


class AutoLaser(BaseLaser):
    damage = 1
    image_name = "auto-laser"
