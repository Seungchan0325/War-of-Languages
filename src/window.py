import ctypes


class Window:

    def __init__(self):
        self.width = 0
        self.height = 0

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @size.setter
    def size(self, size: tuple[int, int]):
        self.width = size[0]
        self.height = size[1]

    def get_screen_size(self) -> tuple[int, int]:
        u32 = ctypes.windll.user32
        screen_width = u32.GetSystemMetrics(0)
        screen_height = u32.GetSystemMetrics(1)
        return (screen_width, screen_height)
