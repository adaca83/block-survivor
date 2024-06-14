import pygame
import random

class Loot:
    projectiles = [
        {'color': (238, 75, 43), 'speed':5, 'width': 10, 'height': 10, 'shootspeed':500, 'duration': 10000},
        {'color': (255, 195, 0), 'speed':15, 'width': 5, 'height': 5, 'shootspeed':800, 'duration': 10000},
        {'color': (0, 0, 255), 'speed':2, 'width': 20, 'height': 20, 'shootspeed':100, 'duration': 2000}
    ]


    def __init__(self, enemy):
        self.chosen_loot = random.choices(
            self.projectiles, weights=[10, 10, 10], k=1
        )[0]

        triangle_size = 10

        self.enemy = enemy
        self.triangle_points = [
            (self.enemy.x, self.enemy.y - triangle_size),
            (self.enemy.x - triangle_size, self.enemy.y + triangle_size),
            (self.enemy.x + triangle_size, self.enemy.y + triangle_size)
        ]

    def draw(self, screen, offset_x, offset_y):
        self.screen = screen
        
        offset_points = [
            (self.triangle_points[0][0] - offset_x, self.triangle_points[0][1] - offset_y),
            (self.triangle_points[1][0] - offset_x, self.triangle_points[1][1] - offset_y),
            (self.triangle_points[2][0] - offset_x, self.triangle_points[2][1] - offset_y), 
        ]

        pygame.draw.polygon(screen, self.chosen_loot['color'], offset_points)

    def get_hitbox(self):
        min_x = min(point[0] for point in self.triangle_points)
        max_x = max(point[0] for point in self.triangle_points)
        min_y = min(point[1] for point in self.triangle_points)
        max_y = max(point[1] for point in self.triangle_points)

        width = max_x - min_x
        height = max_y - min_y

        return pygame.Rect(min_x, min_y, width, height)
