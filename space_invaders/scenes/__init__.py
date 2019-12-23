import operator

import pygame

from ..assets import pixeled
from ..constants import BLACK, FONT_SIZE, PAUSE_TEXT_BLINK_SPEED, WHITE


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


class GameScene(BaseScene):
    pass


class PlaylessScene(BaseScene):  # TODO: find a better name
    def __init__(self, game, text, last_scene):
        super().__init__(game)

        self.last_scene = last_scene
        self.text = text

        self.opacity = 255
        self.op = operator.sub

        self.to_update = []

        # create the darkened screen
        screen = pygame.Surface(game.screen_size)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))
        self.to_update.append(self.screen_rect)

        self.dark_screen = self.screen.copy()

    def get_text(self, text, size, opacity):
        font = pixeled(size)

        rendered_text = font.render(text, True, WHITE)

        if opacity != 255:
            surf = pygame.Surface(rendered_text.get_size())
            surf.blit(rendered_text, (0, 0))
            surf.set_colorkey(BLACK)
            surf.set_alpha(opacity)
        else:
            surf = rendered_text

        return surf

    def update(self):
        self.opacity = self.op(self.opacity, PAUSE_TEXT_BLINK_SPEED)

        if self.opacity <= 50:
            self.op = operator.add
        elif self.opacity >= 255:
            self.op = operator.sub

    def clear_screen(self):
        if self.to_update:
            for update in self.to_update:
                self.screen.blit(self.dark_screen.subsurface(update), update)
        else:
            self.screen.blit(self.dark_screen, (0, 0))

    def draw(self):
        text = self.get_text(self.text, FONT_SIZE * 2, self.opacity)
        text_rect = text.get_rect(center=(self.screen_rect.center))
        self.screen.blit(text, text_rect)

        self.to_update.append(text_rect)

    def update_screen(self):
        pygame.display.update(self.to_update)
        self.to_update.clear()


class PauseScene(PlaylessScene):
    def __init__(self, game, last_scene):
        super().__init__(game, "Paused", last_scene)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.game.is_paused:
                self.game.is_paused = False
                self.game.switch_scene(self.last_scene)


class DeathScene(PlaylessScene):  # TODO: press r to restart
    def __init__(self, game, last_scene):
        super().__init__(game, "You died", last_scene)
