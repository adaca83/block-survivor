import pygame
import random
import math

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player(width // 2, height // 2, width, height)
        self.enemies = []
        self.initialize_enemies(5)  # Initialize with 5 enemies
        self.font = pygame.font.Font(None, 36)
        self.start_time = pygame.time.get_ticks()  # Record the start time
        self.last_enemy_increase_time = self.start_time  # Record the time for enemy increase

    def initialize_enemies(self, num_enemies):
        self.enemies = [Enemy(self.width, self.height) for _ in range(num_enemies)]

    def add_enemy(self):
        self.enemies.append(Enemy(self.width, self.height))

    def reset(self):
        self.player = Player(self.width // 2, self.height // 2, self.width, self.height)
        self.initialize_enemies(5)  # Reset with 5 enemies
        self.start_time = pygame.time.get_ticks()  # Reset the start time
        self.last_enemy_increase_time = self.start_time  # Reset the enemy increase time

    def check_collisions(self):
        player_hitbox = self.player.get_hitbox()
        for enemy in self.enemies[:]:
            if player_hitbox.colliderect(enemy.get_hitbox()):
                self.player.hp -= 1
                self.enemies.remove(enemy)
                enemy.reset_position()
                self.enemies.append(enemy)
                if self.player.hp <= 0:
                    return False
        for projectile in self.player.projectiles[:]:
            projectile_hitbox = projectile.get_hitbox()
            for enemy in self.enemies[:]:
                if projectile_hitbox.colliderect(enemy.get_hitbox()):
                    self.player.projectiles.remove(projectile)
                    self.enemies.remove(enemy)
                    enemy.reset_position()
                    self.enemies.append(enemy)
        return True

    def draw_life_meter(self, screen):
        life_text = self.font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        screen.blit(life_text, (10, 10))

    def draw_timer(self, screen):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = self.font.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
        screen.blit(timer_text, (self.width // 2 - timer_text.get_width() // 2, 10))

    def update_enemy_count(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_enemy_increase_time) >= 20000:  # 20000 ms = 20 seconds
            self.add_enemy()
            self.last_enemy_increase_time = current_time

    def run(self, FPS):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Handle the quit event
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        running = False
            if running:
                screen.fill((0, 0, 0))
                self.player.update(self.enemies)
                self.player.draw(screen)
                for enemy in self.enemies:
                    enemy.update(self.player.x, self.player.y)
                    enemy.draw(screen)
                self.draw_life_meter(screen)
                self.draw_timer(screen)  # Draw the timer
                self.update_enemy_count()  # Update enemy count based on time
                running = self.check_collisions()
                pygame.display.flip()
                clock.tick(FPS)
        pygame.quit()  # Quit Pygame after the game loop ends

class Enemy:
    def __init__(self, game_width, game_height):
        self.radius = 10
        self.color = (0, 0, 255)
        self.game_width = game_width
        self.game_height = game_height
        self.speed = 1
        self.reset_position()

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

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (self.x + self.radius, self.y + self.radius),
                           self.radius)

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance
        self.x += dx * self.speed
        self.y += dy * self.speed
        if self.y > self.game_height:
            self.reset_position()

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)

class Player:
    def __init__(self, x, y, game_width, game_height):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 28
        self.color = (255, 0, 0)
        self.speed = 5
        self.game_width = game_width
        self.game_height = game_height
        self.hp = 5
        self.projectiles = []
        self.last_shot_time = 0
        self.shot_interval = 500  # milliseconds

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for projectile in self.projectiles:
            projectile.draw(screen)

    def update(self, enemies):
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
        if 0 <= new_x <= self.game_width - self.width:
            self.x = new_x
        if 0 <= new_y <= self.game_height - self.height:
            self.y = new_y
        self.shoot(enemies)
        for projectile in self.projectiles:
            projectile.update()

    def shoot(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_interval:
            if enemies:
                nearest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
                projectile = Projectile(self.x + self.width // 2, self.y + self.height // 2,
                                        nearest_enemy.x + nearest_enemy.radius, nearest_enemy.y + nearest_enemy.radius)
                self.projectiles.append(projectile)
                self.last_shot_time = current_time

    def distance_to(self, enemy):
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=10):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 5
        self.color = (128, 128, 128)
        self.speed = speed
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

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
