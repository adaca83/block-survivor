import pygame
import random
import csv

from exp_Crystals import * 
from Grid import * 
from Spatialgrid import *
from Enemy import * 
from Projectiles import * 
from Player import * 
from Horde import * 
from Loot import * 

class Game:
    enemy_probabilities={
        1: 0.65,
        2: 0.2,
        3: 0.1, 
        4: 0.04, 
        5: 0.01
    }
    MAX_LEVEL = 5
    
    def __init__(self, width, height):
        
        self.background_image = pygame.image.load(r"assets/images/background/expanded_grassfield.png")
        self.bg_width = self.background_image.get_width()
        self.bg_height = self.background_image.get_height()
        
        self.width = width
        self.height = height
        self.cell_size = 25
        self.spatial_grid = SpatialGrid(width, height, self.cell_size)
        self.player = Player(self.bg_width // 2, self.bg_height // 2, width, height, self)
        self.enemies = []
        self.walls = []
        self.crystals = []
        self.hordes = []
        self.next_horde_spawn_time = random.randint(50, 100)
        self.horde_interval = (50, 100)

        self.font = pygame.font.Font(None, 36)
        self.hiscore_font = pygame.font.Font("assets/fonts/ARCADECLASSIC.ttf", 50)
        self.hiscore_file = "hiscore.csv"
        self.loot_items = []

        # Percentage lootchange from each kill (0 - 100)
        self.lootchance = 10        
        self.initialize_enemies(5)  # Initialize with 5 enemies
        
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
                if not enemy.is_horde_enemy:
                    enemy.reset_position()
                    enemy.level = self.choose_enemy_level()
                    enemy.set_attributes_based_on_level()
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
                        if random.randint(1,100) <= self.lootchance:
                            new_loot = Loot(enemy)
                            self.loot_items.append(new_loot)

                            
                        self.spatial_grid.remove(enemy, enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        crystal = exp_Crystals(enemy.x, enemy.y)
                        self.crystals.append(crystal)
                        if not enemy.is_horde_enemy:
                            enemy.reset_position()
                            enemy.level = self.choose_enemy_level()
                            enemy.set_attributes_based_on_level()
                            self.enemies.append(enemy)
                            self.spatial_grid.add(enemy, enemy.x, enemy.y)
                    break

            for wall in self.walls:
                if projectile_hitbox.colliderect(wall.get_hitbox()):
                    if projectile in self.player.projectiles:
                        self.player.projectiles.remove(projectile)
                    break

        for loot in self.loot_items:
            if player_hitbox.colliderect(loot.get_hitbox()):
                self.player.new_weapon(loot)
                self.loot_items.remove(loot)

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
        #all_scores are sorted with the highest scores first and the top 3 scores are kept.
        all_scores = all_scores[:3]

        n = 1
        for score in all_scores:
            score[0] = n
            n += 1

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
                
                # Calculate offset to keep player centered
                offset_x = min(max(self.player.x - self.width // 2, 0), self.bg_width - self.width)
                offset_y = min(max(self.player.y - self.height // 2, 0), self.bg_height - self.height)
                
                screen.blit(self.background_image, (-offset_x, -offset_y))
                
                self.update_hordes(elapsed_time)
                
                for crystal in self.crystals: 
                    crystal.draw(screen, offset_x, offset_y)
                
                for wall in self.walls:
                    wall.draw(screen, offset_x, offset_y)

                for enemy in self.enemies:
                    enemy.update(self.player.x, self.player.y, self.walls)
                    enemy.draw(screen, offset_x, offset_y)

                for loot in self.loot_items:
                    loot.draw(screen, offset_x, offset_y)

                self.player.update(self.enemies, self.walls, self.crystals)
                self.player.draw(screen, offset_x, offset_y)
                    
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