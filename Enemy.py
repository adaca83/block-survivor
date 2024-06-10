import pygame
import random
import math

class Enemy:
    LEVEL_COLORS = {
        1: (0, 0, 255),   # Blue
        2: (0, 255, 0),   # Green
        3: (255, 255, 0), # Yellow
        4: (255, 165, 0), # Orange
        5: (255, 0, 0)    # Red
    }

    COOLDOWN_TIME = 5000  # Cooldown time in milliseconds

    def __init__(self, game, game_width, game_height, level=None, is_horde_enemy=False):
        self.game = game
        self.radius = 10 + (level - 1) * 5  # Increase size slightly with each level
        self.color = self.LEVEL_COLORS.get(level, (255, 255, 255))  # Default to white if level not in dictionary
        self.game_width = game_width
        self.game_height = game_height
        self.speed = 0.5
        self.level = level if level else self.game.choose_enemy_level()
        self.hp = self.level
        self.last_evolution_time = pygame.time.get_ticks()  # Time of the last evolution
        self.is_horde_enemy = is_horde_enemy
        self.reset_position()
        self.previous_x = self.x
        self.previous_y = self.y

    def set_attributes_based_on_level(self):
        self.radius = 10 + (self.level - 1) * 5
        self.color = self.LEVEL_COLORS.get(self.level, (255, 255, 255))
        self.hp = self.level

    def reset_position(self):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.x = random.randint(0, self.game_width - 2 * self.radius)
            self.y = self.radius
        elif edge == 'bottom':
            self.x = random.randint(0, self.game_width - 2 * self.radius)
            self.y = self.game_height - self.radius
        elif edge == 'left':
            self.x = self.radius
            self.y = random.randint(0, self.game_height - 2 * self.radius)
        elif edge == 'right':
            self.x = self.game_width - self.radius
            self.y = random.randint(0, self.game_height - 2 * self.radius)

        if not self.is_horde_enemy:
            self.level = self.game.choose_enemy_level()
            self.set_attributes_based_on_level()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (self.x + self.radius, self.y + self.radius),
                           self.radius)
        # Draw the HP inside the enemy
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.hp), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x + self.radius, self.y + self.radius))
        screen.blit(text, text_rect)

    def update(self, player_x, player_y, walls):
        # Calculate the direction to move
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance

        # Calculate new position
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Update previous position before changing to the new position
        self.previous_x, self.previous_y = self.x, self.y

        # Check for wall collisions and update position accordingly
        if not self.check_wall_collision(new_x, self.y, walls):
            self.x = new_x
        if not self.check_wall_collision(self.x, new_y, walls):
            self.y = new_y

        # Update spatial grid
        if self.game.spatial_grid.contains(self, self.previous_x, self.previous_y):
            self.game.spatial_grid.remove(self, self.previous_x, self.previous_y)
        self.game.spatial_grid.add(self, self.x, self.y)

    def check_wall_collision(self, x, y, walls):
        hitbox = pygame.Rect(x, y, 2 * self.radius, 2 * self.radius)
        for wall in walls:
            if hitbox.colliderect(wall.get_hitbox()):
                return True
        return False

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)