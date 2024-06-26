import pygame

class Environment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = (0, 255, 0)

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.rect(screen, self.color, (self.x - offset_x, self.y - offset_y, self.width, self.height))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)