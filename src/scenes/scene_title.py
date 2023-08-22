import pygame

from system.systems import Screen
from system import scene_base
from system.control.button import Button


class MyButton(Button):

    def __init__(self, y: int, text: str):
        screen = Screen.instance()

        rect_width = screen.width * 0.28
        rect_height = screen.height * 0.1
        rect = pygame.Rect((0, 0), (rect_width, rect_height))
        rect.centerx = screen.area.centerx
        rect.y = y

        super().__init__(rect)

        text_color = (255, 255, 255)
        title_font = pygame.font.SysFont("arial", int(rect.height * 0.43))
        render_text = title_font.render(text, True, text_color)

        self._render_text = render_text

        surface1 = pygame.Surface(self.rect.size)
        surface1.fill("purple")

        surface2 = pygame.Surface(self.rect.size)
        surface2.fill("red")

        text_rect = render_text.get_rect(center=surface1.get_rect().center)
        surface1.blit(render_text, text_rect)
        text_rect = render_text.get_rect(center=surface2.get_rect().center)
        surface2.blit(render_text, text_rect)

        self._surface = (
            surface1,
            surface2
        )

        self._prev_state = self.is_on_mouse()
        self.image = self._surface[self._prev_state]

    def update(self):
        pass

class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        super().__init__()
        screen = Screen.instance()

        play_button_y = screen.height * 0.48
        settings_button_y = screen.height * 0.63
        self.sprites.add(MyButton(play_button_y, "{ Play }"))
        self.sprites.add(MyButton(settings_button_y, "{ Settings }"))

    def update(self):
        self.sprites.update()
