#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import sys
import os
import threading
import stat
from constants import *
import main_scene
import song_select_scene
import numpy as np
from collections import deque
import play
import RPi.GPIO as GPIO

print 'PID', os.getpid()
print sys.platform
print os.name


class Pyfidelity(object):

    def __init__(self, debug=False, orientation=3,
                 screen_width=320, screen_height=240):
        self.debug = debug
        if not debug:
            # do all raspberry pi related stuff
            self.init_touchscreen()
            self.GPIO_init()
            self.ext_button_init(23)

        # only 1 (rot left) and 3 (rot right) supported
        self.orientation = orientation
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.fps_clock = pygame.time.Clock()

        if not debug:
            pygame.mouse.set_visible(False)


        self.playing = False  # playing music
        self.done = True  # program is running

        self.ext_button_time = 500  # poor man's solution for bouncing
        
        self.is_mouse_button_down = False
        self.mouse_button_down_pos = 0, 0
        self.mouse_speed = 0, 0
        self.mouse_speed_deque = [deque(maxlen=20), deque(maxlen=20)]
        self.gravity = 0.05
        self.is_scrolling = [False, False]
        self.scroll_thres = 10, 10
        self.tick_speed = 60
        self.button_long_pressed = 800

        self.play = play.Play()
        self.song_select_scene = \
            song_select_scene.SongScene('myscene',
                                        self.play,
                                        width=screen_height,
                                        height=screen_width,
                                        orientation=self.orientation)
        self.main_scene = main_scene.MainScene(self.play,
                                               width=screen_height,
                                               height=screen_width,
                                               orientation=self.orientation)
        self.cur_scene = self.main_scene
        self.cur_scene.redraw()
        self.cur_scene.update(self.screen)

        self.button_down_time = 0  # time the button was pressed


    def init_touchscreen(self):
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'TSLIB')
        os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

    def display_on(self):
        pass
        
    def display_off(self):
        pass

    def GPIO_init(self):
        """
        Init for GPIO
        """
        GPIO.setmode(GPIO.BCM)

    def ext_button_init(self, GPIO_pin):
        """
        Init for GPIO button
        GPIO_pin in BCM
        Buttons are set to active low
        """
        GPIO.setup(GPIO_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    def ext_button_pressed(self, GPIO_pin):
        """
        Returns True if button at GPIO_pin is pressed
        """
        if self.ext_button_time > 400:
            if GPIO.input(GPIO_pin) == 0:  # active low
                self.ext_button_time = 0
                print "hey, I'm (im)pressed"
            
    def pressed(self, x, y, long_pressed=False):
        action = self.cur_scene.pressed(x, y, long_pressed)
        print 'action', action
        if action == "goto_main":
            self.cur_scene = self.main_scene
            self.main_scene.activated()
        elif action == "goto_main_lp":
            self.play.stop()
            self.cur_scene = self.main_scene
        elif action == "goto_song_select":
            self.cur_scene = self.song_select_scene
        self.cur_scene.redraw()

    def released(self, x, y):
        if not any(self.is_scrolling):
            self.pressed(x, y, long_pressed=False)

    def moved(self, m):
        y, x = m
        rx, ry = False, False
        if self.is_scrolling[0]:
            if self.orientation == 3:
                rx = self.cur_scene.scroll_vertical(-y)
            elif self.orientation == 1:
                rx = self.cur_scene.scroll_vertical(y)
        self.mouse_speed = self.mouse_speed[0] * rx, self.mouse_speed[1] * ry

    def while_mouse_button_down(self):
        x, y = pygame.mouse.get_pos()
        mouse_vec = x - self.mouse_button_down_pos[0], \
            y - self.mouse_button_down_pos[1]

        scroll_x = (np.fabs(mouse_vec[0]) > self.scroll_thres[0] or
                    self.is_scrolling[0]) \
            and not self.is_scrolling[1] \
            and self.cur_scene.scrolling_allowed
        scroll_y = (np.fabs(mouse_vec[1]) > self.scroll_thres[1] or
                    self.is_scrolling[1]) \
            and not self.is_scrolling[0]

        self.is_scrolling = [scroll_x, scroll_y]

        mouse_rel_vec = x - self.mouse_button_down_pos[0], \
            y - self.mouse_button_down_pos[1]
        self.mouse_speed_deque[0].append(mouse_rel_vec[0])
        self.mouse_speed_deque[1].append(mouse_rel_vec[1])

        self.button_down_time += self.fps_clock.get_time()

        if any(self.is_scrolling):
            self.mouse_speed = map(np.mean, self.mouse_speed_deque)
            self.mouse_speed = map(int, self.mouse_speed)
            self.mouse_speed_deque = [deque(maxlen=20), deque(maxlen=20)]
            self.moved(mouse_rel_vec)
        else:
            if self.button_down_time - self.fps_clock.get_time() > \
                    self.button_long_pressed:
                self.is_mouse_button_down = False
                print "long pressed", self.mouse_button_down_pos[0], \
                    self.mouse_button_down_pos[1]
                self.pressed(self.mouse_button_down_pos[0],
                             self.mouse_button_down_pos[1],
                             long_pressed=True)

    def scroll(self):
        ticks = self.fps_clock.get_time()

        def decelerate(x):
            if x < 0:
                return min(0, int(x + self.gravity * ticks))
            elif x > 0:
                return max(0, int(x - self.gravity * ticks))
            else:
                return 0
        self.mouse_speed = map(decelerate, self.mouse_speed)
        if self.mouse_speed[0] == 0:
            self.is_scrolling[0] = False
        if self.mouse_speed[1] == 0:
            self.is_scrolling[1] = False
        if np.fabs(self.mouse_speed[0]) > 30 \
            or np.fabs(self.mouse_speed[1]) > 30:
            n = int(self.mouse_speed[0] / 6.), int(self.mouse_speed[1] / 6.)
            self.moved(n)
            self.tick_speed = 60
        else:
            if self.tick_speed == 60:
                self.tick_speed = 30
                self.mouse_speed = int(self.mouse_speed[0] / 6.), \
                    int(self.mouse_speed[1] / 6.)
            self.moved(self.mouse_speed)

    def process_event(self, event):
        if event.type is MOUSEBUTTONDOWN:
            self.button_down_time = 0  # self.fps_clock.get_time()
            self.is_mouse_button_down = True
            self.mouse_speed = 0, 0
            self.mouse_button_down_pos = pygame.mouse.get_pos()
        if event.type is MOUSEBUTTONUP:
            x, y = map(lambda x: max(0, x), pygame.mouse.get_pos())
            if self.is_mouse_button_down:
                self.released(x, y)
            self.is_mouse_button_down = False
        if event.type is pygame.QUIT or event.type is KEYDOWN \
            and event.key is K_ESCAPE:
            self.done = False

    def run(self):
        while self.done:
            for event in pygame.event.get():
                self.process_event(event)
            if self.is_mouse_button_down:
                self.while_mouse_button_down()
            elif any(self.is_scrolling):
                self.scroll()
            self.fps_clock.tick(self.tick_speed)
            self.play.play()
            self.cur_scene.update(self.screen)
            fps_time = self.fps_clock.get_time()
            if self.cur_scene == self.main_scene:
                self.main_scene.party_region.add_time(fps_time)
            if not self.debug:
                self.ext_button_time += fps_time
                self.ext_button_pressed(23)
        # finish
        pygame.quit()


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(prog='pyfidelity.py')
    parser.add_argument("--debug", "-d", action='store_true',
                        help="debug, set if not running on raspberry pi")
    parser.add_argument(
        "--scan", "-s", action='store_true', help='scan music directory')
    args = parser.parse_args()

    if args.scan:
        import mp3database as db
        print 'Scan music directories:', music_directories
        music_db = db.MusicDB(music_db_file)
        try:
            music_db.scan_library(music_directories)
        except Exception, e:
            print e
            print 'bye bye'
            exit(1)

    pyfidelity = Pyfidelity(args.debug)
    pyfidelity.run()
