import random
from Enemy import * 

class Horde:
    HORDE_MIN_SIZE = 16
    HORDE_MAX_SIZE = 16
    HORDE_SPACING = 30

    def __init__(self, game, player=None, offset_x=None, offset_y=None):
        self.game = game
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.enemies = []
        self.spawn_time = self.generate_next_spawn_time()
        self.pattern = self.choose_pattern()
        self.spawned = False
        self.player = player
        

    def generate_next_spawn_time(self):
        return random.randint(50, 100) # 50, 100

    def choose_pattern(self):
        return random.choice([
            "single_row",
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
            enemy = Enemy(self.game, self.game.width, self.game.height, level=1, is_horde_enemy=True, player=self.player)
            enemy.x, enemy.y = pos
            enemy.set_attributes_based_on_level()
            self.enemies.append(enemy)
            self.game.enemies.append(enemy)
            self.game.spatial_grid.add(enemy, enemy.x + self.offset_y, enemy.y + self.offset_y)

        self.spawned = True

    def get_horde_positions_outside_of_view(self, pattern, num_enemies):
        positions = []

        if pattern == "single_row":
            positions = self.generate_single_row(num_enemies)
        elif pattern == "two_rows":
            positions = self.generate_two_rows(num_enemies)
        elif pattern == "four_rows":
            positions = self.generate_four_rows(num_enemies)
        elif pattern == "eight_rows":
            positions = self.generate_eight_rows(num_enemies)
        elif pattern == "sixteen_rows":
            positions = self.generate_sixteen_rows(num_enemies)

        return positions

    def generate_single_row(self, num_enemies):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            start_x = random.randint(0, self.game.width - num_enemies * self.HORDE_SPACING) + self.offset_x
            y = -self.HORDE_SPACING + self.offset_y  # Just above the screen
            return [(start_x + i * self.HORDE_SPACING, y) for i in range(num_enemies)]
        elif edge == 'bottom':
            start_x = random.randint(0, self.game.width - num_enemies * self.HORDE_SPACING) + self.offset_x
            y = self.game.height + self.offset_y  # Just below the screen
            return [(start_x + i * self.HORDE_SPACING, y) for i in range(num_enemies)]
        elif edge == 'left':
            start_y = random.randint(0, self.game.height - num_enemies * self.HORDE_SPACING) + self.offset_y
            x = -self.HORDE_SPACING + self.offset_x  # Just to the left of the screen
            return [(x, start_y + i * self.HORDE_SPACING) for i in range(num_enemies)]
        elif edge == 'right':
            start_y = random.randint(0, self.game.height - num_enemies * self.HORDE_SPACING) + self.offset_y
            x = self.game.width + self.offset_x  # Just to the right of the screen
            return [(x, start_y + i * self.HORDE_SPACING) for i in range(num_enemies)]

    def generate_two_rows(self, num_enemies):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            start_x = random.randint(0, self.game.width - (num_enemies // 2) * self.HORDE_SPACING) + self.offset_x
            y1, y2 = (-self.HORDE_SPACING, -2 * self.HORDE_SPACING) if edge == 'top' else (self.game.height, self.game.height + self.HORDE_SPACING)
            y1 += self.offset_y
            y2 += self.offset_y
            row1 = [(start_x + i * self.HORDE_SPACING, y1) for i in range(num_enemies // 2)]
            row2 = [(start_x + i * self.HORDE_SPACING, y2) for i in range(num_enemies // 2, num_enemies)]
            return row1 + row2
        elif edge in ['left', 'right']:
            start_y = random.randint(0, self.game.height - (num_enemies // 2) * self.HORDE_SPACING) + self.offset_y
            x1, x2 = (-self.HORDE_SPACING, -2 * self.HORDE_SPACING) if edge == 'left' else (self.game.width, self.game.width + self.HORDE_SPACING)
            x1 += self.offset_x
            x2 += self.offset_x
            row1 = [(x1, start_y + i * self.HORDE_SPACING) for i in range(num_enemies // 2)]
            row2 = [(x2, start_y + i * self.HORDE_SPACING) for i in range(num_enemies // 2, num_enemies)]
            return row1 + row2

    def generate_four_rows(self, num_enemies):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            start_x = random.randint(0, self.game.width - (num_enemies // 4) * self.HORDE_SPACING) + self.offset_x
            y_positions = [-i * self.HORDE_SPACING for i in range(1, 5)] if edge == 'top' else [self.game.height + i * self.HORDE_SPACING for i in range(4)]
            positions = []
            for i in range(num_enemies):
                row = y_positions[i % 4]
                positions.append((start_x + (i // 4) * self.HORDE_SPACING, row + self.offset_y))
            return positions
        elif edge in ['left', 'right']:
            start_y = random.randint(0, self.game.height - (num_enemies // 4) * self.HORDE_SPACING) + self.offset_y
            x_positions = [-i * self.HORDE_SPACING for i in range(1, 5)] if edge == 'left' else [self.game.width + i * self.HORDE_SPACING for i in range(4)]
            positions = []
            for i in range(num_enemies):
                col = x_positions[i % 4]
                positions.append((col + self.offset_x, start_y + (i // 4) * self.HORDE_SPACING))
            return positions

    def generate_eight_rows(self, num_enemies):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            start_x = random.randint(0, self.game.width - (num_enemies // 8) * self.HORDE_SPACING) + self.offset_x
            y_positions = [-i * self.HORDE_SPACING for i in range(1, 9)] if edge == 'top' else [self.game.height + i * self.HORDE_SPACING for i in range(8)]
            positions = []
            for i in range(num_enemies):
                row = y_positions[i % 8]
                positions.append((start_x + (i // 8) * self.HORDE_SPACING, row + self.offset_y))
            return positions
        elif edge in ['left', 'right']:
            start_y = random.randint(0, self.game.height - (num_enemies // 8) * self.HORDE_SPACING) + self.offset_y
            x_positions = [-i * self.HORDE_SPACING for i in range(1, 9)] if edge == 'left' else [self.game.width + i * self.HORDE_SPACING for i in range(8)]
            positions = []
            for i in range(num_enemies):
                col = x_positions[i % 8]
                positions.append((col + self.offset_x, start_y + (i // 8) * self.HORDE_SPACING))
            return positions

    def generate_sixteen_rows(self, num_enemies):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            start_x = random.randint(0, self.game.width - (num_enemies // 16) * self.HORDE_SPACING) + self.offset_x
            y_positions = [-i * self.HORDE_SPACING for i in range(1, 17)] if edge == 'top' else [self.game.height + i * self.HORDE_SPACING for i in range(16)]
            positions = []
            for i in range(num_enemies):
                row = y_positions[i % 16]
                positions.append((start_x + (i // 16) * self.HORDE_SPACING, row + self.offset_y))
            return positions
        elif edge in ['left', 'right']:
            start_y = random.randint(0, self.game.height - (num_enemies // 16) * self.HORDE_SPACING) + self.offset_y
            x_positions = [-i * self.HORDE_SPACING for i in range(1, 17)] if edge == 'left' else [self.game.width + i * self.HORDE_SPACING for i in range(16)]
            positions = []
            for i in range(num_enemies):
                col = x_positions[i % 16]
                positions.append((col + self.offset_x, start_y + (i // 16) * self.HORDE_SPACING))
            return positions

    def update(self, elapsed_time):
        if not self.spawned and elapsed_time >= self.spawn_time:
            self.spawn()