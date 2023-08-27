import pygame
from pygame import Surface, Rect
from pygame.sprite import LayeredDirty

from common import SingletonInstane
from game_config import GameConfig


class Screen(SingletonInstane):

    def __init__(self):
        self._screen_area: Rect
        self._screen: Surface

    def init(self):
        # Set the screen size as big as possible
        self._screen_area = Rect(
            (0, 0),
            pygame.display.get_desktop_sizes()[0])

        # Set the display and Set the display to full screen
        self._screen = pygame.display.set_mode(
            self._screen_area.size,
            flags=pygame.FULLSCREEN)

        # Set caption
        caption = GameConfig.instance().name
        pygame.display.set_caption(caption)

    def render(self,
               background: Surface,
               sprites: LayeredDirty):
        # Draw scene
        updates = sprites.draw(self._screen, background)
        pygame.display.update(updates)

    @property
    def area(self) -> Rect:
        return self._screen_area

    @property
    def size(self) -> tuple[int, int]:
        return self._screen_area.size

    @property
    def width(self) -> int:
        return self._screen_area.width

    @property
    def height(self) -> int:
        return self._screen_area.height


# Create a rectangle using the ratio to the screen.
def create_rect(x_ratio: float,
                y_ratio: float,
                w_ratio: float,
                h_ratio: float) -> pygame.Rect:
    screen = Screen.instance()
    x = screen.width * x_ratio
    y = screen.height * y_ratio
    w = screen.width  * w_ratio
    h = screen.height * h_ratio

    return pygame.Rect(x, y, w, h)
