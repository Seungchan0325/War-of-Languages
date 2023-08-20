import ctypes


def get_screen_size() -> tuple[int, int]:
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    return (screen_width, screen_height)
