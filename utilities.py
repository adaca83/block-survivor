import pygame
import random
import math
import csv

class exp_Crystals: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y
        self.width = 5
        self.height = 5
        self.color = (0, 0, 255)
        self.speed = 5
        
        
    def draw(self, screen): 
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
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
            
            
class Game:
    enemy_probabilities={
        1: 0.5,
        2: 0.25,
        3: 0.15, 
        4: 0.07, 
        5: 0.03
    }
    MAX_LEVEL = 5
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 25
        self.spatial_grid = SpatialGrid(width, height, self.cell_size)
        self.player = Player(width // 2, height // 2, width, height, self)
        self.enemies = []
        self.walls = []
        self.crystals = []
        self.hordes = []
        self.next_horde_spawn_time = random.randint(50, 100)
        self.horde_interval = (50, 100)
        self.initialize_enemies(5)  # Initialize with 5 enemies
        self.font = pygame.font.Font(None, 36)
        self.hiscore_font = pygame.font.Font("assets/fonts/ARCADECLASSIC.ttf", 50)
        self.hiscore_file = "hiscore.csv"
        
        
        for enemy in self.enemies: 
            self.spatial_grid.add(enemy, enemy.x, enemy.y)

    def initialize_enemies(self, num_enemies):
        self.enemies = [Enemy(self, self.width, self.height, level=self.choose_enemy_level()) for _ in range(num_enemies)]

    def reset(self):
        self.player = Player(self.width // 2, self.height // 2, self.width, self.height, self)
        self.walls = []
        self.initialize_enemies(5)  # Reset with 5 enemies
        self.spatial_grid = SpatialGrid(self.width, self.height, self.cell_size)
        for enemy in self.enemies:
            self.spatial_grid.add(enemy, enemy.x, enemy.y)


    def check_collisions(self):
        player_hitbox = self.player.get_hitbox()
        for enemy in self.enemies[:]:
            if player_hitbox.colliderect(enemy.get_hitbox()):
                self.player.hp -= enemy.level
                self.spatial_grid.remove(enemy, enemy.x, enemy.y)
                self.enemies.remove(enemy)
                enemy.reset_position()
                self.enemies.append(enemy)
                self.spatial_grid.add(enemy, enemy.x, enemy.y)
                if self.player.hp <= 0:
                    return False
                
        for projectile in self.player.projectiles[:]:
            projectile_hitbox = projectile.get_hitbox()
            nearby_enemies = self.spatial_grid.get_nearby(projectile.x, projectile.y)
            for enemy in nearby_enemies:
                if projectile_hitbox.colliderect(enemy.get_hitbox()):
                    if projectile in self.player.projectiles:
                        self.player.projectiles.remove(projectile)
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        self.spatial_grid.remove(enemy, enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        crystal = exp_Crystals(enemy.x, enemy.y)
                        self.crystals.append(crystal)
                        enemy.reset_position()
                        self.enemies.append(enemy)
                        self.spatial_grid.add(enemy, enemy.x, enemy.y)
                    break

            for wall in self.walls:
                if projectile_hitbox.colliderect(wall.get_hitbox()):
                    if projectile in self.player.projectiles:
                        self.player.projectiles.remove(projectile)
                    break

        #to_remove = set()
        #new_enemies = []
        #current_time = pygame.time.get_ticks()


        #for enemy1 in self.enemies:
        #    nearby_enemies = self.spatial_grid.get_nearby(enemy1.x, enemy1.y)
        #    for enemy2 in nearby_enemies:
        #        if enemy1 != enemy2 and enemy1.get_hitbox().colliderect(enemy2.get_hitbox()):
        #            if (current_time - enemy1.last_evolution_time >= Enemy.COOLDOWN_TIME and
        #                    current_time - enemy2.last_evolution_time >= Enemy.COOLDOWN_TIME):
        #                new_level = min(enemy1.level + enemy2.level, self.MAX_LEVEL)
        #                to_remove.add(enemy1)
        #                to_remove.add(enemy2)
        #                new_enemy = Enemy(self, self.width, self.height, level=new_level)
        #                new_enemy.x, new_enemy.y = enemy1.x, enemy1.y
        #                new_enemies.append(new_enemy)
        #                break

        #for enemy in to_remove:
        #    if enemy in self.enemies:
        #        self.spatial_grid.remove(enemy, enemy.x, enemy.y)
        #        self.enemies.remove(enemy)
        #for new_enemy in new_enemies:
        #    self.enemies.append(new_enemy)
        #    self.spatial_grid.add(new_enemy, new_enemy.x, new_enemy.y)

        return True
    
    def choose_enemy_level(self): 
        levels, probabilities = zip(*self.enemy_probabilities.items())
        return random.choices(levels, probabilities)[0]

    def draw_life_meter(self, screen):
        life_text = self.font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        screen.blit(life_text, (10, 10))

    def draw_level_meter(self, screen):
        life_text = self.font.render(f"lvl: {self.player.level}", True, (255, 255, 255))
        screen.blit(life_text, (10, 40))    

    def draw_timer(self, screen, elapsed_time):
        timer_text = self.font.render(f"Time: {elapsed_time:.1f}s", True, (255, 255, 255))
        text_rect = timer_text.get_rect(center=(self.width // 2, 10))
        screen.blit(timer_text, text_rect)

    def run_startscreen(self, screen):
        welcome_1 = pygame.image.load("assets/images/welcome/welcome_screen.png")
        screen.blit(welcome_1,(0, 0))

    def run_new_hiscore(self, screen):
        newscore_1 = pygame.image.load("assets/images/hiscore/hiscore_screen.png")
        screen.blit(newscore_1,(0, 0))


    def fetch_hiscore(self):
        hiscore_list = []

        with open(self.hiscore_file, newline='', mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            all_scores = list(reader)

        for score in all_scores:
            edited_score = f"{score[0]}   {score[1]}   {score[2]}"
            hiscore_list.append(edited_score)

        return hiscore_list
    
    def check_if_highscore(self, elapsed_time):

        with open(self.hiscore_file, newline='', mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            all_scores = list(reader)
        
        for score_list in all_scores:
            if int(score_list[2]) < elapsed_time:
                return True
        return False
    
    def save_highscore(self, player_name, elapsed_time):
        with open(self.hiscore_file, newline='', mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            all_scores = list(reader)

        # Convert elapsed_time to int for comparison
        elapsed_time = int(elapsed_time)

        # Determine the position for the new score
        position = 1
        for i, score in enumerate(all_scores):
            if elapsed_time > int(score[2]):
                position = i + 1
                break
            else:
                position = i + 2

        # Add the new score entry
        new_score = [position, player_name, elapsed_time]
        all_scores.append(new_score)
        # Sort the scores: highest first
        all_scores.sort(key=lambda x: int(x[2]), reverse=True)
        # Keep only the top 3 scores
        all_scores = all_scores[:3]

        n = 1
        for score in all_scores:
            score[0] = n
            n+=1

        # Write back to the CSV
        with open(self.hiscore_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerows(all_scores)



    def run_credits(self, screen, elapsed_time):
        hiscore = self.fetch_hiscore()

        credit_1 = pygame.image.load("assets/images/credits/credit_screen.png")
        screen.blit(credit_1, (0, 0))
        screen.blit(self.font.render(f"{int(elapsed_time)}", False, "White"), (465, 154))

        n = 260
        for score in hiscore:
            screen.blit(self.hiscore_font.render(f"{score}", False, "White"), (230, n))
            n += 50
            
    def spawn_horde(self): 
        new_horde = Horde(self)
        self.hordes.append(new_horde)
        
    def update_hordes(self, elapsed_time): 
        if elapsed_time >= self.next_horde_spawn_time:
            self.spawn_horde()
            self.next_horde_spawn_time = elapsed_time + random.randint(*self.horde_interval)

        for horde in self.hordes:
            horde.update(elapsed_time)



    def run(self, FPS):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        clock = pygame.time.Clock()
        running = True
        startscreen = True
        game_active = False
        credit_screen = False
        new_hiscore_screen = False
        elapsed_time = 0
        player_name = ""

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if startscreen:
                        game_active = True
                        startscreen = False
                        credit_screen = False
                        start_time = pygame.time.get_ticks()

                    elif credit_screen:
                        if event.key == pygame.K_SPACE:
                            credit_screen = False
                            startscreen = False
                            self.reset()
                            game_active = True
                            start_time = pygame.time.get_ticks()

                        elif event.key == pygame.K_q:
                            credit_screen = False
                            running = False
                        
                    elif new_hiscore_screen:
                        if event.key == pygame.K_RETURN:
                            self.save_highscore(player_name, elapsed_time)
                            new_hiscore_screen = False
                            credit_screen = True
                            player_name = ""
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        else:
                            if len(player_name) < 6:
                                player_name += event.unicode

                    elif game_active and event.key == pygame.K_x:
                        game_active = False
                        if self.check_if_highscore(elapsed_time):
                            new_hiscore_screen = True
                        else:
                            credit_screen = True

            if startscreen:
                self.run_startscreen(screen)

            elif credit_screen:
                self.run_credits(screen, elapsed_time)

            elif new_hiscore_screen:
                self.run_new_hiscore(screen)
                input_box = pygame.Rect(self.width // 2 - 100, self.height // 2 - 20, 200, 40)
                color_active = pygame.Color('dodgerblue2')
                pygame.draw.rect(screen, color_active, input_box, 2)
                txt_surface = self.font.render(player_name, True, (255, 255, 255))
                screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

            elif game_active:
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                screen.fill((0, 0, 0))
                
                self.update_hordes(elapsed_time)
                
                for crystal in self.crystals: 
                    crystal.draw(screen)
                
                for wall in self.walls:
                    wall.draw(screen)

                for enemy in self.enemies:
                    enemy.update(self.player.x, self.player.y, self.walls)
                    enemy.draw(screen)

                self.player.update(self.enemies, self.walls, self.crystals)
                self.player.draw(screen)
                    
                self.player.draw_experience_bar(screen)
                self.draw_life_meter(screen)
                self.draw_level_meter(screen)
                self.draw_timer(screen, elapsed_time)
                
                if not self.check_collisions():
                    game_active = False

                    if self.check_if_highscore(elapsed_time):
                        new_hiscore_screen = True
                    else:
                        credit_screen = True

                # Increase the number of enemies every 5 seconds
                if int(elapsed_time) % 20 == 0 and len(self.enemies) < int(elapsed_time) // 20 + 5:
                    self.enemies.append(Enemy(self, self.width, self.height, level=self.choose_enemy_level()))

            pygame.display.flip()
            clock.tick(FPS)

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

    def __init__(self, game, game_width, game_height, level=None,):
        self.game = game
        self.radius = 10 + (level - 1) * 5  # Increase size slightly with each level
        self.color = self.LEVEL_COLORS.get(level, (255, 255, 255))  # Default to white if level not in dictionary
        self.game_width = game_width
        self.game_height = game_height
        self.speed = 1
        self.level = level
        self.hp = level
        self.last_evolution_time = pygame.time.get_ticks()  # Time of the last evolution
        self.reset_position()
        self.previous_x = self.x
        self.previous_y = self.y
        

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
        
        if not self.level:             
            self.level = self.game.choose_enemy_level()
        self.color = self.LEVEL_COLORS.get(self.level, (255, 255, 255))
        self.radius = 10 + (self.level - 1) * 5
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

class Horde:
    HORDE_MIN_SIZE = 16
    HORDE_MAX_SIZE = 16
    HORDE_SPACING = 10
    
    def __init__(self, game): 
        self.game = game
        self.enemies = []
        self.spawn_time = self.generate_next_spawn_time()
        self.pattern = self.choose_pattern()
        self.spawned = False
        
    def generate_next_spawn_time(self):
        return random.randint(1, 20)
    
    def choose_pattern(self): 
        return random.choice([
            "signle_row",
            "two_rows",
            "four_rows",
            "eight_rows",
            "sixteen_rows"
        ]) 
        
    def spawn(self):
        if self.spawned: 
            return 
        
        num_enemies = random.randint(
            self.HORDE_MIN_SIZE,
            self.HORDE_MAX_SIZE
        )
        positions = self.get_horde_positions_outside_of_view(self.pattern, num_enemies)
        
        for pos in positions: 
            enemy = Enemy(self.game, self.game.width, self.game.height, level=1)
            enemy.x, enemy.y = pos
            self.enemies.append(enemy)
            self.game.enemies.append(enemy)
            self.game.spatial_grid.add(enemy, enemy.x, enemy.y)
            
        self.spawned = True
        
    def get_horde_positions_outside_of_view(self, pattern, num_enemies):
        positions = []
        
        if pattern == "signle_row": 
            positions = self.generate_single_row(num_enemies)
        elif pattern == "two_rows": 
            positions = self.generate_two_rows(num_enemies)
        elif pattern == "four_rows": 
            positions = self.generate_four_rows(num_enemies)
        elif pattern == "eight_rows": 
            positions = self.generate_eight_rows(num_enemies)
        elif pattern == "sizteen_rows": 
            positions = self.generate_sixteen_rows(num_enemies)
        
        print(pattern)
        return positions 

    def generate_single_row(self, num_enemies): 
        start_x = random.randint(0, self.game.width)
        y = random.choice([0, self.game.height])
        return [(start_x + i * self.HORDE_SPACING, y) for i in range(num_enemies)]
    
    def generate_two_rows(self, num_enemies):
        start_x = random.randint(0, self.game.width)
        y1, y2 = 0, self.game.height
        row1 = [(start_x + i * self.HORDE_SPACING, y1) for i in range(num_enemies // 2)]
        row2 = [(start_x + i * self.HORDE_SPACING, y2) for i in range(num_enemies // 2, num_enemies)]
        return row1 + row2
    
    def generate_four_rows(self, num_enemies):
        start_x = random.randint(0, self.game.width)
        rows = [random.choice([0, self.game.height // 3, 2 * self.game.height // 3, self.game.height]) for _ in range(4)]
        return [(start_x + i * self.HORDE_SPACING, rows[i % 4]) for i in range(num_enemies)]

    def generate_eight_rows(self, num_enemies):
        start_x = random.randint(0, self.game.width)
        rows = [random.choice([i * self.game.height // 8 for i in range(8)]) for _ in range(8)]
        return [(start_x + i * self.HORDE_SPACING, rows[i % 8]) for i in range(num_enemies)]

    def generate_sixteen_rows(self, num_enemies):
        start_x = random.randint(0, self.game.width)
        rows = [i * self.game.height // 16 for i in range(16)]
        return [(start_x + i * self.HORDE_SPACING, rows[i % 16]) for i in range(num_enemies)]
    
    def update(self, elapsed_time): 
        if not self.spawned and elapsed_time >= self.spawn_time: 
            self.spawn()

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
        self.experience = 0
        self.level = 1
        self.pickup_radius = 100
        
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for projectile in self.projectiles:
            projectile.draw(screen)

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
        bar_width = self.game_width
        bar_height = 20
        filled_width = (self.experience / 100 ) * bar_width
        pygame.draw.rect(screen, (0, 0, 0), (0, self.game_height - bar_height, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 0, 255), (0, self.game_height - bar_height, filled_width, bar_height))
        
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

class SpatialGrid:
