from Tile import Tile, Cell

import os, sys, random, pygame

TILE_PATH = os.path.join("tiles", "circuit")
IMAGE_COUNT = 13
DIM = 25
WIDTH = 600
HEIGHT = 600
FPS = 60


def load_tile_images(path, count, tile_size=64):
    images = []
    for i in range(count):
        fname = os.path.join(path, f"{i}.png")
        img = pygame.image.load(fname).convert_alpha()
        img = pygame.transform.smoothscale(img, (tile_size, tile_size))
        images.append(img)

    return images


def remove_duplicated_tiles(tiles):
    unique = {}
    for tile in tiles:
        key = ",".join(tile.edges)
        if key not in unique:
            unique[key] = tile

    return list(unique.values())


def check_valid(options, valid):
    valid_set = set(valid)
    for i in range(len(options) - 1, -1, -1):
        if options[i] not in valid_set:
            options.pop(i)


class KolamGenerator:
    def __init__(self, screen, tile_images):
        self.screen = screen
        self.tile_images = tile_images
        self.tiles = []
        self.grid = []
        self.setup_tiles()
        self.start_over()

    def start_over(self):
        self.grid = []
        for _ in range(DIM * DIM):
            self.grid.append(Cell(len(self.tiles)))

    def setup_tiles(self):
        base_edges = [
            ["AAA", "AAA", "AAA", "AAA"],  # Edge socket for each img
            ["BBB", "BBB", "BBB", "BBB"],  # runs clockwise (UP, RIGHT, DOWN, LEFT)
            ["BBB", "BCB", "BBB", "BBB"],
            ["BBB", "BDB", "BBB", "BDB"],
            ["ABB", "BCB", "BBA", "AAA"],
            ["ABB", "BBB", "BBB", "BBA"],
            ["BBB", "BCB", "BBB", "BCB"],
            ["BDB", "BCB", "BDB", "BCB"],
            ["BDB", "BBB", "BCB", "BBB"],
            ["BCB", "BCB", "BBB", "BCB"],
            ["BCB", "BCB", "BCB", "BCB"],
            ["BCB", "BCB", "BBB", "BBB"],
            ["BBB", "BCB", "BBB", "BCB"],
        ]

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
            temp = remove_duplicated_tiles(temp)

            for tt in temp:
                tt.index = i  # base index
            tiles.extend(temp)

        tiles = remove_duplicated_tiles(tiles)

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
