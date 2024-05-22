import pygame
from utilities import Game

# Define constants
GAME_WIDTH = 800
GAME_HEIGHT = 800
FPS = 60

# Initialize pygame
pygame.init()

# Create wthe game instance
game = Game(GAME_WIDTH, GAME_HEIGHT)

# Run the game
game.run(FPS)

pygame.quit()
