# -*- coding: utf-8 -*-
import pygame
import os
import xml.etree.ElementTree as ET
from pygame.locals import *
from constants import *

class BlinkenMemory(object):
    def __init__(self, ncols, nrows):
        # self._map = [[False for i in range(ny)] for j in range(nx)]
        self.frame = [[BLACK for i in range(ncols)] for j in range(nrows)]
        self.frame_duration = 100 # in ms
        
    def __getitem__(self, idx):
        return self.frame[idx]
        
    def print_map(self):
        for i in self._map:
            for j in i:
                print(j)
            print()

    def get_pixel(self, ix, iy):
        return self.frame[iy][ix]
    

class Blinkentanz(pygame.Surface):
    """
    Draws area for Blinkenlights.
    Reads BMLs.
    """

    def __init__(self, width, height,
                 fcolor_on=WHITE,
                 fcolor_off=BLACK,
                 bcolor=GRAY,
                 orientation=3):
        # width and height of total available area
        self.tot_width = width
        self.tot_height = height

        self.orientation = orientation
        # nof of pixels in x an y
        self.nx = 1
        self.ny = 1

        # bmls
        self.metadata = dict()
        self.idx_bframe = 0
        self.nof_bframes = 1
        self.bframes = [BlinkenMemory(self.nx, self.ny)]
        
        # colors
        self.fcolor_on = fcolor_on
        self.fcolor_off = fcolor_off
        self.bcolor = bcolor

    def update_pixel_size(self):
        self.pixel_size = min(int(self.tot_width / self.nx),
                              int(self.tot_height / self.ny))
        self.xoffset = (self.tot_width - self.pixel_size * self.nx) / 2
        self.yoffset = (self.tot_height - self.pixel_size * self.ny) / 2
        self.field_size = (self.pixel_size * self.nx,
                           self.pixel_size * self.ny)

        # width and height of area occupied by pixels
        self.width = self.nx * self.pixel_size + 1
        self.height = self.ny * self.pixel_size + 1
        super(Blinkentanz, self).__init__((self.width, self.height))

        # calculate border for pixels
        self.pixel_border_ratio = 0.9
        self.pixel_border_size = int(self.pixel_size * \
                                 (1.-self.pixel_border_ratio))
        self.pixel_border_size = max(self.pixel_border_size, 1)

    def get_frame_duration(self):
        """
        Returns duration of current frame
        """
        return self.bframes[self.idx_bframe].frame_duration

    def next(self):
        """
        Set frame idx to next and draw frame
        """
        self.idx_bframe += 1
        if self.idx_bframe >= self.nof_bframes:
            self.idx_bframe = 0
        self.draw_dancefloor()
           
    def goto_frame(self, idx):
        """
        Set frame idx and draw frame
        """
        if idx < self.nof_bframes and idx >= 0:
            self.idx_bframe = idx
            self.draw_dancefloor()
             
    def draw_background(self):
        self.fill(self.bcolor)

    def draw_dancefloor(self):
        """
        Draws whole blinkenlights area.
        """
        for ix in range(self.nx):
            for iy in range(self.ny):
                self.draw_pixel(ix, iy)
            
    def draw_pixel(self, ix, iy):
        if self.orientation == 3:
            x = (self.nx - ix - 1) * self.pixel_size
            y = (self.ny - iy - 1) * self.pixel_size
        else:
            x = ix * self.pixel_size
            y = iy * self.pixel_size
        fg = pygame.Rect(x + self.pixel_border_size, 
                              y + self.pixel_border_size, 
                              self.pixel_size - self.pixel_border_size, 
                              self.pixel_size - self.pixel_border_size)
        pygame.draw.rect(self, self.bframes[self.idx_bframe].get_pixel(ix, iy), fg)

    def read_bml(self, f):
        """
        Read bml format 
        """
        f = os.path.abspath(f)
        data = ET.parse(f)
        r = data.getroot()
        if(r.tag != 'blm'):
            print('no bml data file')
            return
        settings = r.attrib
        self.nx = int(settings["width"])
        self.ny = int(settings["height"])
        channels = settings.get("channels")
        if not channels:
            channels = 1
        else:
            channels = int(channels)
        bits = int(settings.get("bits"))
        self.metadata = r.find('header')
        self.idx_bframe = -1
        self.nof_bframes = 0
        self.bframes = list()
        
        for frame in r.findall('frame'):
            self.bframes.append(BlinkenMemory(self.nx, self.ny))
            self.idx_bframe += 1
            self.nof_bframes += 1
            for iy, row in enumerate(frame.findall('row')):
                def chunks(l, n):
                    for i in range(0, len(l), n):
                        yield l[i:i+n]
                       
                if channels == 3:
                    if bits > 4:
                        raw_row_data_chunks = chunks(row.text, 6)
                    else:
                        raw_row_data_chunks = chunks(row.text, 3)
                    for ix, c in enumerate(raw_row_data_chunks):
                        if bits == 4: # will prob. never be the case
                            k = 2**(8-bits)
                            b = k - 1
                            c =  [hex(k * int(x+x, 16) + b) for x in c]
                            c = c[0] + c[1] + c[2] 
                        c = int(c, 16) 
                        if  c > 0:
                            self.bframes[self.idx_bframe][iy][ix] = c
                        else:
                            self.bframes[self.idx_bframe][iy][ix] = BLACK
                elif channels == 1:
                    if bits > 4:
                        print("Warning: not implemented yet")
                    k = 2**(8-bits)
                    b = k - 1
                    for ix, c in enumerate(row.text):
                        
                        c =  k * int(c, 16) + b
                        if c > b:
                            self.bframes[self.idx_bframe][iy][ix] = (c, c, c)
                        else:
                            self.bframes[self.idx_bframe][iy][ix] = BLACK
            self.bframes[self.idx_bframe].frame_duration = \
              int(frame.attrib["duration"])
        self.update_pixel_size()
        self.draw_background()
        self.goto_frame(0) 
