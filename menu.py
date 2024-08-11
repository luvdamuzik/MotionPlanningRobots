import pygame
from settings import *
from pygame.image import load


class Menu:
    def __init__(self):
        self.buttons = pygame.sprite.Group()
        self.top_buttons = pygame.sprite.Group()
        self.bottom_buttons = pygame.sprite.Group()
        self.menu_button = pygame.sprite.Group()
        self.temp_top_menu = pygame.sprite.Group()
        self.menu_surfs = None
        self.display_surface = pygame.display.get_surface()
        self.create_data()
        self.create_buttons()
        self.collapse_top_menu = True

    def collapse_top_menu_toggle(self):
        self.collapse_top_menu = not self.collapse_top_menu

    def create_data(self):
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']:
                if not value['menu'] in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key, load(value['menu_surf']))]
                else:
                    self.menu_surfs[value['menu']].append((key, load(value['menu_surf'])))

    def create_buttons(self):
        # menu area general
        size = 200
        margin = 6
        self.rect_bottom = pygame.Rect(WIDTH - size - margin, HEIGHT - size - margin, size, size)
        # save and load
        self.rect_top = pygame.Rect(WIDTH - size - margin, 0 + margin, size, size)

        # button areas
        generic_button_rect = pygame.Rect(self.rect_bottom.topleft,
                                          (self.rect_bottom.width / 2, self.rect_bottom.height / 2))
        generic_button_rect_1 = pygame.Rect(self.rect_bottom.topleft,
                                            (self.rect_bottom.width, self.rect_bottom.height / 2))
        button_margin = 5
        self.wall_button_rect = generic_button_rect.copy().inflate(-button_margin, -button_margin)
        self.table_button_rect = generic_button_rect.move(self.rect_bottom.width / 2, 0).inflate(
            -button_margin,
            -button_margin)
        self.robot_button_rect = generic_button_rect_1.move(0, self.rect_bottom.height / 2).inflate(-button_margin,
                                                                                                    -button_margin)
        # save and load buttons
        generic_button_rect_save_load = pygame.Rect(self.rect_top.topleft,
                                                    (self.rect_top.width, self.rect_top.height / 4))
        generic_button_top_small = pygame.Rect(self.rect_top.topleft,
                                               (self.rect_top.width / 4, self.rect_top.height / 4))

        self.menu_button_rect = generic_button_top_small.copy().move(self.rect_top.width - self.rect_top.width / 4, 0). \
            inflate(-button_margin, -button_margin)

        # self.menu_button_rect = generic_button_rect_save_load.copy().inflate(-button_margin, -button_margin)

        self.save_button_rect = generic_button_rect_save_load.copy().inflate(-button_margin, -button_margin)
        self.load_button_rect = generic_button_rect_save_load.move(0, self.rect_top.height / 4).inflate(-button_margin,
                                                                                                        -button_margin)
        self.clear_button_rect = generic_button_rect_save_load.move(0, self.rect_top.height / 2).inflate(-button_margin,
                                                                                                         -button_margin)
        self.collapse_button_rect = generic_button_top_small. \
            move(0, self.rect_top.height).move(self.rect_top.width - self.rect_top.width / 4,
                                               -self.rect_top.height / 4).inflate(-button_margin, -button_margin)

        # create the buttons
        Button(self.wall_button_rect, [self.buttons, self.bottom_buttons], self.menu_surfs['wall'])
        Button(self.table_button_rect, [self.buttons, self.bottom_buttons], self.menu_surfs['obstacle'])
        Button(self.robot_button_rect, [self.buttons, self.bottom_buttons], self.menu_surfs['robot'])
        Button(self.save_button_rect, [self.buttons, self.top_buttons], self.menu_surfs['save'])
        Button(self.load_button_rect, [self.buttons, self.top_buttons], self.menu_surfs['load'])
        Button(self.clear_button_rect, [self.buttons, self.top_buttons], self.menu_surfs['clear'])
        Button(self.collapse_button_rect, [self.buttons, self.top_buttons], self.menu_surfs['X'])
        Button(self.menu_button_rect, [self.buttons, self.menu_button], self.menu_surfs['menu'])

    def click(self, mouse_pos, mouse_button):
        for sprite in self.buttons:
            if not self.collapse_top_menu:
                if sprite.rect.collidepoint(mouse_pos):
                    if mouse_button[2]:  # right click
                        sprite.switch()
                    return sprite.get_id()
            else:
                if (sprite in self.menu_button or sprite in self.bottom_buttons) and sprite.rect.collidepoint(mouse_pos):
                    return sprite.get_id()

    def highlight_indicator(self, index):
        if EDITOR_DATA[index]['menu'] == 'wall':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.wall_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'obstacle':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.table_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'robot':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.robot_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'save':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.save_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'load':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.load_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'clear':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.clear_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'X':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.collapse_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'menu':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.menu_button_rect.inflate(4, 4), 5, 4)

    def display(self, index):
        self.buttons.update()
        self.top_buttons.update()
        self.bottom_buttons.update()
        self.menu_button.update()

        if self.collapse_top_menu:
            self.temp_top_menu = self.menu_button.copy()
            self.temp_top_menu.draw(self.display_surface)
        else:
            self.temp_top_menu = self.top_buttons.copy()
            self.temp_top_menu.draw(self.display_surface)
        self.bottom_buttons.draw(self.display_surface)
        self.highlight_indicator(index)


class Button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_alt=None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        # items
        self.items = {'main': items, 'alt': items_alt}
        self.index = 0
        self.main_active = True

    def get_id(self):
        return self.items['main'][self.index][0]

    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items['main']) else self.index

    def update(self):
        self.image.fill(BUTTON_BG_COLOR)
        surf = self.items['main'][self.index][1]

        rect = surf.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(surf, rect)
