
import pygame
import random

class NPC:
    npc_sprites = {
        "green_vendor": "assets/images/characters/vendor01.png"
    }

    def __init__(self, sprite: str, game, game_width, game_height):
        self.game = game
        # Load the image file using pygame.image.load()
        self.img = pygame.image.load(self.npc_sprites[sprite])
        # Generate random coordinates within the game's dimensions with padding
        self.x = random.randint(20, game_width - 20 - self.img.get_width())
        self.y = random.randint(20, game_height - 20 - self.img.get_height())

    def draw(self, screen, offset_x, offset_y):
        # Get the rect for positioning the image
        npc_rect = self.img.get_rect()
        npc_rect.topleft = (self.x - offset_x, self.y - offset_y)
        # Draw the image on the screen at the specified location
        screen.blit(self.img, npc_rect)