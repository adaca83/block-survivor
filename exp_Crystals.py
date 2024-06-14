import pygame
import math


class exp_Crystals: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y
        self.width = 5
        self.height = 5
        self.color = (0, 0, 255)
        self.speed = 5
        
        
    def draw(self, screen, offset_x, offset_y): 
        pygame.draw.rect(screen, self.color, (self.x - offset_x, self.y - offset_y, self.width, self.height))
        
    def get_hitbox(self): 
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed