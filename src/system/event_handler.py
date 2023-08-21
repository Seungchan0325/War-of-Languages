from collections import defaultdict

import pygame

from common import SingletonInstane


class EventHandler(SingletonInstane):

    def __init__(self):
        self.is_quit = False

        self.is_mouse_up = defaultdict(bool)
        self.is_mouse_down = defaultdict(bool)
        self.is_mouse_pressing = defaultdict(bool)

        self.is_key_up = defaultdict(bool)
        self.is_key_down = defaultdict(bool)
        self.is_key_pressing = defaultdict(bool)

    def init(self):
        pass

    def update(self):
        self.is_mouse_up.clear()
        self.is_mouse_down.clear()

        self.is_key_up.clear()
        self.is_key_down.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_quit = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_mouse_up[event.button] = True
                self.is_mouse_pressing[event.button] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.is_mouse_down[event.button] = True
                self.is_mouse_pressing[event.button] = True

            elif event.type == pygame.KEYUP:
                self.is_key_up[event.key] = True
                self.is_key_pressing[event.key] = False

            elif event.type == pygame.KEYDOWN:
                self.is_key_down[event.key] = True
                self.is_key_pressing[event.key] = True
