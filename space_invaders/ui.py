import functools

import pygame

from .assets import pixeled
from .constants import WHITE


class BaseUIElement:
    def __init__(self, parent, pos, size):
        self.parent = parent

        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = pos

    def process_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Button(BaseUIElement):
    def __init__(self, parent, pos, size, text, func):
        super().__init__(parent, pos, size)

        self.text = text
        self.func = func

        self.is_highlighted = False

    @functools.lru_cache(2)
    def _get_surf(self, highlited):
        surf = pygame.Surface(self.rect.size)

        if highlited:  # TODO: use color.lerp in pygame 2.0+
            nsurf = pygame.Surface(self.rect.size)
            nsurf.fill(WHITE)
            nsurf.set_alpha(255 / 2)
            surf.blit(nsurf, (0, 0))

        pygame.draw.polygon(
            surf, WHITE,
            [(0, 0), (self.rect.width, 0), self.rect.size, (0, self.rect.height)],
            round(max(self.rect.size) * 0.1)
        )
        font = pixeled(self.rect.height / 2.2)
        txt = font.render(self.text, True, WHITE)
        txt_rect = txt.get_rect(center=(
            round(self.rect.width / 2),
            round(self.rect.height / 2)
        ))
        surf.blit(txt, txt_rect)
        return surf

    def process_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.is_highlighted = True
            else:
                self.is_highlighted = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.func()

    def draw(self):
        self.parent.game.screen.blit(self._get_surf(self.is_highlighted), self.rect)
        self.parent.to_update.append(self.rect)
