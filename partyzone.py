import scene
import region
import blinkentanz
import os
import random
from constants import *


"""
Draws the blinkentanz area and manages bmls and loading the next frame
"""


class PartyZone(region.Region):
    def __init__(self,  name, x1, y1, x2, y2,
                 fcolor_on=WHITE,
                 fcolor_off=BLACK,
                 bcolor=GRAY,
                 action=None,
                 action_long=None,
                 orientation=3):

        super(self.__class__, self).__init__(name, x1, y1, x2, y2,
                                             bcolor,
                                             action=action,
                                             action_long=action_long)
        self.partying = False  # meh, lame
        self.partytime = 0  # time since start in ms
        self.bmls = self._parse_bmls(bml_directories)
        self.bt = blinkentanz.Blinkentanz(x2-x1,
                                          y2-y1,
                                          fcolor_on,
                                          fcolor_off,
                                          bcolor,
                                          orientation)
        self.frame_duration = 0
        self.load_bml(bml=bml_directories[0] + "/pifidelity.bml")

    def add_time(self, t):
        if self.partying:
            self.partytime += t

    def load_bml(self, fails=0, max_fails=3, bml=None):
        if fails == max_fails:
            print 'tried three times loading a bml. Giving up.'
        if not bml:
            bml = self.rand_bml()
        try:
            self.bt.read_bml(bml)
            self.cur_bml = bml
            self.frame_duration = self.bt.get_frame_duration()
        except Exception, e:
            print e
            self.load_bml(fails=fails+1)
            self.cur_bml = None
            
    def rand_bml(self):
        """
        Selects random bml from self.bmls
        """
        return random.sample(self.bmls, 1)[0]

    def start(self):
        self.partying = True

    def stop(self):
        self.partying = False
        
    def draw(self, screen):
        if self.partytime > self.frame_duration:
            self.partytime = 0
            if self.bt.next():
                self.load_bml()
                                
            self.frame_duration = self.bt.get_frame_duration()
        
        screen.blit(self.bt, [self.x+self.bt.xoffset, self.y+self.bt.yoffset])
        
    def _parse_bmls(self, directories):
        """
        Parses through directories and its subdirectories and returns list with bmls.
        """
        bmls = []
        for bml_dir in bml_directories:
            try:
                d = os.listdir(bml_dir)
            except os.error, e:
                continue
            d = filter(lambda x: not x.startswith('.'), d)
            d = map(lambda x: bml_dir + '/' + x, d)
            for f in d:
                try:
                    if not os.path.isdir(f):
                        ending = f.split('.')[-1].lower()
                        if ending == 'bml':
                            bmls.append(f)
                    else:
                        # parse subdirectories
                        p = self._parse_bmls([f])
                        for x in p:
                            bmls.append(x)
                except Exception, e:
                    print e
        if not bmls:
            raise Exception('No bmls in {}'.format(directories))
        return bmls
