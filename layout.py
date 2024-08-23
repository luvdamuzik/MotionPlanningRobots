import sys
from itertools import permutations, product

import pygame

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from pathfinding.finder.breadth_first import BreadthFirstFinder

from PSO import find_path_pso
from menu import MenuLayout
from robot import Robot
from node import Node
from settings import *
import tkinter as tk
from tkinter import messagebox
from pygame.mouse import get_pos as mouse_pos


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"


def convert_to_points(tuple_list):
    return [Point(x, y) for x, y in tuple_list]


class Layout:
    def __init__(self, layers, grid, start_coords, end_coords, switch, asset_dict):
        # robots
        self.dt = None
        self.robots = pygame.sprite.Group()
        self.follow_player = False
        self.following_robot_index = None
        # get display surface
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        # sprite setup
        self.all_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

        # Create map
        self.build_level(layers, asset_dict)
        self.menu = MenuLayout()
        self.selected_option = None

        # Coords
        self.grid = grid
        self.start_coords = start_coords
        self.end_coords = end_coords

    def build_level(self, layers, asset_dict):
        for layer_name, layer in layers.items():
            for pos, data in layer.items():
                if layer_name == 'wall':
                    Node(pos, asset_dict['wall'], (self.all_sprites, self.obstacle_sprites))
                if layer_name == 'obstacle':
                    Node(pos, asset_dict['table'], (self.all_sprites, self.obstacle_sprites))
                if layer_name == 'robot':
                    Robot(pos, [self.all_sprites, self.robots], self.obstacle_sprites)

    def draw_path(self):
        for robot in self.robots:
            if robot.path:
                points = []
                for point in robot.path:
                    # Calculate the position of each point on the internal surface
                    x = (
                                point.x * TILE_SIZE) - self.all_sprites.offset.x + self.all_sprites.internal_offset.x + TILE_SIZE / 2
                    y = (
                                point.y * TILE_SIZE) - self.all_sprites.offset.y + self.all_sprites.internal_offset.y + TILE_SIZE / 2

                    # Scale the points according to the zoom level
                    x = x * self.all_sprites.zoom_scale + self.half_width - self.all_sprites.internal_surf_size[
                        0] * self.all_sprites.zoom_scale / 2
                    y = y * self.all_sprites.zoom_scale + self.half_height - self.all_sprites.internal_surf_size[
                        1] * self.all_sprites.zoom_scale / 2

                    points.append((x, y))
                    pygame.draw.circle(self.display_surface, robot.color, (x, y), 2)

                # Draw the path as a series of connected lines on the main display surface
                pygame.draw.lines(self.display_surface, robot.color, False, points, 5)

    def BFS_one_to_one(self, grid, start_coords, end_coords):
        try:
            helpers = []
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                if grid[end_coords[0][0] - direction[0]][end_coords[0][1] - direction[1]] != 0:
                    helpers.append((end_coords[0][0] - direction[0], end_coords[0][1] - direction[1]))

            if not helpers:
                raise ValueError("Unable to find a valid coordinate to go to.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            paths = []
            grid = Grid(matrix=grid)
            start_point = grid.node(start_coords[0][0], start_coords[0][1])
            for helper in helpers:
                end_point = grid.node(helper[1], helper[0])
                finder = BreadthFirstFinder()
                path, _ = finder.find_path(start_point, end_point, grid)
                paths.append(path)
                grid.cleanup()

            for robot in self.robots:
                robot.set_path(min(paths, key=len))

    def Dijkstra_one_to_one(self, grid, start_coords, end_coords):
        try:
            helpers = []
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                if grid[end_coords[0][0] - direction[0]][end_coords[0][1] - direction[1]] != 0:
                    helpers.append((end_coords[0][0] - direction[0], end_coords[0][1] - direction[1]))

            if not helpers:
                raise ValueError("Unable to find a valid coordinate to go to.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            paths = []
            grid = Grid(matrix=grid)
            start_point = grid.node(start_coords[0][0], start_coords[0][1])
            for helper in helpers:
                end_point = grid.node(helper[1], helper[0])
                finder = DijkstraFinder()
                path, _ = finder.find_path(start_point, end_point, grid)
                paths.append(path)
                grid.cleanup()

            for robot in self.robots:
                robot.set_path(min(paths, key=len))

    def Astar_one_to_one(self, grid, start_coords, end_coords):
        try:
            helpers = []
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                if grid[end_coords[0][0] - direction[0]][end_coords[0][1] - direction[1]] != 0:
                    helpers.append((end_coords[0][0] - direction[0], end_coords[0][1] - direction[1]))

            if not helpers:
                raise ValueError("Unable to find a valid coordinate to go to.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            paths = []
            grid = Grid(matrix=self.grid)
            start_point = grid.node(start_coords[0][0], start_coords[0][1])
            for helper in helpers:
                end_point = grid.node(helper[1], helper[0])
                finder = AStarFinder()
                path, _ = finder.find_path(start_point, end_point, grid)
                paths.append(path)
                grid.cleanup()

            for robot in self.robots:
                robot.set_path(min(paths, key=len))

    def Dijkstra_one_to_many(self, grid, start_coords, end_coords_list):
        def get_helpers(target, grid):
            helpers = []
            for direction in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                helper = (target[0] + direction[0], target[1] + direction[1])
                if 0 <= helper[0] < len(grid) and 0 <= helper[1] < len(grid[0]):
                    if grid[helper[0]][helper[1]] != 0:
                        helpers.append(helper)
            return helpers

        try:
            shortest_path = None
            min_path_length = float('inf')

            all_helpers_combinations = [get_helpers(target, grid) for target in end_coords_list]

            for helper_combination in product(*all_helpers_combinations):
                if len(set(helper_combination)) < len(helper_combination):
                    continue

                for perm in permutations(helper_combination):
                    current_point = (start_coords[0][1], start_coords[0][0])
                    total_path = []
                    path_length = 0

                    for helper in perm:
                        grid = Grid(matrix=self.grid)
                        start_node = grid.node(current_point[1], current_point[0])
                        end_node = grid.node(helper[1], helper[0])
                        finder = DijkstraFinder()
                        path, _ = finder.find_path(start_node, end_node, grid)
                        if not path:
                            raise ValueError(f"Unable to find a path to helper coordinate {helper}.")
                        total_path.extend(path)
                        path_length += len(path) - 1
                        current_point = helper

                    if path_length < min_path_length:
                        min_path_length = path_length
                        shortest_path = total_path

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            for robot in self.robots:
                robot.set_path(shortest_path)

    def Astar_one_to_many(self, grid, start_coords, end_coords_list):
        def get_helpers(target, grid):
            helpers = []
            for direction in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                helper = (target[0] + direction[0], target[1] + direction[1])
                if 0 <= helper[0] < len(grid) and 0 <= helper[1] < len(grid[0]):
                    if grid[helper[0]][helper[1]] != 0:
                        helpers.append(helper)
            return helpers

        try:
            shortest_path = None
            min_path_length = float('inf')

            all_helpers_combinations = [get_helpers(target, grid) for target in end_coords_list]

            for helper_combination in product(*all_helpers_combinations):
                if len(set(helper_combination)) < len(helper_combination):
                    continue

                for perm in permutations(helper_combination):
                    current_point = (start_coords[0][1], start_coords[0][0])
                    total_path = []
                    path_length = 0

                    for helper in perm:
                        grid = Grid(matrix=self.grid)
                        start_node = grid.node(current_point[1], current_point[0])
                        end_node = grid.node(helper[1], helper[0])
                        finder = AStarFinder()
                        path, _ = finder.find_path(start_node, end_node, grid)
                        if not path:
                            raise ValueError(f"Unable to find a path to helper coordinate {helper}.")
                        total_path.extend(path)
                        path_length += len(path) - 1
                        current_point = helper

                    if path_length < min_path_length:
                        min_path_length = path_length
                        shortest_path = total_path

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            for robot in self.robots:
                robot.set_path(shortest_path)

    def choose_algorithm_popup(self):
        input_active = True
        selected_option = None
        selected_option_text = None

        font = pygame.font.Font(None, 32)
        option_height = 50
        menu_width = 400

        if len(self.start_coords) == 1 and len(self.end_coords) == 1:
            options = [['BFS', 'BFS 1to1'], ['Dijkstra', 'Dijkstra 1to1'], ['A*', 'A* 1to1'], ['PSO', 'PSO']]
        elif len(self.start_coords) == 1 and len(self.end_coords) > 1:
            options = [['Dijkstra', 'Dijkstra 1toMany'], ['A*', 'A* 1toMany'], ['PSO', 'PSO']]
        else:
            options = [['A* with pause', 'A* ManytoManyP'], ['A* with block', 'A* ManytoManyB'],
                       ['A* with pause+block', 'A* ManytoManyPB'], ['PSO', 'PSO ManytoMany']]

        menu_height = option_height * len(options) + 40

        color_active = pygame.Color('lightskyblue3')
        color_passive = pygame.Color('dodgerblue2')
        bg_color = pygame.Color('white')
        text_color = pygame.Color('black')

        button_font = pygame.font.Font(None, 28)
        button_color = pygame.Color('lightgray')
        button_hover_color = pygame.Color('gray')
        button_text_color = pygame.Color('black')

        popup_rect = pygame.Rect(0, 0, menu_width, menu_height)
        popup_rect.center = self.display_surface.get_rect().center
        x_button_rect = pygame.Rect(popup_rect.right - 40, popup_rect.top + 5, 30, 30)

        option_rects = []
        for i in range(len(options)):
            option_bg_rect = pygame.Rect(popup_rect.left + 20, popup_rect.top + 40 + i * option_height, menu_width - 40,
                                         option_height - 10)
            option_rects.append(option_bg_rect)

        while input_active:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if x_button_rect.collidepoint(mouse_pos):
                        return None, None
                    for i, option_rect in enumerate(option_rects):
                        if option_rect.collidepoint(mouse_pos):
                            selected_option = options[i][1]
                            selected_option_text = options[i][0]
                            input_active = False
                            break

            self.display_surface.fill("grey")
            pygame.draw.rect(self.display_surface, bg_color, popup_rect)
            pygame.draw.rect(self.display_surface, text_color, popup_rect, 2)

            x_button_color = button_hover_color if x_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.display_surface, x_button_color, x_button_rect)
            x_text_surface = button_font.render("X", True, button_text_color)
            self.display_surface.blit(x_text_surface, (x_button_rect.x + 7, x_button_rect.y + 3))

            for i, option_rect in enumerate(option_rects):
                option_color = color_active if option_rect.collidepoint(mouse_pos) else color_passive
                pygame.draw.rect(self.display_surface, option_color, option_rect, border_radius=10)

                option_text = font.render(options[i][0], True, text_color)
                text_rect = option_text.get_rect(center=option_rect.center)
                self.display_surface.blit(option_text, text_rect)

            pygame.display.flip()

        return selected_option, selected_option_text

    def reset_robots(self):
        for robot in self.robots:
            robot.update_position()

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect_top.collidepoint(mouse_pos()):
            selected_algorithm, self.selected_option = self.choose_algorithm_popup()
            if selected_algorithm:
                self.reset_robots()
            if selected_algorithm == 'BFS 1to1':
                self.BFS_one_to_one(self.grid, self.start_coords, self.end_coords)
            if selected_algorithm == 'Dijkstra 1to1':
                self.Dijkstra_one_to_one(self.grid, self.start_coords, self.end_coords)
            if selected_algorithm == 'A* 1to1':
                self.Astar_one_to_one(self.grid, self.start_coords, self.end_coords)
            if selected_algorithm == 'Dijkstra 1toMany':
                self.Dijkstra_one_to_many(self.grid, self.start_coords, self.end_coords)
            if selected_algorithm == 'A* 1toMany':
                self.Astar_one_to_many(self.grid, self.start_coords, self.end_coords)
            if selected_algorithm == 'PSO':
                best_path = find_path_pso(self.grid, self.start_coords, self.end_coords, 2, 100, 100, 200)
                best_path = convert_to_points(best_path)
                for robot in self.robots:
                    robot.set_path(best_path)
            if selected_algorithm == 'A* ManytoManyP':
                clusters = None # then assign clusters to robots then run after that check for collisons then fix them using pause

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch(layout=True)
            if event.type == pygame.MOUSEWHEEL and 0.2 <= self.all_sprites.zoom_scale <= 1:
                self.all_sprites.zoom_scale += event.y * 0.03
            if event.type == pygame.MOUSEWHEEL and (
                    self.all_sprites.zoom_scale < 0.2 or self.all_sprites.zoom_scale > 1):
                if self.all_sprites.zoom_scale < 0.2:
                    self.all_sprites.zoom_scale = 0.2
                if self.all_sprites.zoom_scale > 1:
                    self.all_sprites.zoom_scale = 1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self.all_sprites.start_panning()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                self.all_sprites.stop_panning()

            self.menu_click(event)

    def run(self, dt):
        self.dt = dt
        mouse_pos = pygame.mouse.get_pos()

        adjusted_mouse_pos = (
            (mouse_pos[
                 0] - self.half_width) / self.all_sprites.zoom_scale + self.all_sprites.offset.x + self.all_sprites.internal_offset.x,
            (mouse_pos[
                 1] - self.half_height) / self.all_sprites.zoom_scale + self.all_sprites.offset.y + self.all_sprites.internal_offset.y
        )

        if pygame.mouse.get_pressed()[0]:
            clicked_robot = None

            for i, robot in enumerate(self.robots):
                # print(robot.rect.x, robot.rect.y)
                # print(mouse_pos)
                # print(adjusted_mouse_pos)
                if robot.rect.collidepoint(mouse_pos):
                    clicked_robot = robot
                    self.follow_player = True
                    self.following_robot_index = i
                    break

            if not clicked_robot:
                self.follow_player = False

        if pygame.mouse.get_pressed()[2]:
            self.follow_player = False

        if self.follow_player:
            self.all_sprites.custom_draw(self.robots.sprites()[self.following_robot_index])
        else:
            self.all_sprites.custom_draw()

        self.draw_path()
        self.event_loop()
        self.all_sprites.update(dt, self.grid, self.start_coords, self.end_coords)
        self.menu.display()
        if self.selected_option:
            font = pygame.font.Font(None, 32)
            text_surf = font.render(f"Selected: {self.selected_option}", True, pygame.Color('white'))

            text_rect = text_surf.get_rect(topleft=(10, 10))
            bg_rect = text_rect.inflate(10, 10)

            pygame.draw.rect(self.display_surface, pygame.Color('grey'), bg_rect)

            self.display_surface.blit(text_surf, text_rect)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # offset
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # zoom
        self.zoom_scale = 0.4
        self.internal_surf_size = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_height, self.half_width))
        self.internal_surf_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_width
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_height

        # Panning variables
        self.is_panning = False
        self.pan_start_pos = pygame.math.Vector2()

    def start_panning(self):
        self.is_panning = True
        self.pan_start_pos = pygame.math.Vector2(pygame.mouse.get_pos())

    def stop_panning(self):
        self.is_panning = False

    def update_pan(self):
        if self.is_panning:
            current_mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
            pan_movement = self.pan_start_pos - current_mouse_pos
            self.pan_start_pos = current_mouse_pos
            self.internal_offset += pan_movement / self.zoom_scale

    def center_target_camera(self, target):
        self.offset.x = target.rect.x - self.half_width
        self.offset.y = target.rect.y - self.half_height

    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] and self.zoom_scale < 1:
            self.zoom_scale += 0.01
        if keys[pygame.K_e] and self.zoom_scale > 0.4:
            self.zoom_scale -= 0.01

    def draw_corner_lines(self, rect, line_length=10, offset=2, color=(255, 0, 0), thickness=5):
        # Top-left corner
        pygame.draw.line(
            self.internal_surf, color,
            (rect.left + offset, rect.top + offset),
            (rect.left + line_length + offset, rect.top + offset), thickness)
        pygame.draw.line(
            self.internal_surf, color,
            (rect.left + offset, rect.top + offset),
            (rect.left + offset, rect.top + line_length + offset), thickness)

        # Top-right corner
        pygame.draw.line(
            self.internal_surf, color,
            (rect.right - offset, rect.top + offset),
            (rect.right - line_length - offset, rect.top + offset), thickness)
        pygame.draw.line(
            self.internal_surf, color,
            (rect.right - offset, rect.top + offset),
            (rect.right - offset, rect.top + line_length + offset), thickness)

        # Bottom-left corner
        pygame.draw.line(
            self.internal_surf, color,
            (rect.left + offset, rect.bottom - offset),
            (rect.left + line_length + offset, rect.bottom - offset), thickness)
        pygame.draw.line(
            self.internal_surf, color,
            (rect.left + offset, rect.bottom - offset),
            (rect.left + offset, rect.bottom - line_length - offset), thickness)

        # Bottom-right corner
        pygame.draw.line(
            self.internal_surf, color,
            (rect.right - offset, rect.bottom - offset),
            (rect.right - line_length - offset, rect.bottom - offset), thickness)
        pygame.draw.line(
            self.internal_surf, color,
            (rect.right - offset, rect.bottom - offset),
            (rect.right - offset, rect.bottom - line_length - offset), thickness)

    def custom_draw(self, player=None):
        # getting offset
        if player:
            self.center_target_camera(player)
            self.zoom_scale = 1
        else:
            self.zoom_keyboard_control()
            # self.offset.x = 0
            # self.offset.y = 0
            self.update_pan()

        # zoom
        self.internal_surf.fill('#FFFFFF')

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset + self.internal_offset
            scaled_offset_rect = pygame.Rect(
                offset_rect[0],
                offset_rect[1],
                sprite.rect.width,
                sprite.rect.height
            )
            self.internal_surf.blit(sprite.image, offset_rect)
            if isinstance(sprite, Robot):
                self.draw_corner_lines(scaled_offset_rect, color=sprite.color)

        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_width, self.half_height))

        self.display_surface.blit(scaled_surf, scaled_rect)
