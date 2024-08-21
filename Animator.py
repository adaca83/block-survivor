import pygame
import time
from Enemy import *

class Animator:
    dying_enemies = []
    running_players = {}

    def __init__(self) -> None:
        self.death_images = [pygame.image.load(f"assets/images/death_animation/death0{i}.png") for i in range(1, 7)]
        self.death_animation_speed = 40  # Milliseconds between frames

        self.run_images_right = [pygame.image.load(f"assets/images/run_animation/RG_run_right{i}.png") for i in range(1, 9)]
        self.run_images_left = [pygame.image.load(f"assets/images/run_animation/RG_run_left{i}.png") for i in range(1, 9)]
        self.run_animation_speed = 80  # Milliseconds between frames

        # ADD MORE IMAGES WITH CORRESPONDING SPEEDS HERE FOR NEW ANIMATIONS

    def start_run_animation(self, player, direction):
        # Determine the correct set of images based on the direction
        run_images = self.run_images_left if direction == 1 else self.run_images_right

        # Only start a new animation if it's not already running or if the direction has changed
        if player not in self.running_players or self.running_players[player]['direction'] != direction:
            self.running_players[player] = {
                'images': run_images,
                'animation_index': 0,
                'animation_speed': self.run_animation_speed,
                'last_update': time.time(),
                'position': (player.x, player.y),
                'direction': direction
            }

    def update_run_animation(self, player):
        if player in self.running_players:
            run_anim = self.running_players[player]
            current_time = time.time()

            if current_time - run_anim['last_update'] > run_anim['animation_speed'] / 1000:
                run_anim['animation_index'] = (run_anim['animation_index'] + 1) % len(run_anim['images'])
                run_anim['last_update'] = current_time

    def draw_run_animation(self, screen, player, offset_x=0, offset_y=0):
        if player in self.running_players:
            run_anim = self.running_players[player]
            image = run_anim['images'][run_anim['animation_index']]
            # Adjust position based on the current offset
            screen_pos = (player.x - offset_x, player.y - offset_y)
            screen.blit(image, screen_pos)

    def stop_run_animation(self, player):
        if player in self.running_players:
            del self.running_players[player]

    def death_animation(self, enemy):
        death_anim = {
            'images': self.death_images,
            'animation_index': 0,
            'animation_speed': self.death_animation_speed,
            'last_update': time.time(),
            'position': (enemy.x-20, enemy.y-20)  # x & y marks the corner of the enemy
        }
        self.dying_enemies.append(death_anim)

    @classmethod
    def update_death_animation(cls):
        current_time = time.time()
        for death_anim in cls.dying_enemies[:]:
            if current_time - death_anim['last_update'] > death_anim['animation_speed'] / 1000:
                death_anim['animation_index'] += 1
                death_anim['last_update'] = current_time
                if death_anim['animation_index'] >= len(death_anim['images']):
                    cls.dying_enemies.remove(death_anim)

    @classmethod
    def draw_death_animations(cls, screen, offset_x, offset_y):
        for death_anim in cls.dying_enemies:
            image = death_anim['images'][death_anim['animation_index']]
            # Adjust position based on the current offset
            screen_pos = (death_anim['position'][0] - offset_x, death_anim['position'][1] - offset_y)
            screen.blit(image, screen_pos)