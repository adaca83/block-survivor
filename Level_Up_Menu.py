import pygame
import random
import os

class level_up_menu:
    def __init__(self, width, height, font, player):
        self.width = width
        self.height = height
        self.font = font
        self.player = player
        self.selected_option = None
        self.all_options = {
            "Mvt Speed": (self.increase_speed, "option_5.png"),
            "HP": (self.increase_hp, "option_2.png"),
            "Atk Speed": (self.increase_attack_speed, "option_3.png"),
            "Field of View": (self.increase_FOV, "option_6.png"),
            "Pick up Area": (self.increase_pickup_radius, "option_1.png"),
            "Player Size": (self.decrease_player_size, "option_4.png"),
        }
        self.option_rects = []
        self.option_images = self.load_option_images()
        self.options = self.get_random_options()

    def load_option_images(self):
        base_path = r"assets\images\level_up_options"
        return {name: pygame.image.load(os.path.join(base_path, filename)) for name, (_, filename) in self.all_options.items()}

    def get_random_options(self):
        return dict(random.sample(list(self.all_options.items()), 4))

    def draw(self, screen):
        screen.fill((0, 0, 0))  # Ensure the background is black
        y_offset = self.height // 2 - 100  # Center the options vertically
        self.option_rects = []
        option_width = 150
        option_height = 150
        spacing = 40
        total_width = (option_width + spacing) * 4 - spacing
        x_start = (self.width - total_width) // 2  # Center the options horizontally

        for i, (option, (func, _)) in enumerate(self.options.items()):
            rect_x = x_start + i * (option_width + spacing)
            rect_y = y_offset
            rect = pygame.Rect(rect_x, rect_y, option_width, option_height)
            self.option_rects.append(rect)

            # Draw the option image
            option_image = self.option_images[option]
            option_image = pygame.transform.scale(option_image, (option_width, option_height))
            screen.blit(option_image, rect)

            # Draw the option text
            option_text = self.font.render(option, True, (255, 255, 255))
            text_rect = option_text.get_rect(center=(rect.centerx, rect.bottom + 20))
            screen.blit(option_text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = list(self.options.keys())[i]
                    self.apply_choice()
                    self.player.game.exit_level_up()  # Transition back to game state
                    break  # Exit the loop once an option is selected

    def apply_choice(self):
        if self.selected_option:
            self.options[self.selected_option][0]()  # Call the corresponding function
            self.selected_option = None  # Reset the selected option

    def get_selected_option(self):
        return self.selected_option

    def reset(self):
        self.selected_option = None
        self.options = self.get_random_options()  # Reset options when resetting menu

    def increase_speed(self):
        self.player.speed += 1

    def increase_hp(self):
        self.player.hp += 3

    def increase_attack_speed(self):
        self.player.shot_interval = max(500, self.player.shot_interval - 250)

    def increase_FOV(self):
        self.player.FOV += 100

    def increase_pickup_radius(self):
        self.player.pickup_radius += 100
    
    def decrease_player_size(self):
        self.player.width -= 2
        self.player.height -= 2
