import ctypes


def get_monitor_size() -> tuple[int, int]:
    u32 = ctypes.windll.user32
    screen_width = u32.GetSystemMetrics(0)
    screen_height = u32.GetSystemMetrics(1)
    return (screen_width, screen_height)


class SingletonInstane:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance
