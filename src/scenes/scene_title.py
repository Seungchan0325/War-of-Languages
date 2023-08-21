import pygame

from system import scene_base
from system.control.button import Button
from window import Window


class MyButton(Button):

    def __init__(self):
        super().__init__(pygame.Rect((Window.instance().get_center(), (100, 100))))
        text_color = (255, 255, 255)
        self._title_font = pygame.font.SysFont("arial", 30)
        self._text_idx = 0
        self._text = (self._title_font.render("", True, text_color),
                      self._title_font.render("Left", True, text_color),
                      self._title_font.render("Middle", True, text_color),
                      self._title_font.render("Right", True, text_color))

    def update(self):
        if self.is_left_clicked():
            self._text_idx = 1
        elif self.is_middle_clicked():
            self._text_idx = 2
        elif self.is_right_clicked():
            self._text_idx = 3

    def render(self, screen: pygame.Surface):
        screen.blit(self._text[self._text_idx], self._rect.topleft)


class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        self._my_button = MyButton()

    def update(self):
        self._my_button.update()

    def render(self, screen: pygame.Surface):
        screen.fill("black")
        self._my_button.render(screen)
