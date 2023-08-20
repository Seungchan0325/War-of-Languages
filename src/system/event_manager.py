import pygame


class EventManager:

    def __init__(self):
        self._is_quit = False

        self._is_mouse_up = {}
        self._is_mouse_down = {}
        self._is_mouse_pressing = {}

        self._is_key_up = {}
        self._is_key_down = {}
        self._is_key_pressing = {}

    def update(self):
        self._is_mouse_up.clear()
        self._is_mouse_down.clear()

        self._is_key_up.clear()
        self._is_key_down.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_quit = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self._is_mouse_up[event.button] = True
                self._is_mouse_pressing[event.button] = False

            elif event.type == pygame.MOUSEBUTTONUP:
                self._is_mouse_down[event.button] = True
                self._is_mouse_pressing[event.button] = True

            elif event.type == pygame.KEYUP:
                self._is_key_up[event.key] = True
                self._is_key_pressing[event.key] = False

            elif event.type == pygame.KEYDOWN:
                self._is_key_down[event.key] = True
                self._is_key_pressing[event.key] = True

    def is_quit(self) -> bool:
        return self._is_quit

    def get_mouse_pos(self) -> tuple[int, int]:
        return pygame.mouse.get_pos()

    def is_mouse_up(self, button: int) -> bool:
        return self._is_mouse_up.get(button, False)

    def is_mouse_down(self, button: int) -> bool:
        return self._is_mouse_down.get(button, False)

    def is_mouse_pressing(self, button: int) -> bool:
        return self._is_mouse_pressing.get(button, False)

    # key is pygame constant
    def is_key_up(self, key: int) -> bool:
        return self._is_key_up.get(key, False)

    # key is pygame constant
    def is_key_down(self, key: int) -> bool:
        return self._is_key_down.get(key, False)

    # key is pygame constant
    def is_key_pressing(self, key: int) -> bool:
        return self._is_key_pressing.get(key, False)
