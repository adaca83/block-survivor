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
from Animator import *
from Level_Up_Menu import level_up_menu  # Import the level_up_menu class

class Game:
    enemy_probabilities = {
        1: 0.65,
        2: 0.2,
        3: 0.1,
        4: 0.04,
        5: 0.01
    }
    MAX_LEVEL = 5

    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        # Initialization code remains the same
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
        self.next_horde_spawn_time = random.randint(10, 30)
        self.horde_interval = (10, 30)
        self.font = pygame.font.Font(None, 36)
        self.hiscore_font = pygame.font.Font("assets/fonts/ARCADECLASSIC.ttf", 50)
        self.hiscore_file = "hiscore.csv"
        self.loot_items = []
        self.lootchance = 30
        self.initialize_enemies(50)  # Initialize with 5 enemies
        self.animator = Animator()
        self.level_up_menu = level_up_menu(width, height, self.font, self.player)  # Initialize level up menu

        for enemy in self.enemies: 
            self.spatial_grid.add(enemy, enemy.x, enemy.y)

        

    def initialize_enemies(self, num_enemies):
        self.enemies = [Enemy(self, self.width, self.height, level=self.choose_enemy_level(), player=self.player) for _ in range(num_enemies)]

    def reset(self):
        self.player = Player(self.width // 2, self.height // 2, self.width, self.height, self)
        self.walls = []
        self.initialize_enemies(5)  # Reset with 5 enemies
        self.spatial_grid = SpatialGrid(self.width, self.height, self.cell_size)
        for enemy in self.enemies:
            self.spatial_grid.add(enemy, enemy.x, enemy.y)

    def check_collisions(self, offset_x, offset_y):
        player_hitbox = self.player.get_hitbox()
        for enemy in self.enemies[:]:
            if player_hitbox.colliderect(enemy.get_hitbox()):
                self.player.hp -= enemy.level
                self.spatial_grid.remove(enemy, enemy.x, enemy.y)
                self.enemies.remove(enemy)
                if not enemy.is_horde_enemy:
                    enemy.reset_position(offset_x, offset_y)
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
                        self.animator.death_animation(enemy)
                        if random.randint(1, 100) <= self.lootchance:
                            new_loot = Loot(enemy)
                            self.loot_items.append(new_loot)
                        self.spatial_grid.remove(enemy, enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        crystal = exp_Crystals(enemy.x, enemy.y)
                        self.crystals.append(crystal)
                        if not enemy.is_horde_enemy:
                            enemy.reset_position(offset_x, offset_y)
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
                if loot.is_weapon():
                    self.player.new_weapon(loot)
                else:
                    hat = loot.get_hat_location()
                    self.player.add_hat(hat)
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
        screen.blit(welcome_1, (0, 0))

    def run_new_hiscore(self, screen):
        newscore_1 = pygame.image.load("assets/images/hiscore/hiscore_screen.png")
        screen.blit(newscore_1, (0, 0))

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

        elapsed_time = int(elapsed_time)
        position = 1
        for i, score in enumerate(all_scores):
            if elapsed_time > int(score[2]):
                position = i + 1
                break
            else:
                position = i + 2
        new_score = [position, player_name, elapsed_time]
        all_scores.append(new_score)
        all_scores.sort(key=lambda x: int(x[2]), reverse=True)
        all_scores = all_scores[:3]

        n = 1
        for score in all_scores:
            score[0] = n
            n += 1

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
        offset_x, offset_y = self.xy_offset()
        new_horde = Horde(self, player=self.player, offset_x=offset_x, offset_y=offset_y)
        self.hordes.append(new_horde)
        
    def update_hordes(self, elapsed_time): 
        if elapsed_time >= self.next_horde_spawn_time:
            self.spawn_horde()
            self.next_horde_spawn_time = elapsed_time + random.randint(*self.horde_interval)
        for horde in self.hordes:
            horde.update(elapsed_time)
    
    def xy_offset(self): 
        x = min(max(self.player.x - self.width // 2, 0), self.bg_width - self.width)
        y = min(max(self.player.y - self.height // 2, 0), self.bg_height - self.height)
        return x, y
    
    def draw(self, screen, offset_x, offset_y, elapsed_time):
        for crystal in self.crystals: 
            crystal.draw(screen, offset_x, offset_y)
        for wall in self.walls: 
            wall.draw(screen, offset_x, offset_y)
        for enemy in self.enemies: 
            enemy.draw(screen, offset_x, offset_y)
        for loot in self.loot_items: 
            loot.draw(screen, offset_x, offset_y)
        self.animator.draw_death_animations(screen, offset_x, offset_y)
        self.player.draw(screen, offset_x, offset_y)
        self.player.draw_experience_bar(screen)
        self.draw_life_meter(screen)
        self.draw_level_meter(screen)
        self.draw_timer(screen, elapsed_time)    

    def update(self, elapsed_time):
        self.update_hordes(elapsed_time)
        for enemy in self.enemies: 
            enemy.update(self.player.x, self.player.y, self.walls)
        self.animator.update_death_animation()
        self.player.update(self.enemies, self.walls, self.crystals)  

    def handle_keydown(self, event): 
        if self.state == "start_screen": 
            if event.key == pygame.K_RETURN: 
                self.start_game()
        elif self.state == "game_active":
            if event.key == pygame.K_x: 
                self.end_game()
        elif self.state == "credit_screen": 
            if event.key == pygame.K_SPACE:
                self.restart_game()
            elif event.key == pygame.K_q: 
                self.quit_game()
        elif self.state == "new_highscore": 
            if event.key == pygame.K_RETURN: 
                self.save_and_show_credits()
            elif event.key == pygame.K_BACKSPACE: 
                self.player_name = self.player_name[:-1]
            else: 
                if len(self.player_name) < 6: 
                    self.player_name += event.unicode
        elif self.state == "level_up_menu":
            self.level_up_menu.handle_event(event)

    def update_start_screen(self): 
        pass 

    def draw_start_screen(self, screen):
        self.run_startscreen(screen) 

    def update_game_active(self): 
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        offset_x, offset_y = self.xy_offset()
        self.update(self.elapsed_time)
        if not self.check_collisions(offset_x, offset_y):
            self.end_game()
        if self.player.level_up:
            self.player.level_up = False
            self.level_up_menu.reset()
            self.state = "level_up_menu"

    def draw_game_active(self, screen):
        offset_x, offset_y = self.xy_offset()
        screen.blit(self.background_image, (-offset_x, -offset_y))
        self.draw(screen, offset_x, offset_y, self.elapsed_time)

    def update_credit_screen(self):
        pass 

    def draw_credit_screen(self, screen):
        self.run_credits(screen, self.elapsed_time)

    def update_highscore_screen(self):
        pass 

    def draw_highscore_screen(self, screen):
        self.run_new_hiscore(screen)
        input_box = pygame.Rect(self.width // 2 - 100, self.height // 2 - 20, 200, 40)
        color_active = pygame.Color('dodgerblue2')
        pygame.draw.rect(screen, color_active, input_box, 2)
        txt_surface = self.font.render(self.player_name, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

    def update_level_up_menu(self):
        pass 

    def draw_level_up_menu(self, screen):
        self.level_up_menu.draw(screen)

    def start_game(self):
        self.state = "game_active"
        self.start_time = pygame.time.get_ticks()

    def end_game(self):
        self.state = "credit_screen"
        if self.check_if_highscore(self.elapsed_time):
            self.state = "new_highscore"

    def restart_game(self):
        self.reset()
        self.state = "game_active"
        self.start_time = pygame.time.get_ticks()

    def quit_game(self):
        self.state = "exit"

    def save_and_show_credits(self):
        self.save_highscore(self.player_name, self.elapsed_time)
        self.state = "credit_screen"
        self.player_name = ""

    def exit_level_up(self):
        self.state = "game_active"

    def run(self, FPS):
        self.state = "start_screen"
        self.elapsed_time = 0
        self.player_name = ""

#        pygame.init()
#        screen = pygame.display.set_mode((self.width, self.height))
#        pygame.display.set_caption("Square Survivor (Beta 0.1)")
        clock = pygame.time.Clock()
        running = True

        game_state_methods = {
            "start_screen": (self.update_start_screen, self.draw_start_screen),
            "game_active": (self.update_game_active, self.draw_game_active),
            "credit_screen": (self.update_credit_screen, self.draw_credit_screen),
            "new_highscore": (self.update_highscore_screen, self.draw_highscore_screen),
            "level_up_menu": (self.update_level_up_menu, self.draw_level_up_menu),
        }

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_keydown(event)

            update_method, draw_method = game_state_methods[self.state]
            update_method()
            draw_method(self.screen)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()