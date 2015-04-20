import json
import os
import mutagen
import mutagen.mp3
import mutagen.oggvorbis
import mutagen.flac
from mutagen.easyid3 import EasyID3
import itertools


class db_structure(object):
    data_fields = ['albumartist', 'title', 'album', 'tracknumber']

    def __init__(self, path, artist, title, album, tracknumber):
        self.path = path
        self.artist = artist
        self.title = title
        self.album = album
        if tracknumber:
            t = type(tracknumber)
            if t is str or t is unicode:
                s = tracknumber.split('/')[0]
                s = s.split('.')[0]
                self.tracknumber = int(s)
            else:
                self.tracknumber = tracknumber
        else:
            self.tracknumber = None

        self.name_dict = dict(zip(self.data_fields, [self.artist,
                                                     self.title,
                                                     self.album,
                                                     self.tracknumber]))

    def __iter__(self):
        return iter([self.path, self.artist, self.title,
                     self.album, self.tracknumber])

    def __getitem__(self, k):
        if k == 'path':
            return self.path

        return self.name_dict[k]

    def __repr__(self):
        return repr((self.path, self.artist, self.title,
                     self.album, self.tracknumber))

    def to_list(self):
        return (self.path, self.artist, self.title,
                self.album, self.tracknumber)


class MusicDB(object):

    """
    Functions to use from outside:
    scan_library,
    get_albums_from_artist,
    get_artists_from_album,
    get_title, num_songs
    """

    def __init__(self, filename='music.db'):
        self.music_db = list()  # main db
        self.artist_db = set()  # set of all artists
        self.album_db = set()  # set of all albums
        self.title_db = set()
        self.path_db = set()
        self.playlist_db = list()
        self.filename = filename
        self.initialized = False
        self.file_types = frozenset(('mp3', 'flac', 'ogg', 'oga'))

    def num_songs(self):
        return len(self.music_db)

    def save_db(self, db):
        with open(self.filename, 'w') as f:
            l = map(db_structure.to_list, db)
            f.write(json.dumps(l))

    def load_db(self):
        try:
            with open(self.filename, 'r') as f:
                db = json.loads(*f.readlines())
                print len(db)
                # directories, db = db
                db = map(lambda x: db_structure(*x), db)
                self._update_db(db)
        except Exception, e:
            print e

    def scan_library(self, directories=None):
        """
        Scans directories for mp3 files and stops time
        """
        import time
        t = time.time()
        try:
            self._create_db(directories)
        except Exception, e:
            print e
            raise Exception( "Couldn't create DB")
        print 'db created in ', time.time() - t, ' seconds'

    def _parse_dirs(self, directories):
        """
        Parses directories and returns mp3 files
        """
        l = []
        for dirs in directories:
            try:
                d = os.listdir(dirs)
            except os.error, e:
                continue
            # ignore hidden files
            d = filter(lambda x: not x.startswith('.'), d)
            d = map(lambda x: dirs + '/' + x, d)
            for f in d:
                try:
                    if not os.path.isdir(f):
                        ending = f.split('.')[-1].lower()
                        if ending in self.file_types:
                            l.append(f)
                        else:
                            print f
                            print ending, "not supported"
                    else:
                        # parse subdirectories
                        p = self._parse_dirs([f])
                        for x in p:
                            l.append(x)
                except Exception, e:
                    print e
        if not l:
            raise Exception('Parsing failed for {}'.format(directories))
        return l

    def _create_db(self, directories):
        """
        Creates db from directories
        """
        try:
            d = self._parse_dirs(directories)
        except Exception, e:
            print e
        if not d:
            raise Exception('No music in', directories)

        
        def get_tags(f):
            l = [f]
            offset = len(l)
            try:
                t = mutagen.File(f, easy=True)
                for tag in db_structure.data_fields:
                    i = t.get(tag)
                    if i:
                        l.append(i[0])
                    else:
                        l.append(None)
            except Exception, e:
                print f, e
                print db_structure, dir(db_structure)
                for i in xrange(len(l),
                                len(db_structure.data_fields) + offset):
                    l.append(None)
            return l

        d = map(lambda x: db_structure(*get_tags(x)), d)
        
        self._update_db(d)
        self.save_db(d)

    def _find(self, db, wanted, t):
        """
        Finds wanted e.g. 'artist'
        for t e.g. 'song/album'
        in db
        """
        def make_db(db, key):
            s = set()
            for e in db:
                s.add(e[key])
            return s

        d = dict()
        for n in make_db(db, t):
            w = set()
            for a in self._filter_by(db, t, n):
                name = a[wanted]
                if name:
                    w.add(a[wanted])
                else:
                    w.add("unknown")
            d[n] = w
        return d

    def _update_db(self, db):
        """
        Updates DBS with album and artist entries
        """
        self.album_db = self._find(db, 'albumartist', 'album')
        self.artist_db = self._find(db, 'album', 'albumartist')
        self.music_db = db
        self.initialized = True

    def _get(self, key, db, name):
        return self._filter_by(db, key, name)

    def get_album(self, name):
        return self._sort_by(self._get('album', self.music_db, name),
                             'tracknumber')

    def get_artists_from_album(self, name):
        if name not in self.album_db:
            return None
        return self.album_db[name]

    def get_title(self, db, name):
        return self._get('title', db, name)

    def get_albums_from_artist(self, name):
        a = list()
        if name not in self.artist_db:
            return None
        return self.artist_db[name]

    def _sort_by(self, db, t):
        return sorted(db, key=lambda db_structure: db_structure.name_dict[t])

    def _filter_by(self, db, t, name):
        l = []
        return filter(lambda x: name == x.name_dict[t], db)
