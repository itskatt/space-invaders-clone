import functools

import pygame

from .constants import RED


@functools.lru_cache()
def get_damaged(img):  # TODO: move to own file
    img = img.copy()
    img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
    return img