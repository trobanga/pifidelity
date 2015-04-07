from constants import *


class Region(object):

    def __init__(self, _id, x1, y1, x2, y2,
                 color=GRAY,
                 action=None, action_long=None):
        self.x, self.y, self.width, self.height = x1, y1, x2 - x1, y2 - y1
        self._id = _id
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = color
        self.action = action
        self.action_long = action_long

    def __repr__(self):
        s = self._id + " %d %d %d %d" % (self.x, self.y,
                                         self.width, self.height)
        return s

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def pressed(self, x, y, long_pressed=False):
        if x <= (self.x + self.width) \
                and x >= self.x \
                and y <= (self.y + self.height) \
                and y >= self.y:
            print self._id
            if long_pressed:
                if self.action_long:
                    print self._id, "long"
                    return self.action_long(self)
            else:
                if self.action:
                    print self._id, "short"
                    return self.action(self)
