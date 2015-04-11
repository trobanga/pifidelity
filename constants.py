import pygame

screen_x_max = 240
screen_y_max = 320

# colors
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(39, 37, 37)
LIGHT_GRAY = pygame.Color(130, 100, 100)

# path to pifidelity- it is easier to deal with absolute paths
pifi_dir = '/home/pi/pifidelity/'


# path to music
music_directories = ["/mnt/Banca/Music"]
music_db_file = pifi_dir + 'music.db'


# paths to bmls
bml_directories = [pifi_dir + 'bmls']

# paths to icons
icons_dir = pifi_dir + 'icons/'
vol_up_icon = icons_dir + 'isometric_vol_up.png'
vol_dn_icon = icons_dir + 'isometric_vol_dn.png'
mute_icon = icons_dir + 'isometric_mute.png'
next_icon = icons_dir + 'isometric_skip.png'
prev_icon = icons_dir + 'isometric_rewind.png'
select_icon = icons_dir + 'isometric_play.png'
