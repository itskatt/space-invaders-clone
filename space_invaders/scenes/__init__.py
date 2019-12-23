import functools
import operator

import pygame

from ..assets import pixeled
from ..constants import (BLACK, FONT_SIZE, PAUSE_KEY, RESTART_KEY,
                         TEXT_BLINK_SPEED, TEXT_RESIZE_SPEED, WHITE,
                         WINDOW_TITLE)


class BaseScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_rect = game.screen_rect

    def cleanup(self):
        pass

    def process_event(self, event):
        pass

    def update(self):
        pass

    def clear_screen(self):
        pass

    def draw(self):
        pass

    def update_screen(self):
        pygame.display.flip()


class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)

        # opactity changing effect
        self.opacity = 255
        self.opacity_op = operator.sub

        # size changing effect
        self.size_mod = 100
        self.size_op = operator.add

        # regions to update
        self.to_update = []

    def get_text(self, text, size, color=WHITE, opacity=255, antialias=True):
        font = pixeled(size)

        rendered_text = font.render(text, antialias, WHITE)

        if opacity != 255:
            surf = pygame.Surface(rendered_text.get_size())
            surf.blit(rendered_text, (0, 0))
            surf.set_colorkey(BLACK)
            surf.set_alpha(opacity)
        else:
            surf = rendered_text

        return surf

    def update(self):
        self.opacity = self.opacity_op(self.opacity, TEXT_BLINK_SPEED)
        if self.opacity <= 50:
            self.opacity_op = operator.add
        elif self.opacity >= 255:
            self.opacity_op = operator.sub

        self.size_mod = self.size_op(self.size_mod, TEXT_RESIZE_SPEED)
        if self.size_mod <= 90:
            self.size_op = operator.add
        elif self.size_mod >= 110:
            self.size_op = operator.sub

    def update_screen(self):
        pygame.display.update(self.to_update)
        self.to_update.clear()


class MenuSceneNoContext(MenuScene):
    pass


class WelcomeScene(MenuSceneNoContext):
    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.game.start_new_game()

    def clear_screen(self):
        if self.to_update:
            for update in self.to_update:
                self.screen.fill(BLACK, update)
        else:
            self.screen.fill(BLACK)

    def cleanup(self):
        self.get_main_text.cache_clear()

    @functools.lru_cache()
    def get_main_text(self, size_mod):
        main_text = self.get_text(WINDOW_TITLE, (FONT_SIZE * 4))
        main_text = pygame.transform.smoothscale(main_text, (
            round(main_text.get_width() * (size_mod / 100)),
            round(main_text.get_height() * (size_mod / 100))
        ))
        return main_text

    def draw(self):
        main_text = self.get_main_text(self.size_mod)
        main_txt_rect = main_text.get_rect(center=(
            self.screen_rect.center[0],
            self.screen_rect.center[1] / 2.5
        ))
        play_text = self.get_text("Press any key to play", FONT_SIZE, opacity=self.opacity)
        play_txt_rect = play_text.get_rect(center=(self.screen_rect.center))

        self.screen.blit(main_text, main_txt_rect)
        self.screen.blit(play_text, play_txt_rect)

        main_txt_rect.inflate_ip(main_txt_rect.width * 1.5, 0)
        self.to_update.extend([main_txt_rect, play_txt_rect])


class MenuSceneContext(MenuScene):
    def __init__(self, game, text, last_scene):
        super().__init__(game)

        self.last_scene = last_scene
        self.text = text

        # create the darkened screen
        screen = pygame.Surface(game.screen_size)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))
        self.to_update.append(self.screen_rect)

        self.dark_screen = self.screen.copy()

    def clear_screen(self):
        if self.to_update:
            for update in self.to_update:
                self.screen.blit(self.dark_screen.subsurface(update), update)
        else:
            self.screen.blit(self.dark_screen, (0, 0))

    def draw(self):
        text = self.get_text(self.text, FONT_SIZE * 2, opacity=self.opacity)
        text_rect = text.get_rect(center=(self.screen_rect.center))
        self.screen.blit(text, text_rect)

        self.to_update.append(text_rect)


class PauseScene(MenuSceneContext):
    def __init__(self, game, last_scene):
        super().__init__(game, "Paused", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == PAUSE_KEY and self.game.is_paused:
                self.game.is_paused = False
                self.game.switch_scene(self.last_scene)


class DeathScene(MenuSceneContext):
    def __init__(self, game, last_scene):
        super().__init__(game, "You died", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == RESTART_KEY:
                self.game.start_new_game()

    def draw(self):
        super().draw()

        text = self.get_text("Press R to restart", FONT_SIZE / 1.5, opacity=self.opacity / 1.5)
        rect = text.get_rect(center=(
            self.screen_rect.center[0],
            self.screen_rect.center[1] + FONT_SIZE * 3  # kinda hacky, might change later
        ))
        self.screen.blit(text, rect)

        self.to_update.append(rect)
