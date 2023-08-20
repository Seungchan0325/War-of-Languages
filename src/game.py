import pygame

import utils


class Game:

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Game, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):

            self._caption = "War of Languages"
            self._fps = 30

            cls._init = True

    # return False if failed to init
    def init(self) -> bool:
        self._screen_size = utils.get_screen_size()

        pygame.init()
        pygame.display.set_caption(self._caption)
        self._screen = pygame.display.set_mode(self._screen_size, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        return True

    def loop(self):
        self._running = True

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            self._screen.fill("white")

            pygame.display.flip()

            self._clock.tick(self._fps)

    def release(self):
        pygame.quit()