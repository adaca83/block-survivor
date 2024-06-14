import pygame
import math

class Projectile:
    # Standard projectile values
    default_width = 5
    default_height = 5
    default_color = (128, 128, 128)
    default_speed = 10

    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.width = self.default_width
        self.height = self.default_height
        self.color = self.default_color
        self.speed = self.default_speed
        self.target_x = target_x
        self.target_y = target_y
        self.calculate_velocity()

    def calculate_velocity(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance
        self.velocity_x = dx * self.speed
        self.velocity_y = dy * self.speed

    @classmethod
    def set_new_projectile(cls, loot:dict):
        cls.default_width = loot.chosen_loot['width']
        cls.default_height = loot.chosen_loot['height']
        cls.default_color = loot.chosen_loot['color']
        cls.default_speed = loot.chosen_loot['speed']

    @classmethod
    def reset_projectile(cls):
        cls.default_width = 5
        cls.default_height = 5
        cls.default_color = (128, 128, 128)
        cls.default_speed = 10

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.rect(screen, self.color, (self.x - offset_x, self.y - offset_y, self.width, self.height))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)