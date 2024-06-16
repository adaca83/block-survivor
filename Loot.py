import pygame
import random

class Loot:
    projectiles = [
        {'color': (238, 75, 43), 'speed':5, 'width': 10, 'height': 10, 'shootspeed':500, 'duration': 10000},
        {'color': (255, 195, 0), 'speed':15, 'width': 5, 'height': 5, 'shootspeed':800, 'duration': 10000},
        {'color': (0, 0, 255), 'speed':2, 'width': 20, 'height': 20, 'shootspeed':100, 'duration': 2000}
    ]

    cosmetics = [
        "assets/images/cosmetics/hats/hat01.png",
        "assets/images/cosmetics/hats/hat02.png"
    ]


    def __init__(self, enemy):
        self.enemy = enemy
        if random.randint(0, 1) == 1:  # 50/50 chance for cosmetic or projectile loot
            self.is_cosmetic = False
            self.chosen_loot = random.choice(self.projectiles)
            triangle_size = 10
            self.triangle_points = [
                (self.enemy.x, self.enemy.y - triangle_size),
                (self.enemy.x - triangle_size, self.enemy.y + triangle_size),
                (self.enemy.x + triangle_size, self.enemy.y + triangle_size)
            ]
        else:
            self.is_cosmetic = True
            self.chosen_loot = random.choice(self.cosmetics)
            self.image = pygame.image.load(self.chosen_loot)
            self.image_rect = self.image.get_rect(center=(self.enemy.x, self.enemy.y - self.image.get_height() // 2))

    def is_weapon(self):
        return isinstance(self.chosen_loot, dict)
    
    def get_hat_location(self):
        return self.chosen_loot

    def draw(self, screen, offset_x, offset_y):
        if self.is_cosmetic:
            # Adjust the position based on the offset
            image_pos = (self.image_rect.x - offset_x, self.image_rect.y - offset_y)
            screen.blit(self.image, image_pos)
        else:
            offset_points = [
                (point[0] - offset_x, point[1] - offset_y) for point in self.triangle_points
            ]
            pygame.draw.polygon(screen, self.chosen_loot['color'], offset_points)

    def get_hitbox(self):
        if self.is_cosmetic:
            return self.image_rect
        else:
            min_x = min(point[0] for point in self.triangle_points)
            max_x = max(point[0] for point in self.triangle_points)
            min_y = min(point[1] for point in self.triangle_points)
            max_y = max(point[1] for point in self.triangle_points)

            width = max_x - min_x
            height = max_y - min_y

            return pygame.Rect(min_x, min_y, width, height)
