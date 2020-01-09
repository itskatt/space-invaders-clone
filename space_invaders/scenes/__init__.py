import functools

import pygame

from ..constants import (BLACK, FONT_SIZE, PAUSE_KEY, RESTART_KEY, START_KEY,
                         WINDOW_TITLE)
from .base import MenuSceneContext, MenuSceneNoContext


class WelcomeScene(MenuSceneNoContext):
    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == START_KEY:
                self.game.start_new_game()

    def clear_screen(self):
        if self.to_update:
            for update in self.to_update:
                self.screen.fill(BLACK, update)
        else:
            self.screen.fill(BLACK)

    def cleanup(self):
        self._get_main_text.cache_clear()

    @functools.lru_cache()
    def _get_main_text(self, size_mod):
        main_text = self.get_text(WINDOW_TITLE, (FONT_SIZE * 4))
        main_text = pygame.transform.smoothscale(main_text, (
            round(main_text.get_width() * (size_mod / 100)),
            round(main_text.get_height() * (size_mod / 100))
        ))
        return main_text

    def draw(self):
        main_text = self._get_main_text(self.size_mod)
        main_txt_rect = main_text.get_rect(center=(
            self.screen_rect.center[0],
            self.screen_rect.center[1] / 2.5
        ))
        play_text = self.get_text("Press ENTER to play", FONT_SIZE, opacity=self.opacity)
        play_txt_rect = play_text.get_rect(center=(self.screen_rect.center))

        self.screen.blits(((main_text, main_txt_rect), (play_text, play_txt_rect)))

        main_txt_rect.inflate_ip(main_txt_rect.width * 1.5, 0)
        self.to_update.extend([main_txt_rect, play_txt_rect])


class PauseScene(MenuSceneContext):
    def __init__(self, game, last_scene):
        super().__init__(game, "Paused", "(press ESCAPE to unpause)", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == PAUSE_KEY and self.game.is_paused:
                self.game.is_paused = False
                self.game.switch_scene(self.last_scene)


class DeathScene(MenuSceneContext):
    def __init__(self, game, last_scene):
        super().__init__(game, "You died", "Press R to restart", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == RESTART_KEY:
                self.game.start_new_game()
