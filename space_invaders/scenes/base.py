import operator

import pygame

from ..assets import pixeled
from ..constants import (
    BLACK, FONT_SIZE, TEXT_BLINK_SPEED, TEXT_RESIZE_SPEED, WHITE)
from ..ui import Button


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

        # ui elements
        self.ui_elements = []

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

    def add_button(self, pos, size, text):
        b = Button(self, pos, size, text)
        self.ui_elements.append(b)
        return b

    def process_event(self, event):
        for elem in self.ui_elements:
            elem.process_event(event)

    def update(self):
        for elem in self.ui_elements:
            elem.update()

        self.opacity = self.opacity_op(self.opacity, TEXT_BLINK_SPEED * self.game.delta)
        if self.opacity <= 50:
            self.opacity_op = operator.add
        elif self.opacity >= 255:
            self.opacity_op = operator.sub

        self.size_mod = self.size_op(self.size_mod, TEXT_RESIZE_SPEED * self.game.delta)
        if self.size_mod <= 85:
            self.size_op = operator.add
        elif self.size_mod >= 105:
            self.size_op = operator.sub

    def draw(self):
        for elem in self.ui_elements:
            elem.draw()

    def update_screen(self):
        pygame.display.update(self.to_update)
        self.to_update.clear()


class MenuSceneNoContext(MenuScene):
    pass


class MenuSceneContext(MenuScene):
    def __init__(self, game, text, bottom_text, last_scene):
        super().__init__(game)

        self.last_scene = last_scene
        self.text = text
        self.bottom_text = bottom_text

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

        bottom_text = self.get_text(self.bottom_text, FONT_SIZE / 1.5, opacity=self.opacity / 1.5)
        rect = bottom_text.get_rect(center=(
            self.screen_rect.center[0],
            self.screen_rect.center[1] + FONT_SIZE * 3  # kinda hacky imo, might change later
        ))
        self.screen.blits(((text, text_rect), (bottom_text, rect)))

        self.to_update.extend([text_rect, rect])
