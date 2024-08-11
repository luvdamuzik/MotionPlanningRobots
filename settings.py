WIDTH, HEIGHT = 1280, 720
FPS = 60
TILE_SIZE = 64
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
ROBOT_COLOR = (0, 0, 255)  # Blue color for the robot
TILE_COLOR = (160, 160, 160)  # Tile floor color
BUTTON_BG_COLOR = '#33323d'
BUTTON_LINE_COLOR = '#f5f1de'
ANIMATION_SPEED = 8

EDITOR_DATA = {
    2: {'style': 'terrain', 'type': 'tile', 'menu': 'wall', 'menu_surf': 'graphics/wall.png',
        'preview': 'graphics/wall.png', 'graphics': None},
    3: {'style': 'obstacle', 'type': 'tile', 'menu': 'obstacle', 'menu_surf': 'graphics/table.png',
        'preview': 'graphics/table.png', 'graphics': None},
    4: {'style': 'robot', 'type': 'object', 'menu': 'robot', 'menu_surf': 'graphics/robot_player.png',
        'preview': 'graphics/robot_player.png', 'graphics': 'graphics/robot_player.png'},
    5: {'style': 'save', 'type': 'text', 'menu': 'save', 'menu_surf': 'graphics/save.png',
        'preview': None, 'graphics': None},
    6: {'style': 'load', 'type': 'text', 'menu': 'load', 'menu_surf': 'graphics/load.png',
        'preview': None, 'graphics': None},
    7: {'style': 'clear', 'type': 'text', 'menu': 'clear', 'menu_surf': 'graphics/clear.png',
        'preview': None, 'graphics': None},
    8: {'style': 'X', 'type': 'text', 'menu': 'X', 'menu_surf': 'graphics/X.png',
        'preview': None, 'graphics': None},
    9: {'style': 'menu', 'type': 'text', 'menu': 'menu', 'menu_surf': 'graphics/menu.png',
        'preview': None, 'graphics': None},
}
