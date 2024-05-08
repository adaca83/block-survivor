import pygame
import random
import math

class GameMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.menu_options = ["Start Game", "High Scores", "Controls", "Settings", "Quit"]
        self.selected_option = 0
        self.last_input_time = 0
        self.screen = pygame.display.set_mode((width, height))

    def draw_menu(self, screen):
        screen.fill((255, 255, 255))
        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.menu_options):
            text = font.render(option, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.width // 2, 200 + i * 50))
            screen.blit(text, text_rect)
            if i == self.selected_option:
                pygame.draw.rect(screen, (255, 0, 0), text_rect, 2)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if current_time - self.last_input_time > 250:
            if keys[pygame.K_UP]:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                self.last_input_time = current_time
            elif keys[pygame.K_DOWN]:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                self.last_input_time = current_time
        if keys[pygame.K_RETURN]:
            selected_option_text = self.menu_options[self.selected_option]
            return selected_option_text

    def run_menu(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Quit"
            selected_option = self.handle_input()
            self.draw_menu(self.screen)
            pygame.display.flip()
            if selected_option:
                return selected_option

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player(width // 2, height // 2, width, height)
        self.enemies = []

    def reset(self):
        self.enemies.clear()

    def run(self, FPS):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            self.player.update()
            self.player.draw(screen)
            for enemy in self.enemies:
                enemy.update(self.player.x, self.player.y)
                enemy.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

class Enemy:
    def __init__(self, game_width, game_height):
        self.radius = 10
        self.color = (0, 0, 255)
        self.game_width = game_width
        self.game_height = game_height
        self.speed = 1
        self.reset_position()

    def reset_position(self):
        self.x = random.randint(0, self.game_width - 2 * self.radius)
        self.y = 0

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

    def draw(self, screen):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width, self.height))

    def update(self):
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
