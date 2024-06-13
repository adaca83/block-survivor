import pygame
import math

from Projectiles import * 
from Environment import * 

class Player:
    def __init__(self, x, y, game_width, game_height, game):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.color = (255, 0, 0)
        self.speed = 5
        self.hp = 5
        self.projectiles = []
        self.last_shot_time = 0
        self.shot_interval = 500  # milliseconds
        self.game = game  # Reference to the game instance
        self.experience = 0
        self.level = 1
        self.pickup_radius = 100
        self.change_weapon = False
        self.projectile_info = None
        self.weapon_change_time = None

    def new_weapon(self, projectile:dict):
        self.projectile_info = projectile
        self.change_weapon = True
        
    def draw(self, screen, offset_x, offset_y):
        pygame.draw.rect(screen, self.color, (self.x - offset_x, self.y - offset_y, self.width, self.height))
        for projectile in self.projectiles:
            projectile.draw(screen, offset_x, offset_y)

    def update(self, enemies, walls, crystals):
        keys = pygame.key.get_pressed()
        movement_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_UP]:
            movement_vector += pygame.Vector2(0, -1)
        if keys[pygame.K_DOWN]:
            movement_vector += pygame.Vector2(0, 1)
        if keys[pygame.K_LEFT]:
            movement_vector += pygame.Vector2(-1, 0)
        if keys[pygame.K_RIGHT]:
            movement_vector += pygame.Vector2(1, 0)
        if movement_vector.length() > 0:
            movement_vector.normalize_ip()
            movement_vector *= self.speed
            
        new_x = self.x + movement_vector.x
        new_y = self.y + movement_vector.y
        
        bg_width = self.game.background_image.get_width()
        bg_height = self.game.background_image.get_height()
        
        half_player_width = self.width // 2
        half_player_height = self.height // 2 + 30  # The 30 is to avoid the exp bar
        
        if self.width // 2 <= new_x <= bg_width - half_player_width: 
            self.x = new_x
        if self.height // 2 <= new_y <= bg_height - half_player_height: 
            self.y = new_y
            
            
        self.handle_collisions(walls)
        self.shoot(enemies)
        for projectile in self.projectiles:
            projectile.update()

        if keys[pygame.K_w]:
            self.build_wall()
            
        self.collect_crystals(crystals)
        
    def collect_crystals(self, crystals): 
        for crystal in crystals[:]: 
            distance = self.distance_to(crystal)
            if distance <= self.pickup_radius: 
                crystal.move_towards(self.x + self.width // 2, 
                                    self.y + self.height // 2
                                    )
                
                if self.get_hitbox().colliderect(crystal.get_hitbox()): 
                    crystals.remove(crystal)
                    self.add_experience(10)
                
    def distance_to(self, entity): 
        dx = entity.x - self.x 
        dy = entity.y - self.y
        return math.sqrt(dx**2 + dy**2)
    
    def add_experience(self, amount): 
        self.experience += amount
        if self.experience >= 100: 
            self.experience = 0
            self.level += 1
            
    def draw_experience_bar(self, screen): 
        bar_width = self.game.width
        bar_height = 20
        filled_width = (self.experience / 100 ) * bar_width
        pygame.draw.rect(screen, (0, 0, 0), (0, self.game.height - bar_height, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 0, 255), (0, self.game.height - bar_height, filled_width, bar_height))
        
    def handle_collisions(self, walls):
        for wall in walls:
            if self.get_hitbox().colliderect(wall.get_hitbox()):
                self.resolve_collision(wall.get_hitbox())

    def resolve_collision(self, rect):
        if self.x < rect.x:
            self.x = rect.x - self.width
        elif self.x + self.width > rect.x + rect.width:
            self.x = rect.x + rect.width
        if self.y < rect.y:
            self.y = rect.y - self.height
        elif self.y + self.height > rect.y + rect.height:
            self.y = rect.y + rect.height

    def build_wall(self):
        wall = Environment(self.x, self.y)
        self.game.walls.append(wall)

    def shoot(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_interval:
            if enemies:
                nearest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
                target_x = nearest_enemy.x + nearest_enemy.radius
                target_y = nearest_enemy.y + nearest_enemy.radius

                projectile = Projectile(self.x + self.width // 2, self.y + self.height // 2, target_x, target_y)
                self.projectiles.append(projectile)
                self.last_shot_time = current_time

                if self.change_weapon:
                    projectile.set_new_projectile(self.projectile_info)
                    self.shot_interval = self.projectile_info.chosen_loot['shootspeed']
                    self.change_weapon = False
                    self.weapon_change_time = current_time
                
                if self.weapon_change_time is not None and (current_time - self.weapon_change_time) >= self.projectile_info.chosen_loot['duration']:
                    projectile.reset_projectile()
                    self.shot_interval = 500

    def distance_to(self, enemy):
        dx = enemy.x - self.x
        dy = enemy.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)