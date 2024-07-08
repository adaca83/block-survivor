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
    OFFSET = 50  # Maximum offset from the edge of the playing area for spawning

    def __init__(self, game, game_width, game_height, level=None, is_horde_enemy=False, player=None):
        self.player = player
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

        self.bg_width = game.bg_width
        self.bg_height = game.bg_height

        self.offset_x = min(max(self.player.x - self.game_width // 2, 0), self.bg_width - self.game_width)
        self.offset_y = min(max(self.player.y - self.game_height // 2, 0), self.bg_height - self.game_height)

        self.reset_position(self.offset_x, self.offset_y)
        self.sprite = None  # Defer loading sprite until it's drawn

    def set_attributes_based_on_level(self):
        self.radius = 10 + (self.level - 1) * 5
        self.color = self.LEVEL_COLORS.get(self.level, (255, 255, 255))
        self.hp = self.level

    def reset_position(self, offset_x, offset_y):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        offset = random.randint(0, self.OFFSET)
        if edge == 'top':
            self.x = random.randint(0, self.game_width) + offset_x
            self.y = -self.OFFSET + offset_y
        elif edge == 'bottom':
            self.x = random.randint(0, self.game_width) + offset_x
            self.y = self.game_height + self.OFFSET + offset_y
        elif edge == 'left':
            self.x = -self.OFFSET + offset_x
            self.y = random.randint(0, self.game_height) + offset_y
        elif edge == 'right':
            self.x = self.game_width + self.OFFSET + offset_x
            self.y = random.randint(0, self.game_height) + offset_y

        if not self.is_horde_enemy:
            self.level = self.game.choose_enemy_level()
            self.set_attributes_based_on_level()
            self.sprite = self.load_sprite()

    def draw(self, screen, offset_x, offset_y):
        if self.sprite is None:
            self.sprite = self.load_sprite()

        sprite = self.sprite
        if self.x < self.player.x: 
            sprite = pygame.transform.flip(self.sprite, True, False)
        
        sprite_rect = sprite.get_rect(center=(self.x - offset_x, self.y - offset_y))
        screen.blit(sprite, sprite_rect)

    def update(self, player_x, player_y, walls):

        if self.is_outside_boundary(player_x, player_y):
            self.reset_position_around_player(player_x, player_y)
            return

        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        self.previous_x, self.previous_y = self.x, self.y

        if not self.check_wall_collision(new_x, self.y, walls):
            self.x = new_x
        if not self.check_wall_collision(self.x, new_y, walls):
            self.y = new_y

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
    
    def load_sprite(self):
        enemy_path = "assets/images/enemies/"
        if self.level == 1: 
            size_scale = 0.5
            color = "green"
            sprites = [
                enemy_path+str("enemy_")+color+str("_A_128.png"),
                enemy_path+str("enemy_")+color+str("_B_128.png"),
                enemy_path+str("enemy_")+color+str("_C_128.png"),
                enemy_path+str("enemy_")+color+str("_D_128.png"),
                        ]
            sprite_path = random.choice(sprites)
        elif self.level == 2:
            size_scale = 0.5 
            color = "green"
            sprites = [
                enemy_path+str("enemy_")+color+str("_E_128.png"),
                enemy_path+str("enemy_")+color+str("_F_128.png"),
                enemy_path+str("enemy_")+color+str("_G_128.png"),
                        ]
            sprite_path = random.choice(sprites)
        elif self.level == 3:
            size_scale = 0.75 
            color = "red"
            sprites = [
                enemy_path+str("enemy_")+color+str("_A_128.png"),
                enemy_path+str("enemy_")+color+str("_B_128.png"),
                enemy_path+str("enemy_")+color+str("_C_128.png"),
                        ]
            sprite_path = random.choice(sprites)
        elif self.level == 4:
            size_scale = 1 
            color = "black"
            sprites = [
                enemy_path+str("enemy_")+color+str("_A_128.png"),
                enemy_path+str("enemy_")+color+str("_D_128.png"),
                enemy_path+str("enemy_")+color+str("_C_128.png"),
                        ]
            sprite_path = random.choice(sprites)
        elif self.level == 5: 
            size_scale = 1.25
            color = "black"
            sprites = [
                enemy_path+str("enemy_")+color+str("_B_128.png"),
                enemy_path+str("enemy_")+color+str("_E_128.png"),
                enemy_path+str("enemy_")+color+str("_F_128.png"),
                enemy_path+str("enemy_")+color+str("_G_128.png"),
                        ]
            sprite_path = random.choice(sprites)

        sprite = pygame.image.load(sprite_path).convert_alpha()
        sprite = pygame.transform.scale(sprite, (64*size_scale, 64*size_scale))

        return sprite

    def is_outside_boundary(self, player_x, player_y):
        boundary_distance = max(self.game_width, self.game_height) // 2 + self.OFFSET
        return (self.x < player_x - boundary_distance or self.x > player_x + boundary_distance or
                self.y < player_y - boundary_distance or self.y > player_y + boundary_distance)

    def reset_position_around_player(self, player_x, player_y):
        angle = random.uniform(0, 2 * math.pi)
        radius = max(self.game_width, self.game_height) // 2 + self.OFFSET
        self.x = player_x + radius * math.cos(angle)
        self.y = player_y + radius * math.sin(angle)
        self.level = self.game.choose_enemy_level()
        self.set_attributes_based_on_level()
        self.sprite = self.load_sprite()
