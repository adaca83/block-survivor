class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.matrix = [[0 for _ in range(width)] for _ in range(height)]
    
    def is_within_bounds(self, node):
        x, y = node
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_walkable(self, node):
        x, y = node
        return self.matrix[y][x] == 0