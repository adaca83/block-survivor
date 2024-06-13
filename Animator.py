import pygame
import time
from Enemy import *

class Animator:

    dying_enemies = []
    
    def __init__(self) -> None:
        self.death_images = [pygame.image.load(f"assets/images/death_animation/death0{i}.png") for i in range(1, 7)]
        self.death_animation_speed = 40  # Milliseconds between frames

        # ADD MORE IMAGES WITH CORRESPONDING SPEEDS HERE FOR NEW ANIMATIONS

    def death_animation(self, enemy, offset_x, offset_y):
        death_anim = {
            'images': self.death_images,
            'animation_index': 0,
            'animation_speed': self.death_animation_speed,
            'last_update': time.time(),
            'position': ((enemy.x-20)-offset_x, (enemy.y-20)-offset_y) # x & y marks the corner of the enemy
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
    def draw_death_animations(cls,  screen):
        
        for death_anim in cls.dying_enemies:
            image = death_anim['images'][death_anim['animation_index']]
            screen.blit(image, death_anim['position'])