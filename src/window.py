import ctypes

from common import SingletonInstane


class Window(SingletonInstane):

    def __init__(self):
        self.width = 0
        self.height = 0

    def get_center(self) -> tuple[int, int]:
        return (self.width / 2, self.height / 2)

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @size.setter
    def size(self, size: tuple[int, int]):
        self.width = size[0]
        self.height = size[1]

    @staticmethod
    def get_screen_size() -> tuple[int, int]:
        u32 = ctypes.windll.user32
        screen_width = u32.GetSystemMetrics(0)
        screen_height = u32.GetSystemMetrics(1)
        return (screen_width, screen_height)
