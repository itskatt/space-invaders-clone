import logging
from collections import defaultdict
from functools import partial

import pygame

from .constants import ASSETS_DIR, BASE_SCREEN_SIZE

log = logging.getLogger(__name__)

_cache = {}


def load_assets(size):
    if _cache:
        _cache.clear()
    _cache["sprites"] = {}
    _cache["fonts"] = defaultdict(dict)

    for asset in ASSETS_DIR.rglob("*"):
        if asset.parent.name == "sprites":
            sprite = pygame.image.load(str(asset)).convert_alpha()  # change probably
            if not size == BASE_SCREEN_SIZE:
                sprite = pygame.transform.scale(sprite, (
                    round(sprite.get_width() * size[0] / BASE_SCREEN_SIZE[0]),
                    round(sprite.get_height() * size[1] / BASE_SCREEN_SIZE[1])
                ))
            _cache["sprites"][asset.stem] = sprite

            log.debug(f"Loaded {asset.name} at startup")


def get_sprite(name):
    try:
        1
        return _cache["sprites"][name]
    except KeyError:
        log.warning(f"Failed to get sprite {name}")
        return _cache["sprites"]["error"]


def get_font(name, size):
    size = round(size)
    try:
        return _cache["fonts"][name][size]
    except KeyError:
        path = ASSETS_DIR / "fonts" / (name + ".ttf")
        font = pygame.font.Font(str(path), size)
        _cache["fonts"][name][size] = font

        log.debug(f"Loaded and cached font {name} of size {size}")
        return font


pixeled = partial(get_font, "pixeled")
