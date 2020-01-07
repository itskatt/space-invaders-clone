import functools

import pygame

from .constants import RED


@functools.lru_cache()
def get_damaged(img):
    img = img.copy()
    img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
    return img


@functools.lru_cache()
def get_rotated(img, angle):
    return pygame.transform.rotate(img, angle)
