import pygame

from ..assets import pixeled
from ..constants import BLACK, FONT_SIZE, WHITE


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

    def draw(self):
        pass


class PauseScene(BaseScene):
    def __init__(self, game, last_scene):
        super().__init__(game)

        self.last_scene = last_scene

        screen = pygame.Surface(game.screen_size)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))

        font = pixeled(FONT_SIZE * 2)

        pause_text = font.render("Paused", True, WHITE)
        pause_txt_rect = pause_text.get_rect(center=(
            game.screen_width / 2,
            game.screen_height / 2
        ))
        self.screen.blit(pause_text, pause_txt_rect)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.game.is_paused:
                self.game.is_paused = False
                self.game.switch_scene(self.last_scene)


class DeathScene(BaseScene):
    def __init__(self, game, last_scene):
        super().__init__(game)

        self.last_scene = last_scene

        screen = pygame.Surface(game.screen_size)
        screen.fill(BLACK)
        screen.set_alpha(255 / 2)

        self.screen.blit(screen, (0, 0))

        font = pixeled(FONT_SIZE * 2)

        pause_text = font.render("You died", True, WHITE)
        pause_txt_rect = pause_text.get_rect(center=(
            game.screen_width / 2,
            game.screen_height / 2
        ))
        self.screen.blit(pause_text, pause_txt_rect)
