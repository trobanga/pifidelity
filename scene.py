import pygame
from constants import *


class Scene(pygame.Surface):

    def __init__(self, width=240, height=320,
                 offset=(0, 0),
                 orientation=3,
                 background_color=BLACK, scrollable=False):
        super(Scene, self).__init__((width, height))
        self.height = height
        self.width = width
        self.orientation = orientation
        self.background_color = background_color
        self.fill(self.background_color)
        self.pos = [offset[1], offset[0]]  # Position on 'parent' screen
        self.regions = list()
        self.offset = offset
        self.scrolling_allowed = scrollable

    def add_region(self, r):
        r.draw(self)
        self.regions.append(r)

    def scroll_horizontal(self, dx):
        return self.scrolling_allowed

    def scroll_vertical(self, dy):
        return self.scrolling_allowed

    def redraw(self):
        self.fill(self.background_color)
        for r in self.regions:
            r.draw(self)

    def update(self, screen):
        screen.fill(self.background_color)
        self.redraw()
        s = pygame.transform.rotate(self, 90)
        screen.blit(s, self.pos)
        pygame.display.update()

    def pressed(self, x, y, long_pressed=False):
        pass
