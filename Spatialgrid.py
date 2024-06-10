class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = {}

    def _get_cell_coords(self, x, y):
        return x // self.cell_size, y // self.cell_size

    def add(self, item, x, y):
        cell_coords = self._get_cell_coords(x, y)
        if cell_coords not in self.grid:
            self.grid[cell_coords] = []
        self.grid[cell_coords].append(item)

    def contains(self, item, x, y):
        cell_coords = self._get_cell_coords(x, y)
        return cell_coords in self.grid and item in self.grid[cell_coords]

    def remove(self, item, x, y):
        cell_coords = self._get_cell_coords(x, y)
        if cell_coords in self.grid and item in self.grid[cell_coords]:
            self.grid[cell_coords].remove(item)

    def get_nearby(self, x, y):
        cell_coords = self._get_cell_coords(x, y)
        nearby_items = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nearby_cell = (cell_coords[0] + dx, cell_coords[1] + dy)
                if nearby_cell in self.grid:
                    nearby_items.extend(self.grid[nearby_cell])
        return nearby_items