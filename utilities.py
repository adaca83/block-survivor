class Game:
    MAX_LEVEL = 5
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player(width // 2, height // 2, width, height, self)
        self.enemies = []
        self.walls = []
        self.initialize_enemies(5)  # Initialize with 5 enemies
        self.font = pygame.font.Font(None, 36)

    def initialize_enemies(self, num_enemies):
        self.enemies = [Enemy(self.width, self.height) for _ in range(num_enemies)]

    def reset(self):
        self.player = Player(self.width // 2, self.height // 2, self.width, self.height, self)
        self.walls = []
        self.initialize_enemies(5)  # Reset with 5 enemies

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
                    if projectile in self.player.projectiles:
                        self.player.projectiles.remove(projectile)
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        enemy.reset_position()
                        self.enemies.append(enemy)
                    break

            for wall in self.walls:
                if projectile_hitbox.colliderect(wall.get_hitbox()):
                    if projectile in self.player.projectiles:
                        self.player.projectiles.remove(projectile)
                    break

        to_remove = set()
        new_enemies = []
        current_time = pygame.time.get_ticks()

        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i + 1:]:
                if enemy1.get_hitbox().colliderect(enemy2.get_hitbox()):
                    # Check cooldown before allowing evolution
                    if (current_time - enemy1.last_evolution_time >= Enemy.COOLDOWN_TIME and
                            current_time - enemy2.last_evolution_time >= Enemy.COOLDOWN_TIME):
                        new_level = min(enemy1.level + enemy2.level, self.MAX_LEVEL)  # Cap the maximum level at 10
                        to_remove.add(enemy1)
                        to_remove.add(enemy2)
                        new_enemy = Enemy(self.width, self.height, level=new_level)
                        new_enemy.x, new_enemy.y = enemy1.x, enemy1.y
                        new_enemies.append(new_enemy)
                        break

        for enemy in to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        self.enemies.extend(new_enemies)

        return True

    def draw_life_meter(self, screen):
        life_text = self.font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        screen.blit(life_text, (10, 10))

    def draw_timer(self, screen, elapsed_time):
        timer_text = self.font.render(f"Time: {elapsed_time:.1f}s", True, (255, 255, 255))
        text_rect = timer_text.get_rect(center=(self.width // 2, 10))
        screen.blit(timer_text, text_rect)

    def run(self, FPS):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        running = True
        while running:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            self.player.update(self.enemies, self.walls)
            self.player.draw(screen)
            for enemy in self.enemies:
                enemy.update(self.player.x, self.player.y, self.walls)
                enemy.draw(screen)
            for wall in self.walls:
                wall.draw(screen)
            self.draw_life_meter(screen)
            self.draw_timer(screen, elapsed_time)
            if not self.check_collisions():
                running = False
            pygame.display.flip()
            clock.tick(FPS)

            # Increase the number of enemies every 20 seconds
            if int(elapsed_time) % 5 == 0 and len(self.enemies) < int(elapsed_time) // 5 + 5:
                self.enemies.append(Enemy(self.width, self.height))

        pygame.quit()

class Enemy:
    LEVEL_COLORS = {
        1: (0, 0, 255),   # Blue
        2: (0, 255, 0),   # Green
        3: (255, 255, 0), # Yellow
        4: (255, 165, 0), # Orange
        5: (255, 0, 0)    # Red
    }

    COOLDOWN_TIME = 5000  # Cooldown time in milliseconds

    def __init__(self, game_width, game_height, level=1):
        self.radius = 10 + (level - 1) * 5  # Increase size slightly with each level
        self.color = self.LEVEL_COLORS.get(level, (255, 255, 255))  # Default to white if level not in dictionary
        self.game_width = game_width
        self.game_height = game_height
        self.speed = 1
        self.level = level
        self.hp = level
        self.last_evolution_time = pygame.time.get_ticks()  # Time of the last evolution
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
        self.hp = self.level  # Ensure HP is reset to the level value
        self.last_evolution_time = pygame.time.get_ticks()  # Reset the evolution cooldown

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
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if not self.check_wall_collision(new_x, self.y, walls):
            self.x = new_x
        if not self.check_wall_collision(self.x, new_y, walls):
            self.y = new_y

    def check_wall_collision(self, x, y, walls):
        hitbox = pygame.Rect(x, y, 2 * self.radius, 2 * self.radius)
        for wall in walls:
            if hitbox.colliderect(wall.get_hitbox()):
                return True
        return False

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.matrix = [[0 for _ in range(width)] for _ in range(height)]
    
    def is_within_bounds(self, node):
        x, y = node
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_walkable(self, node):
        x, y = node
        return self.matrix[y][x] == 0

    
class Player:
    def __init__(self, x, y, game_width, game_height, game):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.color = (255, 0, 0)
        self.speed = 5
        self.game_width = game_width
        self.game_height = game_height
        self.hp = 5
        self.projectiles = []
        self.last_shot_time = 0
        self.shot_interval = 500  # milliseconds
        self.game = game  # Reference to the game instance

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for projectile in self.projectiles:
            projectile.draw(screen)

    def update(self, enemies, walls):
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
        self.handle_collisions(walls)
        self.shoot(enemies)
        for projectile in self.projectiles:
            projectile.update()

        if keys[pygame.K_w]:
            self.build_wall()

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
                projectile = Projectile(self.x + self.width // 2, self.y + self.height // 2, nearest_enemy.x, nearest_enemy.y)
                self.projectiles.append(projectile)
                self.last_shot_time = current_time

    def distance_to(self, enemy):
        dx = enemy.x - self.x
        dy = enemy.y - self.y
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

class Environment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = (0, 255, 0)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
