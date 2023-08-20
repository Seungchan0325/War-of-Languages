import pygame

import game_config
import utils


class Game:

    def __init__(self):
        self.config = None

        self._screen_size = None
        self._screen = None
        self._clock = None

        self._running = None

    # return False if failed to init
    def init(self) -> bool:
        self.config = game_config.GameConfig(
            "War of Languages",
            30,
            utils.get_screen_size(),
        )

        pygame.init()
        pygame.display.set_caption(self.config.caption)
        self._screen = pygame.display.set_mode(self.config.screen_size, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        return True

    def loop(self):
        self._running = True

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            pygame.display.flip()

            self._clock.tick(self.config.fps)

    def release(self):
        pygame.quit()
