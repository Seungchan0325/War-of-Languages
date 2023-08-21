import pygame

from system import scene_base
from system.control.button import Button


class MyButton(Button):

    def __init__(self):
        super().__init__(pygame.Rect((0, 0), (100, 100)))

        self._surface = pygame.Surface(self.rect.size)
        self._surface.fill("white")
        self.image = self._surface
        text_color = (255, 0, 255)
        self._title_font = pygame.font.SysFont("arial", 30)
        self._text = (self._title_font.render("", True, text_color),
                      self._title_font.render("Left", True, text_color),
                      self._title_font.render("Middle", True, text_color),
                      self._title_font.render("Right", True, text_color))

        self._text_idx = 0

    def update(self):
        old_text_idx = self._text_idx
        if self.is_clicked(pygame.BUTTON_LEFT):
            self._text_idx = 1
        elif self.is_clicked(pygame.BUTTON_MIDDLE):
            self._text_idx = 2
        elif self.is_clicked(pygame.BUTTON_RIGHT):
            self._text_idx = 3

        if old_text_idx != self._text_idx:
            self.dirty = 1
            self._surface.fill("white")
            self._surface.blit(self._text[self._text_idx], (0, 0))
            self.image = self._surface


class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        super().__init__()

        self.sprites.add(MyButton())

    def update(self):
        self.sprites.update()
