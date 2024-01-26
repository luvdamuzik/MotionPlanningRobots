import pygame
from pygame.image import load
from pygame.math import Vector2 as vector

from editor import Editor
from layout import Layout
from settings import *

import tkinter as tk
from tkinter import messagebox

# Initialize pygame
pygame.init()

# Create a Pygame window
screen = pygame.display.set_mode((800, 600))


class Game:
    def __init__(self):

        pygame.init()
        # Screen
        # self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # Title and icon
        pygame.display.set_caption("Motion Planning simulator")
        icon = load("graphics/robot.png")
        pygame.display.set_icon(icon)
        # Clock
        self.clock = pygame.time.Clock()

        self.wall_image = load('graphics/wall.png').convert_alpha()
        self.table_image = load('graphics/table.png').convert_alpha()

        self.layout = None
        self.editor_active = True
        self.transition = Transition(self.toggle)
        self.editor = Editor(self.switch)

        # cursor
        surf = load("graphics/mouse.png").convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), surf)
        pygame.mouse.set_cursor(cursor)

    def toggle(self):
        self.editor_active = not self.editor_active

    def switch(self, layers=None, layout=False):
        if layers:
            if layers[1]:
                grid = layers[1]
            else:
                grid = None

            if layers[2]:
                start_coords = layers[2]
            else:
                start_coords = None

            if layers[3]:
                end_coords = layers[3]
            else:
                end_coords = None

            layers = layers[0]

            if grid and start_coords and end_coords:
                self.transition.active = True
                self.layout = Layout(layers, grid, start_coords, end_coords, self.switch, {
                    'wall': self.wall_image,
                    'table': self.table_image
                })
        else:
            if layout:
                self.transition.active = True
            else:
                self.transition.active = False


    def run(self):
        while True:
            self.screen.fill('black')
            dt = self.clock.tick(FPS) / 1000
            if self.editor_active:
                self.editor.run(dt)
            else:
                self.layout.run(dt)

            self.transition.display(dt)
            pygame.display.update()


class Transition:
    def __init__(self, toggle):
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False

        self.border_width = 0
        self.direction = 1
        self.center = (WIDTH / 2, HEIGHT / 2)
        self.radius = vector(self.center).magnitude()
        self.threshold = self.radius + 100

    def display(self, dt):
        if self.active:
            self.border_width += 1000 * dt * self.direction
            if self.border_width >= self.threshold:
                self.direction = -1
                self.toggle()
            if self.border_width < 0:
                self.active = False
                self.border_width = 0
                self.direction = 1
            pygame.draw.circle(self.display_surface, "black", self.center, self.radius, int(self.border_width))


if __name__ == "__main__":
    game = Game()
    game.run()
