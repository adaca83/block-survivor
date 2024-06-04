import cProfile
import pstats
import pygame
from utilities import Game

# Define constants
GAME_WIDTH = 800
GAME_HEIGHT = 800
FPS = 60

profiler = cProfile.Profile()
profiler.enable()
# Initialize pygame
pygame.init()

# Create wthe game instance
game = Game(GAME_WIDTH, GAME_HEIGHT)

# Run the game
game.run(FPS)

pygame.quit()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats()
