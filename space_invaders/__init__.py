"""
Space invaders game.
"""
import argparse
import logging
import os
import sys
import time
import traceback
from contextlib import contextmanager

import pygame

from .constants import DIR, WINDOW_TITLE
from .game import Game

log = logging.getLogger(__name__)


@contextmanager
def setup_log():  # FIXME
    try:
        loggers = [
            log,
            # ...
        ]
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("[{levelname:^7}] {name}: {message}", style="{")
        handler.setFormatter(fmt)
        for log_ in loggers:
            log_.setLevel(logging.INFO)
            log_.addHandler(handler)

        yield
    finally:
        for log_ in loggers:
            for hnd in log_.handlers:
                hnd.close()
                log_.removeHandler(hnd)


def parse_args():
    parser = argparse.ArgumentParser(
        WINDOW_TITLE,
        description="The game's cli"
    )
    parser.add_argument(
        "--no-reports",
        help="Don't save crash reports when the game crashes.",
        action="store_true",
        default=False
    )
    return parser.parse_args()


def main():
    """
    The main function, sets everyting up and runs the game.
    """
    with setup_log():
        args = parse_args()

        os.environ["SDL_VIDEO_CENTERED"] = "1"  # place the game window at the center of the screen
        status = pygame.init()
        log.info(f"Pygame init status {status}")
        log.info(f"SDL version: {(pygame.get_sdl_version())}")

        try:
            game = Game()
            game.mainloop()
        except Exception:
            log.exception("An exception occured:")

            if not args.no_reports:  # TODO: save to a different path
                with open(DIR / f"CRASH_{round(time.time())}.txt", "w", encoding="utf=8") as f:
                    traceback.print_exc(file=f)
                    log.info("Created crash report")

        pygame.quit()
