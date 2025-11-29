import random
from config import gVar
from .tile_data import *
from typing import List, Optional, cast
from utils.colors import Colors


class WFCGenerator:
    def __init__(self, screen, tile_images):
        self.screen = screen
        self.tile_images = tile_images
        self.tiles: List[Tile] = []
        self.grid: List[Cell] = []
        self.width = gVar.WIDTH  # Rezised width size of the whole screen
        self.height = gVar.HEIGHT
        self.screen_width = self.width  # Width of the actual drawing screen
        self.screen_height = self.height
        self.x_symmetry = False
        self.y_symmetry = False
        self.dim_x = gVar.DIM
        self.dim_y = gVar.DIM
        self.setup_tiles()
        self.start_over()

    def remove_duplicated_tiles(self, tiles):
        unique = {}
        for tile in tiles:
            key = ",".join(tile.edges)
            if key not in unique:
                unique[key] = tile

        return list(unique.values())

    def check_valid(self, options, valid):
        valid_set = set(valid)
        for i in range(len(options) - 1, -1, -1):
            if options[i] not in valid_set:
                options.pop(i)

    def edge_filling(self):
        edge_socket = gVar.TILE_DATA.edge_constraint

        valid_up_indices = {
            i for i, tile in enumerate(self.tiles) if tile.edges[0] == edge_socket
        }
        valid_right_indices = {
            i for i, tile in enumerate(self.tiles) if tile.edges[1] == edge_socket
        }
        valid_down_indices = {
            i for i, tile in enumerate(self.tiles) if tile.edges[2] == edge_socket
        }
        valid_left_indices = {
            i for i, tile in enumerate(self.tiles) if tile.edges[3] == edge_socket
        }

        for j in range(self.dim_y):
            for i in range(self.dim_x):
                is_on_edge = (
                    i == 0 or i == self.dim_x - 1 or j == 0 or j == self.dim_y - 1
                )
                if not is_on_edge:
                    continue

                idx = i + j * self.dim_x
                cell_options = set(self.grid[idx].options)

                if j == 0:
                    cell_options.intersection_update(valid_up_indices)
                if j == self.dim_y - 1 and not self.y_symmetry:
                    cell_options.intersection_update(valid_down_indices)
                if i == 0:
                    cell_options.intersection_update(valid_left_indices)
                if i == self.dim_x - 1 and not self.x_symmetry:
                    cell_options.intersection_update(valid_right_indices)

                self.grid[idx].options = list(cell_options)

    def start_over(self):
        self.grid = []
        for _ in range(self.dim_x * self.dim_y):
            self.grid.append(Cell(len(self.tiles)))

        if gVar.TILE_DATA.edge_constraint is not None:
            self.edge_filling()

    def setup_tiles(self):
        base_edges = gVar.TILE_DATA.base_edges  # Socket rules

        imgs = self.tile_images

        base_tiles = []
        for i, edges in enumerate(base_edges):
            img = imgs[i % len(imgs)]  # '%' used so that index never runs out of bound
            base_tiles.append(Tile(img, edges, index=i))

        # Generate rotations for each base tile
        tiles = []
        for i, t in enumerate(base_tiles):
            temp = []
            for rot in range(4):
                temp.append(t.rotate(rot))
            temp = self.remove_duplicated_tiles(temp)

            for tt in temp:
                tt.index = i  # base index
            tiles.extend(temp)

        tiles = self.remove_duplicated_tiles(tiles)

        for i, tile in enumerate(tiles):
            tile.index = i

        # Analyze adjacency rules
        for tile in tiles:
            tile.analyze(tiles)

        self.tiles = tiles
        print(f"Tiles after rotation/dedupe: {len(self.tiles)}")

    def collapse_one(self):  # pick a non-collapsed cell with lowest entropy
        non_collapsed = [c for c in self.grid if not c.collapsed]
        if not non_collapsed:
            return

        non_collapsed.sort(key=lambda c: len(c.options))
        min_len = len(non_collapsed[0].options)
        tie_group = [c for c in non_collapsed if len(c.options) == min_len]
        chosen = random.choice(tie_group)
        chosen.collapsed = True

        if not chosen.options:  # contradiction -> restart
            self.start_over()
            return

        pick = random.choice(chosen.options)
        chosen.options = [pick]

    def update_neighbors(self):
        next_grid: List[Optional[Cell]] = [None] * (self.dim_x * self.dim_y)
        for j in range(self.dim_y):
            for i in range(self.dim_x):
                idx = i + j * self.dim_x
                if self.grid[idx].collapsed:
                    next_grid[idx] = self.grid[idx]

                else:
                    # start with all options
                    options = list(self.grid[idx].options)

                    # up neighbor
                    if j > 0:
                        up = self.grid[i + (j - 1) * self.dim_x]
                        valid_options = []
                        for opt in up.options:
                            valid_options.extend(self.tiles[opt].down)
                        self.check_valid(options, valid_options)

                    # right neighbor
                    if i < self.dim_x - 1:
                        right = self.grid[i + 1 + j * self.dim_x]
                        valid_options = []
                        for opt in right.options:
                            valid_options.extend(self.tiles[opt].left)
                        self.check_valid(options, valid_options)

                    # down neighbor
                    if j < self.dim_y - 1:
                        down = self.grid[i + (j + 1) * self.dim_x]
                        valid_options = []
                        for opt in down.options:
                            valid_options.extend(self.tiles[opt].up)
                        self.check_valid(options, valid_options)

                    # left neighbor
                    if i > 0:
                        left = self.grid[i - 1 + j * self.dim_x]
                        valid_options = []
                        for opt in left.options:
                            valid_options.extend(self.tiles[opt].right)
                        self.check_valid(options, valid_options)

                    # if no options, contradiction -> restart whole grid
                    if len(options) == 0:
                        print("[WFC] contradiction found - restarting")
                        self.start_over()
                        return

                    next_grid[idx] = Cell(options)

        self.grid = cast(List[Cell], next_grid)

    def step(self):
        if all(c.collapsed for c in self.grid):
            return

        self.collapse_one()
        self.update_neighbors()

    def draw(self):
        w = self.screen_width // self.dim_x
        h = self.screen_height // self.dim_y
        for j in range(self.dim_y):
            for i in range(self.dim_x):
                cell = self.grid[i + j * self.dim_x]
                rect = pygame.Rect(i * w, j * h, w, h)
                if cell.collapsed:
                    index = cell.options[0]
                    # draw tile image scaled to cell size
                    tile_img = self.tiles[index].img
                    img_surf = pygame.transform.smoothscale(tile_img, (int(w), int(h)))
                    self.screen.blit(img_surf, rect.topleft)
                else:
                    # draw grid rectangle for undecided cell
                    pygame.draw.rect(self.screen, Colors.MEDIUM_GRAY, rect, 1)

    def make_symmetry(self):
        if self.x_symmetry:
            self.screen_width = gVar.WIDTH // 2
            self.dim_x = gVar.DIM // 2

        else:
            self.screen_width = gVar.WIDTH
            self.dim_x = gVar.DIM

        if self.y_symmetry:
            self.screen_height = gVar.HEIGHT // 2
            self.dim_y = gVar.DIM // 2

        else:
            self.screen_height = gVar.HEIGHT
            self.dim_y = gVar.DIM

    def adjust_screen_size(self):
        if self.x_symmetry:
            self.width = (gVar.WIDTH // (self.dim_x * 2)) * (self.dim_x * 2)
            self.screen_width = self.width // 2
        else:
            self.width = (gVar.WIDTH // self.dim_x) * self.dim_x
            self.screen_width = self.width

        if self.y_symmetry:
            self.height = (gVar.HEIGHT // (self.dim_y * 2)) * (self.dim_y * 2)
            self.screen_height = self.height // 2
        else:
            self.height = (gVar.HEIGHT // self.dim_y) * self.dim_y
            self.screen_height = self.height
