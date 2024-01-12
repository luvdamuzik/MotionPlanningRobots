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

}
