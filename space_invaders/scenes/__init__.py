import operator

import pygame

from ..assets import pixeled
from ..constants import BLACK, FONT_SIZE, PAUSE_TEXT_BLINK_SPEED, WHITE


class BaseScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

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


class GameScene(BaseScene):
    pass


class PlaylessScene(BaseScene):  # TODO: find a better name
    def __init__(self, game, text, last_scene):
        super().__init__(game)

        self.last_scene = last_scene
        self.text = text

        self.opacity = 255
        self.op = operator.sub

        screen = pygame.Surface(game.screen_size)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))

        self.dark_screen = self.screen.copy()

    def draw_main_text(self, text, opacity):
        font = pixeled(FONT_SIZE * 2)

        main_text = font.render(text, True, WHITE)
        main_txt_rect = main_text.get_rect(center=(
            self.game.screen_width / 2,
            self.game.screen_height / 2
        ))
        if opacity != 255:
            surf = pygame.Surface(main_text.get_size())
            surf.blit(main_text, (0, 0))
            surf.set_colorkey(BLACK)
            surf.set_alpha(opacity)
        else:
            surf = main_text

        self.screen.blit(surf, main_txt_rect)

    def update(self):
        self.opacity = self.op(self.opacity, PAUSE_TEXT_BLINK_SPEED)

        if self.opacity <= 50:
            self.op = operator.add
        elif self.opacity >= 255:
            self.op = operator.sub

    def clear_screen(self):  # TODO: change
        self.screen.blit(self.dark_screen, (0, 0))

    def draw(self):
        self.draw_main_text(self.text, self.opacity)


class PauseScene(PlaylessScene):
    def __init__(self, game, last_scene):
        super().__init__(game, "Paused", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.game.is_paused:
                self.game.is_paused = False
                self.game.switch_scene(self.last_scene)


class DeathScene(PlaylessScene):
    def __init__(self, game, last_scene):
        super().__init__(game, "You died", last_scene)
