import pygame
from settings import *
from timer import Timer

ROBOT_COLORS = [
    pygame.Color(255, 0, 0),
    pygame.Color(0, 255, 0),
    pygame.Color(0, 0, 255),
    pygame.Color(255, 255, 0),
    pygame.Color(255, 165, 0),
    pygame.Color(128, 0, 128),
]


class Robot(pygame.sprite.Sprite):
    robot_counter = 0

    def __init__(self, pos, group, obstacle_sprites):
        super().__init__(group)
        self.next_pos_index = 0
        self.pos_top_left = pos
        self.image = pygame.image.load('graphics/robot_player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy().inflate(0, -26)

        self.color = ROBOT_COLORS[Robot.robot_counter % len(ROBOT_COLORS)]
        Robot.robot_counter += 1

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.obstacle_sprites = obstacle_sprites

        self.path = []
        self.collision_rects = []
        self.path_timer = Timer(500)

        self.can_move = False
        self.pause_timer = Timer(1500)
        self.paused_index = []
        self.reset = False

    def update_position(self):
        self.rect.topleft = self.pos_top_left
        self.hitbox.topleft = self.pos_top_left
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.can_move = False
        self.next_pos_index = 0
        self.paused_index = []
        if self.reset:
            self.reset = False
            self.create_collision_rect()

    def set_path(self, path):
        del path[0]
        self.path = path
        self.create_collision_rect()

    def create_collision_rect(self):
        if self.path:
            self.collision_rects = []
            for point in self.path:
                x = (point.x * TILE_SIZE) + TILE_SIZE / 2
                y = (point.y * TILE_SIZE) + TILE_SIZE / 2
                rect = pygame.Rect((x - 2, y - 2), (4, 4))
                self.collision_rects.append(rect)

    def get_direction(self):
        if self.collision_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center)
            if end - start:
                self.direction = (end - start).normalize()
        else:
            self.direction = pygame.math.Vector2(0, 0)
            self.next_pos_index = 0
            self.paused_index = []
            self.reset = True
            self.path_timer.deactivate()

    def check_collision(self):
        if self.collision_rects:
            for rect in self.collision_rects:
                if rect.collidepoint(self.pos):
                    del self.collision_rects[0]
                    self.next_pos_index += 1
                    self.get_direction()

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if keys[pygame.K_s] or self.path_timer.active:
            self.get_direction()
            self.path_timer.activate()
            self.can_move = True

    def move(self, dt):
        if self.pause_timer.active or not self.can_move:
            return

        if len(self.path) > 1:
            if self.next_pos_index >= len(self.path) - 1:
                self.next_pos_index = len(self.path) - 2

            if self.next_pos_index == 0:
                current_pos = pygame.math.Vector2((self.path[self.next_pos_index].x * TILE_SIZE),
                                                  (self.path[self.next_pos_index].y * TILE_SIZE), )

                next_pos = pygame.math.Vector2(
                    (self.path[self.next_pos_index + 1].x * TILE_SIZE),
                    (self.path[self.next_pos_index + 1].y * TILE_SIZE),
                )
            else:
                current_pos = pygame.math.Vector2((self.path[self.next_pos_index - 1].x * TILE_SIZE),
                                                  (self.path[self.next_pos_index - 1].y * TILE_SIZE), )

                next_pos = pygame.math.Vector2(
                    (self.path[self.next_pos_index].x * TILE_SIZE),
                    (self.path[self.next_pos_index].y * TILE_SIZE),
                )

            if current_pos == next_pos and self.next_pos_index not in self.paused_index:
                self.pause_timer.activate()
                if self.next_pos_index == 0:
                    self.paused_index.append(self.next_pos_index + 1)
                    self.paused_index.append(self.next_pos_index)

                else:
                    self.paused_index.append(self.next_pos_index)
                return

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision("vertical")
        self.check_collision()
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery

    def update(self, dt, grid, start_coords, end_coords):
        self.path_timer.update()
        self.pause_timer.update()
        self.input()
        self.move(dt)
