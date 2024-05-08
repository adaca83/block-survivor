import pygame
from utilities import Game, GameMenu

# Define constants
GAME_WIDTH = 800
GAME_HEIGHT = 800
FPS = 60

# Initialize pygame
pygame.init()

# Create the game menu and game instances
game_menu = GameMenu(GAME_WIDTH, GAME_HEIGHT)
game = Game(GAME_WIDTH, GAME_HEIGHT)

# Set the initial game state to the menu
current_state = "menu"

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if current_state == "menu":
        # Run the menu and get the selected option
        selected_option = game_menu.run_menu()
        if selected_option == "Start Game":
            # Change the game state to gameplay
            current_state = "gameplay"
            # Reset the game
            game.reset()
        elif selected_option == "Quit":
            running = False
    elif current_state == "gameplay":
        # Run the game
        game.run(FPS)
        # After the game ends, return to menu
        current_state = "menu"

pygame.quit()
