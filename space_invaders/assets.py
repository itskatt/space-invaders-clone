import logging
from collections import defaultdict
from functools import partial

import pygame

from .constants import ASSETS_DIR, BASE_SCREEN_SIZE

log = logging.getLogger(__name__)

_cache = {}


def nested_dict():
    return defaultdict(nested_dict)


def construct_dict_call(keys):
    return "".join([f"['{key}']" for key in keys])


def load_assets(size):
    if _cache:
        _cache.clear()

    _cache["sprites"] = nested_dict()
    _cache["fonts"] = defaultdict(dict)

    _load_sprites(size)


def _load_sprites(size):
    for asset in (ASSETS_DIR / "sprites").rglob("*"):
        if asset.is_dir():
            continue

        sprite = pygame.image.load(str(asset)).convert_alpha()  # change probably
        if not size == BASE_SCREEN_SIZE:
            sprite = pygame.transform.scale(sprite, (
                round(sprite.get_width() * size[0] / BASE_SCREEN_SIZE[0]),
                round(sprite.get_height() * size[1] / BASE_SCREEN_SIZE[1])
            ))
        parts = list(asset.parts[asset.parts.index("sprites"):])
        parts[-1] = asset.stem
        exec("_cache" + construct_dict_call(parts) + "= sprite", globals(), locals())

        log.debug(f"Loaded {asset.name} at startup")


def get_sprite(*name):
    possible_sprite = eval("_cache['sprites']" + construct_dict_call(name), globals(), locals())
    if isinstance(possible_sprite, defaultdict):
        log.warning(f"Failed to get sprite {'/'.join(name)}")
        return _cache["sprites"]["error"]
    return possible_sprite


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
