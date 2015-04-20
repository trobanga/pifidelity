import pygame
import numpy as np
import region
import scene
from constants import *
import mp3database as db
import playlists


class SongScene(scene.Scene):

    class Aspects:

        """
        Different visualizations for songs
        """

        def __init__(self):
            self.artists, self.album, self.albums_from_artist = range(3)
            self.aspects = ['albumartists',
                            'albums',
                            'albums from artist']

        def __getitem__(self, key):
            return self.aspects[key]

    class Songs(region.Region):

        """

        """

        def __init__(self, _id, x1, y1, x2, y2, color=GRAY,
                     title='', action=None, action_long=None):
            super(self.__class__, self).__init__(_id, x1, y1, x2, y2,
                                                 color,
                                                 action=action,
                                                 action_long=action_long)
            self.title = title
            pygame.font.init()
            self.font = pygame.font.Font('freesansbold.ttf', 20)

        def draw(self, screen):
            super(self.__class__, self).draw(screen)
            t = self.font.render(self.title, True, LIGHT_GRAY)
            screen.blit(t, (self.x, self.y))

    # init of SongScene
    def __init__(self, name, play, width=240, height=320, offset=(0, 0),
                 region_size=50,
                 title_size=20,
                 border_size=3,
                 orientation=3,
                 background_color=LIGHT_GRAY):

        self.scene_name = name
        self.screen_width = height
        self.region_size = region_size  # height of fields
        self.title_size = title_size  # offset to print title
        self.border_size = border_size  # size between fields
        self.total_region_size = self.region_size + self.border_size
        self.title_offset = self.title_size + self.border_size

        # three is an empiric number needed to cover all space while scrolling
        self.nof_regions = (height - self.title_offset) / self.region_size + 3

        # calculate surface height
        self.surf_height = self.nof_regions * self.total_region_size \
            + self.region_size

        super(SongScene, self).__init__(width,
                                        self.surf_height,
                                        offset,
                                        orientation,
                                        background_color=background_color,
                                        scrollable=True)

        self.title_region = None
        self.rel_scrolled = 0
        self.scroll_init = self.title_size - self.region_size
        self.cur_scroll_distance = self.scroll_init
        self.scroll_pos = 0
        self.aspects = self.Aspects()  # different
        self.cur_aspect = self.aspects.artists

        self.music_db = db.MusicDB(music_db_file)
        self.music_db.load_db()

        self.play = play  # handle to play.py
        self.pl = playlists.Playlist('the only lonely playlist')

        self.scroll_list = [] + sorted(self.music_db.artist_db.keys())
        # print self.scroll_list
        self.scroll_max = len(self.scroll_list) - 1

        self.title_region = self.Songs(name, 0, 0, self.width, self.title_size,
                                       color=BLACK, title='Artists')
        self.title_region.draw(self)
        self.init_regions()

    def init_regions(self):

        def _y_upper_border(i):
            return i * self.total_region_size

        def _y_lower_border(i):
            return i * self.total_region_size + self.region_size

        regions = [self.Songs("region_" + str(i),
                              0, _y_upper_border(i),
                              self.width, _y_lower_border(i),
                              color=BLACK,
                              action=self.on_pressed,
                              action_long=self.on_pressed_long)
                   for i in range(self.nof_regions)]

        for i, r in enumerate(regions):
            self.add_region(r)
        self.set_name_regions()

    def on_artist(self):
        """ Select artist aspect """
        self.select_aspect(self.aspects.albums_from_artist, name)

    def pressed(self, x, y, long_pressed=False):
        """ Handles pressed signal (mouse button down) """
        if self.orientation == 3:
            x = self.screen_width - x
        if x > self.title_size + self.border_size:
            x = x - self.rel_scrolled - self.title_size + self.region_size
            for r in self.regions:
                ret = r.pressed(y, x, long_pressed)
                if ret:
                    return ret

    def on_pressed_long(self, r):
        """ Action that is done when a region is long_pressed """
        if self.cur_aspect == self.aspects.albums_from_artist:
            self.pl.add_songs(self.music_db.get_album(r.title))
            self.play.set_playlist(self.pl)
            if not self.play.is_playing:
                try:
                    self.play.play_first()
                except Exception, e:
                    print e
            self.select_aspect(self.aspects.artists)
            return "goto_main_lp"
        else:
            return None

    def on_pressed(self, r):
        """ Action that is done when a region is pressed """

        if self.cur_aspect == self.aspects.artists:
            self.select_aspect(self.aspects.albums_from_artist, r.title)
            return None
        elif self.cur_aspect == self.aspects.albums_from_artist:
            self.pl.reset()
            self.pl.add_songs(self.music_db.get_album(r.title))
            self.play.set_playlist(self.pl)
            try:
                self.play.play_first()
            except Exception, e:
                print e
            self.select_aspect(self.aspects.artists)
            return "goto_main"
        else:
            return None

    def get_song_list(self, album):
        return self.music_db.get_album(album)

    def select_aspect(self, aspect, artist=None):
        self.cur_aspect = aspect
        if self.cur_aspect == self.aspects.artists:
            self.scroll_list = [None] + sorted(self.music_db.artist_db.keys())
            self.title_region.name = 'Artists'
        elif self.cur_aspect == self.aspects.album:
            self.scroll_list = [None] + sorted(self.music_db.album_db.keys())
            self.title_region.name = 'Albums'
        elif self.cur_aspect == self.aspects.albums_from_artist:
            self.scroll_list = [
                None] + list(self.music_db.get_albums_from_artist(artist))
            self.title_region.name = artist
        self.scroll_max = len(self.scroll_list) - 1
        self.reset_regions()
        self.set_name_regions()
        self.redraw()

    def reset_regions(self):
        self.rel_scrolled = 0
        self.cur_scroll_distance = self.scroll_init
        self.scroll_pos = 0
        for r in self.regions:
            r.title = ''

    def set_title_region(self, title_region):
        self.title_region = title_region
        self.title_region.draw(self)

    def set_name_regions(self):
        """ Helper function to map song titles to fields """
        for i, r in enumerate(self.regions):
            if self.scroll_pos + i < len(self.scroll_list):
                r.title = self.scroll_list[self.scroll_pos + i]
        self.scrolling_allowed = len(self.scroll_list) > 6

    def scroll_horizontal(self, dx):
        pass

    def update_song_names(self, dy):
        """ f """
        if dy > 0:
            self.scroll_pos = max(0, self.scroll_pos - 1)
        else:
            self.scroll_pos = min(self.scroll_max, self.scroll_pos + 1)

    def scroll_vertical(self, dy):
        if not self.scrolling_allowed:
            return True

        self.rel_scrolled += dy
        if dy > 0:  # scroll up
            if self.scroll_pos == 0 and self.rel_scrolled >= 0:
                self.rel_scrolled -= dy
                self.cur_scroll_distance = self.scroll_init
            else:
                if self.rel_scrolled >= (self.region_size + 3):
                    self.update_song_names(dy)
                    self.set_name_regions()
                    self.rel_scrolled = 0
                    dy = 0
                    self.cur_scroll_distance = self.scroll_init
                self.cur_scroll_distance += dy
                self.redraw()
        else:  # scroll down
            if self.scroll_pos == self.scroll_max - len(self.regions) + 1:
                r = -(self.region_size + 3) - 20
                if self.rel_scrolled <= r:
                    self.rel_scrolled -= dy
                else:
                    self.cur_scroll_distance += dy
            else:
                if self.rel_scrolled <= -(self.region_size + 3):
                    self.update_song_names(dy)
                    self.set_name_regions()
                    self.rel_scrolled = 0
                    dy = 0
                    self.cur_scroll_distance = self.scroll_init
                self.cur_scroll_distance += dy
            self.redraw()
        return True

    def redraw(self):
        super(SongScene, self).redraw()
        self.scroll(dy=self.cur_scroll_distance)

    def update(self, screen):

        # title background
        pygame.draw.rect(
            self, self.background_color, (0, 0, self.width, self.title_offset))
        self.title_region.draw(self)
        s = pygame.transform.rotate(self, 90 * self.orientation)
        if self.orientation == 3:  # rotated to the right
            act_area = (
                self.surf_height - self.screen_width,
                0,
                self.surf_height,
                self.width)
        else:
            act_area = (0, 0, self.height, self.width)
        screen.blit(s, self.pos, act_area)
        pygame.display.update()
