import scene
import region
import partyzone
from constants import *


class MainRegions(region.Region):
    def __init__(self,  name, x1, y1, x2, y2,
                 color=GRAY,
                 high_color=LIGHT_GRAY,
                 action=None, action_long=None,
                 highlighting=False,
                 img=None):

        super(self.__class__, self).__init__(name, x1, y1, x2, y2,
                                             color,
                                             action=action,
                                             action_long=action_long)
        self.high_color = high_color
        self.high_time = 0
        self.high_duration = 200  # ms
        self.img = None
        if img:
            try:
                self.img = pygame.image.load(img)
                self.img.convert_alpha()
                self.img = pygame.transform.rotate(self.img, 180)
            except pygame.error, msg:
                print msg

    def draw(self, screen):
        if pygame.time.get_ticks() < self.high_time:
            # draw highlighted
            self.color = self.high_color
        else:
            self.color = GRAY
        super(self.__class__, self).draw(screen)

        if self.img:
            screen.blit(self.img, (self.x, self.y))

    def pressed(self, x, y, long_pressed=False):
        x = 240 - x  # fix for rotated coordinates
        if x <= (self.x + self.width) \
            and x >= self.x \
            and y <= (self.y + self.height) \
            and y >= self.y:
            # set highlight time
            self.high_time = pygame.time.get_ticks() + self.high_duration
        return super(self.__class__, self).pressed(x, y, long_pressed)
        
    
class MainScene(scene.Scene):

    def __init__(self,
                 play,
                 width=240, height=320,
                 offset=(0, 0),
                 orientation=3,
                 background_color=BLACK):
        super(MainScene, self).__init__(width,
                                        height,
                                        offset,
                                        orientation,
                                        background_color=background_color,
                                        scrollable=False)
        self.orientation = orientation
        self.play = play
        self.party_region = partyzone.PartyZone("party_zone", 3, 82, 237, 238,
                            action=self.party_zone, orientation=self.orientation)
        self.add_regions()

    def add_regions(self):
        if self.orientation == 3:
            regions = [
                # first row
                MainRegions("volume up", 3, 241, 79, 317,
                            action=self.vol_up,
                            img='./icons/isometric_vol_up.png'),
                MainRegions("volume mute", 82, 241, 158, 317,
                            action=self.mute,
                            img='./icons/isometric_mute.png'),
                MainRegions("volume down", 161, 241, 237, 317,
                            action=self.vol_down,
                            img='./icons/isometric_vol_dn.png'),
                # second row
                self.party_region,
                # third row
                MainRegions("next song", 3, 3, 79, 79,
                            action=self.next_song,
                            img='./icons/isometric_skip.png'),
                MainRegions("song selector", 82, 3, 158, 79,
                            action=self.song_select,
                            img='./icons/isometric_play.png'),
                MainRegions("prev song", 161, 3, 237, 79,
                            action=self.prev_song,
                            img='./icons/isometric_rewind.png')
               ]
        else:
            regions = [
                # first row
                MainRegions("volume up", 161, 3, 237, 79,
                            action=self.vol_up),
                MainRegions("volume mute", 82, 3, 158, 79,
                            action=self.mute),
                MainRegions("volume down", 3, 3, 79, 79,
                            action=self.vol_down),
                # second row
                MainRegions("play", 3, 82, 237, 238,
                            action=self.party_zone),
                # third row
                MainRegions("next song", 161, 241, 237, 317,
                            action=self.next_song),
                MainRegions("song selector", 82, 241, 158, 317,
                            action=self.song_select),
                MainRegions("prev song", 3, 241, 79, 317,
                            action=self.prev_song)
               ]

        for r in regions:
            self.add_region(r)

    def mute(self, r):
        self.play.mute()

    def vol_up(self, r):
        self.play.vol_up()

    def vol_down(self, r):
        self.play.vol_down()

    def party_zone(self, r):
        if self.play.is_playing:
            self.play.stop()
        else:
            try:
                self.play.start()
            except Exception, e:
                return "goto_song_select"

    def song_select(self, r):
        return "goto_song_select"

    def prev_song(self, r):
        self.play.prev_song()

    def next_song(self, r):
        self.play.next_song()

    def pressed(self, x, y, long_pressed=False):
        for r in self.regions:
            t = r.pressed(y, x, long_pressed)
            if t:
                return t
