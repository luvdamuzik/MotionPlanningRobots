import json
import sys

from pygame.image import load
from pygame.math import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos
from pygame.mouse import get_pressed as mouse_buttons

from menu import Menu
from settings import *
from support import *
from timer import *

import tkinter as tk
from tkinter import messagebox

from pathlib import Path
import os, os.path


class Editor:
    def __init__(self, switch):
        # main setup
        self.display_surface = pygame.display.get_surface()
        self.canvas_data = {}
        self.imports()
        self.switch = switch

        # navigation
        self.origin = vector()
        self.pan_active = False
        self.pan_offset = vector()

        # support lines
        self.support_line_surf = pygame.Surface((WIDTH, HEIGHT))
        self.support_line_surf.set_colorkey("green")
        self.support_line_surf.set_alpha(30)

        # selection
        self.selection_index = 2
        self.previous_index = None

        # menu
        self.menu = Menu()

        # objects
        self.canvas_objects = pygame.sprite.Group()
        self.object_drag_active = False
        self.object_timer = Timer(400)

        # saves
        self.num_of_saves = len(os.listdir('saves'))

    # support functions
    def get_current_cell(self, obj=None):
        distance_to_origin = vector(mouse_pos()) - self.origin if not obj else vector(
            obj.distance_to_origin) - self.origin

        if distance_to_origin.x > 0:
            col = int(distance_to_origin.x / TILE_SIZE)
        else:
            col = int(distance_to_origin.x / TILE_SIZE) - 1

        if distance_to_origin.y > 0:
            row = int(distance_to_origin.y / TILE_SIZE)
        else:
            row = int(distance_to_origin.y / TILE_SIZE) - 1

        return col, row

    def imports(self):
        self.animations = {}
        for key, value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index': 0,
                    'frames': graphics,
                    'length': len(graphics)
                }
                # preview
        self.preview_surfs = {key: load(value['preview']) for key, value in EDITOR_DATA.items() if
                              value['preview']}

    def animation_update(self, dt):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * dt
            if value['frame index'] >= value['length']:
                value['frame index'] = 0

    def mouse_on_object(self):
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos()):
                return sprite

    def create_grid(self, save=False):
        try:
            # add objects to the tiles
            for tile in self.canvas_data.values():
                tile.objects = []

            for obj in self.canvas_objects:
                current_cell = self.get_current_cell(obj)
                offset = vector(obj.distance_to_origin) - (vector(current_cell) * TILE_SIZE)

                if current_cell in self.canvas_data:  # tile exists already
                    self.canvas_data[current_cell].add_id(obj.tile_id, offset)
                else:  # no tile exists yet
                    self.canvas_data[current_cell] = CanvasTile(obj.tile_id, offset)

            # create an empty grid
            layers = {
                'wall': {},
                'obstacle': {},
                'robot': {},
            }

            if self.canvas_data == {}:
                raise ValueError("Nothing found.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            return
        else:
            try:
                # grid offset
                left = sorted(self.canvas_data.keys(), key=lambda tile: tile[0])[0][0]
                right = sorted(self.canvas_data.keys(), key=lambda tile: tile[0], reverse=True)[0][0]
                top = sorted(self.canvas_data.keys(), key=lambda tile: tile[1])[0][1]
                bottom = sorted(self.canvas_data.keys(), key=lambda tile: tile[1], reverse=True)[0][1]

                grid = [[1 for _ in range(right - left + 1)] for _ in range(bottom - top + 1)]
                start_coords = []
                end_coords = []

                # fill the grid
                for tile_pos, tile in self.canvas_data.items():
                    row_adjusted = tile_pos[1] - top
                    col_adjusted = tile_pos[0] - left
                    x = col_adjusted * TILE_SIZE
                    y = row_adjusted * TILE_SIZE

                    if tile.has_wall:
                        layers['wall'][(x, y)] = tile.has_wall
                        grid[row_adjusted][col_adjusted] = 0

                    if tile.has_obstacle:
                        layers['obstacle'][(x, y)] = tile.has_obstacle
                        end_coords.append((row_adjusted, col_adjusted))
                        grid[row_adjusted][col_adjusted] = 0

                    if tile.objects:  # (obj, offset)
                        for obj, offset in tile.objects:
                            if obj in [key for key, value in EDITOR_DATA.items() if value['style'] == 'robot']:  # robot
                                layers['robot'][(int(x + offset.x), int(y + offset.y))] = obj
                                start_coords.append((int((x + offset.x) / TILE_SIZE), int((y + offset.y) / TILE_SIZE)))

                if not start_coords and not end_coords:
                    raise ValueError("No Robots or Tables found.")
                if not start_coords:
                    raise ValueError("No Robots Found.")
                if not end_coords:
                    raise ValueError("No Tables Found.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Error", str(e))
                return
            else:
                if save:
                    base = Path('saves')
                    jsonpath = base / ("save_file_" + str(self.num_of_saves) + ".txt")
                    base.mkdir(exist_ok=True)
                    data = {
                        "grid": grid,
                        "start": start_coords,
                        "end": end_coords
                    }
                    with open(jsonpath, "w") as outfile:
                        json.dump(data, outfile)
                else:
                    return layers, grid, start_coords, end_coords

    # input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch(self.create_grid())

            self.pan_input(event)
            self.selection_hotkey(event)
            self.menu_click(event)

            self.object_drag(event)
            self.canvas_add()
            self.canvas_remove()

    def pan_input(self, event):

        # middle mouse button pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1] and not self.menu.rect.collidepoint(mouse_pos()):
            self.pan_active = True
            self.pan_offset = vector(mouse_pos()) - self.origin

        if not mouse_buttons()[1]:
            self.pan_active = False

        # mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * TILE_SIZE
            else:
                self.origin.x -= event.y * TILE_SIZE
            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)

        # panning update
        if self.pan_active:
            self.origin = vector(mouse_pos()) - self.pan_offset

            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)

    def selection_hotkey(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
        self.selection_index = max(2, min(self.selection_index, 6))

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and \
                (self.menu.rect_bottom.collidepoint(mouse_pos()) or self.menu.rect_top.collidepoint(mouse_pos())):
            new_index = self.menu.click(mouse_pos(), mouse_buttons())
            # save
            if new_index == 5:
                self.previous_index = self.selection_index
                self.create_grid(True)
                self.selection_index = self.previous_index
                self.num_of_saves += 1
            elif new_index == 6:
                with open('saves/save_file_0.txt') as load_file:
                    data = json.load(load_file)
                self.load(data['grid'], data['start'], data['end'])
            else:
                self.selection_index = new_index if new_index else self.selection_index

    def load(self, grid, start_coords, end_coords):
        for robot in start_coords:
            CanvasObject(
                pos=((robot[0] * TILE_SIZE) + self.origin.x,
                     (robot[1] * TILE_SIZE) + self.origin.y),
                frames=self.animations[4]['frames'],
                tile_id=4,
                origin=self.origin,
                group=self.canvas_objects)

        for row, _ in enumerate(grid):
            for col, _ in enumerate(grid[row]):
                if grid[row][col] == 0 and [row, col] not in end_coords:  # wall
                    self.canvas_data[(col, row)] = CanvasTile(2)
                elif grid[row][col] == 0 and [row, col] in end_coords:  # table
                    self.canvas_data[(col, row)] = CanvasTile(3)

    def canvas_add(self):
        if mouse_buttons()[0] and not self.menu.rect_bottom.collidepoint(mouse_pos()) \
                and not self.menu.rect_top.collidepoint(mouse_pos()) and not self.object_drag_active:
            current_cell = self.get_current_cell()
            if EDITOR_DATA[self.selection_index]['type'] == 'tile':
                if current_cell not in self.canvas_data:
                    self.canvas_data[current_cell] = CanvasTile(self.selection_index)

            else:  # objects
                if not self.object_timer.active:
                    CanvasObject(
                        pos=((self.get_current_cell()[0] * TILE_SIZE) + self.origin.x,
                             (self.get_current_cell()[1] * TILE_SIZE) + self.origin.y),
                        frames=self.animations[self.selection_index]['frames'],
                        tile_id=self.selection_index,
                        origin=self.origin,
                        group=self.canvas_objects)
                    self.object_timer.activate()

    def canvas_remove(self):
        if mouse_buttons()[2] and not self.menu.rect_bottom.collidepoint(mouse_pos()) and \
                not self.menu.rect_top.collidepoint(mouse_pos()):
            # delete objects
            selected_object = self.mouse_on_object()
            if selected_object and not self.object_drag_active:
                selected_object.kill()

            # delete tiles
            if self.canvas_data:
                current_cell = self.get_current_cell()
                if current_cell in self.canvas_data:
                    self.canvas_data[current_cell].remove_id(self.selection_index)

                    if self.canvas_data[current_cell].is_empty:
                        del self.canvas_data[current_cell]

    def object_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(event.pos):
                    sprite.start_drag()
                    self.object_drag_active = True

        if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            for sprite in self.canvas_objects:
                if sprite.selected:
                    sprite.drag_end(self.origin)
                    self.object_drag_active = False

    # drawing
    def draw_tile_lines(self):
        cols = WIDTH // TILE_SIZE
        rows = HEIGHT // TILE_SIZE

        origin_offset = vector(x=self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
                               y=self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE)

        self.support_line_surf.fill("green")

        for col in range(cols + 1):
            x = origin_offset.x + col * TILE_SIZE
            pygame.draw.line(self.support_line_surf, "black", (x, 0), (x, HEIGHT))

        for row in range(rows + 1):
            y = origin_offset.y + row * TILE_SIZE
            pygame.draw.line(self.support_line_surf, "black", (0, y), (WIDTH, y))

        self.display_surface.blit(self.support_line_surf, (0, 0))

    def draw_level(self):
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * TILE_SIZE

            if tile.has_wall:
                image = pygame.image.load('graphics/wall.png').convert_alpha()
                self.display_surface.blit(image, pos)

            if tile.has_obstacle:
                image = pygame.image.load('graphics/table.png').convert_alpha()
                self.display_surface.blit(image, pos)

            if tile.robot:
                image = pygame.image.load('graphics/robot_player.png').convert_alpha()
                self.display_surface.blit(image, pos)
        self.canvas_objects.draw(self.display_surface)

    def preview(self):
        selected_object = self.mouse_on_object()
        if not self.menu.rect_bottom.collidepoint(mouse_pos()) and not self.menu.rect_top.collidepoint(mouse_pos()):
            if selected_object:
                rect = selected_object.rect.inflate(10, 10)
                color = "black"
                line_width = 3
                size = 15
                pygame.draw.lines(self.display_surface, color, False,
                                  ((rect.left, rect.top + size), rect.topleft, (rect.left + size, rect.top)),
                                  line_width)
                pygame.draw.lines(self.display_surface, color, False,
                                  ((rect.right - size, rect.top), rect.topright, (rect.right, rect.top + size)),
                                  line_width)
                pygame.draw.lines(self.display_surface, color, False,
                                  (
                                      (rect.right - size, rect.bottom), rect.bottomright,
                                      (rect.right, rect.bottom - size)),
                                  line_width)
                pygame.draw.lines(self.display_surface, color, False,
                                  ((rect.left, rect.bottom - size), rect.bottomleft, (rect.left + size, rect.bottom)),
                                  line_width)

            else:
                type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
                if self.selection_index not in (5, 6):
                    surf = self.preview_surfs[self.selection_index].copy()
                    surf.set_alpha(200)

                    # tile
                    if type_dict[self.selection_index] == 'tile':
                        current_cell = self.get_current_cell()
                        rect = surf.get_rect(topleft=self.origin + vector(current_cell) * TILE_SIZE)
                    # object
                    else:
                        current_cell = self.get_current_cell()
                        rect = surf.get_rect(topleft=self.origin + vector(current_cell) * TILE_SIZE)
                    self.display_surface.blit(surf, rect)
                else:
                    pass

    # update
    def run(self, dt):
        self.event_loop()
        # updating
        self.canvas_objects.update(dt)
        self.object_timer.update()

        # drawing
        self.display_surface.fill("grey")
        self.draw_level()
        self.draw_tile_lines()
        pygame.draw.circle(self.display_surface, "red", self.origin, 10)
        self.preview()
        self.menu.display(self.selection_index)


class CanvasTile:
    def __init__(self, tile_id, offset=vector()):

        # terrain

        self.is_empty = False
        self.has_wall = False
        self.wall_neighbors = []

        # obstacle
        self.has_obstacle = False

        # robots
        self.robot = None

        # objects
        self.objects = []

        self.add_id(tile_id, offset)

    def add_id(self, tile_id, offset=vector()):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        if options[tile_id] == 'terrain':
            self.has_wall = True
        elif options[tile_id] == 'obstacle':
            self.has_obstacle = True
        # elif options[tile_id] == 'robot':
        #     self.robot = tile_id
        else:
            if (tile_id, offset) not in self.objects:
                self.objects.append((tile_id, offset))

    def remove_id(self, tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        if options[tile_id] == 'terrain':
            self.has_wall = False
        elif options[tile_id] == 'obstacle':
            self.has_obstacle = False
        elif options[tile_id] == 'robot':
            self.robot = None

        self.check_content()

    def check_content(self):
        if not self.has_wall and not self.has_obstacle and not self.robot:
            self.is_empty = True


class CanvasObject(pygame.sprite.Sprite):
    def __init__(self, pos, frames, tile_id, origin, group):
        super().__init__(group)
        self.tile_id = tile_id

        # animation
        self.frames = frames
        self.frame_index = 0

        self.image = pygame.image.load('graphics/robot_player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        # movement
        self.distance_to_origin = vector(self.rect.topleft) - origin
        self.selected = False

    def start_drag(self):
        self.selected = True

    def drag(self):
        if self.selected:
            x = int(mouse_pos()[0] / TILE_SIZE) * TILE_SIZE
            y = int(mouse_pos()[1] / TILE_SIZE) * TILE_SIZE

            fixed = vector((x, y))
            self.rect.topleft = fixed

    def drag_end(self, origin):
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
        self.image = pygame.image.load('graphics/robot_player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def pan_pos(self, origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self, dt):
        self.animate(dt)
        self.drag()
