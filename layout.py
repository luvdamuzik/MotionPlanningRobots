import sys

import pygame

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from robot import Robot
from node import Node
from settings import *
import tkinter as tk
from tkinter import messagebox


class Layout:
    def __init__(self, layers, grid, start_coords, end_coords, switch, asset_dict):
        # robots
        self.robots = None
        self.follow_player = False
        # get display surface
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        # sprite setup
        self.all_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Create map
        self.build_level(layers, asset_dict)

        # Coords
        self.grid = grid
        self.start_coords = start_coords
        self.end_coords = end_coords

        self.calc_path_simple_one_to_one(layers, grid, start_coords, end_coords)

    def build_level(self, layers, asset_dict):
        for layer_name, layer in layers.items():
            for pos, data in layer.items():
                if layer_name == 'wall':
                    Node(pos, asset_dict['wall'], (self.all_sprites, self.obstacle_sprites))
                if layer_name == 'obstacle':
                    Node(pos, asset_dict['table'], (self.all_sprites, self.obstacle_sprites))
                if layer_name == 'robot':
                    self.robots = Robot(pos, self.all_sprites, self.obstacle_sprites)

    def calc_path_simple_one_to_one(self, layers, grid, start_coords, end_coords):
        try:
            # find valid coord to go to
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                if grid[end_coords[0][0] - direction[0]][end_coords[0][1] - direction[1]] != 0:
                    helper = (end_coords[0][0] - direction[0], end_coords[0][1] - direction[1])
                    break
                else:
                    helper = None

            if helper is None:
                raise ValueError("Unable to find a valid coordinate to go to.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))
            self.switch()
        else:
            grid = Grid(matrix=grid)
            print(grid)
            print(start_coords)
            print(end_coords)
            start_point = grid.node(start_coords[0][0], start_coords[0][1])
            end_point = grid.node(helper[1], helper[0])
            finder = AStarFinder()
            path, _ = finder.find_path(start_point, end_point, grid)

            self.robots.set_path(path)

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
            if event.type == pygame.MOUSEWHEEL and 0.4 <= self.all_sprites.zoom_scale <= 1:
                self.all_sprites.zoom_scale += event.y * 0.03

    def run(self, dt):
        # update and draw the game
        if pygame.mouse.get_pressed()[0]:
            self.follow_player = True
        elif pygame.mouse.get_pressed()[2]:
            self.follow_player = False

        if self.follow_player:
            self.all_sprites.custom_draw(self.robots)
        else:
            self.all_sprites.custom_draw()

        self.event_loop()
        self.all_sprites.update(dt, self.grid, self.start_coords, self.end_coords)


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

    def center_target_camera(self, target):
        self.offset.x = target.rect.x - self.half_width
        self.offset.y = target.rect.y - self.half_height

    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] and self.zoom_scale < 1:
            self.zoom_scale += 0.01
        if keys[pygame.K_e] and self.zoom_scale > 0.4:
            self.zoom_scale -= 0.01

    def custom_draw(self, player=0):
        # getting offset
        if player:
            self.center_target_camera(player)
            self.zoom_scale = 1
        else:
            self.zoom_keyboard_control()
            self.offset.x = 0
            self.offset.y = 0

        # zoom
        self.internal_surf.fill('#FFFFFF')

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image, offset_rect)

        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_width, self.half_height))

        self.display_surface.blit(scaled_surf, scaled_rect)
