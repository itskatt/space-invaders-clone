import pygame

from ..constants import AUTO_LASER_DAMAGE, BASIC_LASER_DAMAGE
from .base import BaseLaser


class BasicLaser(BaseLaser):
    damage = BASIC_LASER_DAMAGE

    def _get_image_name(self):
        return "basic-laser"


class AutoLaser(BaseLaser):
    damage = AUTO_LASER_DAMAGE

    def _get_image_name(self):
        return "auto-laser"
