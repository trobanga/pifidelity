from collections import deque


class Playlist(object):

    """
    Class for handling playlists
    """

    def __init__(self, name):
        self.name = name
        self.pl = deque()
        self.idx = -1
        self.loop = False
        self.cur_song = None

    def first(self):
        """ Sets cur_song to first song in list """
        if self.is_empty():
            self._no_pl_exception()
        self.cur_song = self.pl[0]
        self.idx = 0

    def reset(self):
        self.idx = -1
        self.pl = deque()

    def clear(self):
        self.pl = deque()

    def add_songs(self, songs):
        for song in songs:
            self.pl.append(song)

    def remove_song(self, idx):
        self.pl.pop(idx)

    def next_song(self):
        if self.is_empty():
            self._no_pl_exception()
        self.idx += 1
        if self.idx >= len(self.pl):
            if self.loop:
                self.idx = 0
                self.cur_song = self.pl[0]
            else:
                self.idx = -1
                self.cur_song = None
        else:
            self.cur_song = self.pl[self.idx]

    def prev_song(self):
        if self.is_empty():
            self._no_pl_exception()
        self.idx -= 1
        if self.idx < 0:
            self.idx = 0
        self.cur_song = self.pl[self.idx]

    def is_empty(self):
        return len(self.pl) == 0
    
    def _no_pl_exception(self):
        raise Exception('playlist empty')

    def debug(self):
        print self.pl
        print self.idx
        print self.cur_song
