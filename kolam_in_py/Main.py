from Tile import Tile, Cell
from typing import List, Optional, cast

import os, sys, random, pygame

TILE_PATH = os.path.join("tiles", "kolam_tiles")
IMAGE_COUNT = 6
DIM = 10
WIDTH = 600
HEIGHT = 600
FPS = 120


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
        self.tiles: List[Tile] = []
        self.grid: List[Cell] = []
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

    def update_neighbors(self):
        next_grid: List[Optional[Cell]] = [None] * (DIM * DIM)
        for j in range(DIM):
            for i in range(DIM):
                idx = i + j * DIM
                if self.grid[idx].collapsed:
                    next_grid[idx] = self.grid[idx]

                else:
                    # start with all options
                    options = [k for k in range(len(self.tiles))]

                    # up neighbor
                    if j > 0:
                        up = self.grid[i + (j - 1) * DIM]
                        valid_options = []
                        for opt in up.options:
                            valid_options.extend(self.tiles[opt].down)
                        check_valid(options, valid_options)

                    # right neighbor
                    if i < DIM - 1:
                        right = self.grid[i + 1 + j * DIM]
                        valid_options = []
                        for opt in right.options:
                            valid_options.extend(self.tiles[opt].left)
                        check_valid(options, valid_options)

                    # down neighbor
                    if j < DIM - 1:
                        down = self.grid[i + (j + 1) * DIM]
                        valid_options = []
                        for opt in down.options:
                            valid_options.extend(self.tiles[opt].up)
                        check_valid(options, valid_options)

                    # left neighbor
                    if i > 0:
                        left = self.grid[i - 1 + j * DIM]
                        valid_options = []
                        for opt in left.options:
                            valid_options.extend(self.tiles[opt].right)
                        check_valid(options, valid_options)

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
        w = WIDTH / DIM
        h = HEIGHT / DIM
        for j in range(DIM):
            for i in range(DIM):
                cell = self.grid[i + j * DIM]
                rect = pygame.Rect(i * w, j * h, w, h)
                if cell.collapsed:
                    index = cell.options[0]
                    # draw tile image scaled to cell size
                    tile_img = self.tiles[index].img
                    img_surf = pygame.transform.smoothscale(tile_img, (int(w), int(h)))
                    self.screen.blit(img_surf, rect.topleft)
                else:
                    # draw grid rectangle for undecided cell
                    pygame.draw.rect(self.screen, (70, 70, 70), rect, 1)


def main():
    pygame.init()
    pygame.display.set_caption("Wave Function Collapse (pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    tile_images = load_tile_images(TILE_PATH, IMAGE_COUNT, tile_size=64)

    kolam = KolamGenerator(screen, tile_images)

    running = True
    paused = False

    # we will run step() once per N frames to slow things a bit (so you can watch it)
    # but we also allow a faster mode by pressing SPACE to run fast.
    frames_between_steps = 1
    frame_count = 0

    font = pygame.font.SysFont("Arial", 16)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

                elif event.key == pygame.K_r:
                    kolam.start_over()

                elif event.key == pygame.K_SPACE:
                    # toggle fast mode
                    if frames_between_steps == 1:
                        frames_between_steps = 0
                    else:
                        frames_between_steps = 1

                elif event.key == pygame.K_p:
                    paused = not paused

            elif event.type == pygame.MOUSEBUTTONDOWN:
                kolam.start_over()

        if not paused:
            if frames_between_steps == 0:
                # very fast (collapse many times per frame)
                for _ in range(200):
                    kolam.step()
            else:
                if frame_count % frames_between_steps == 0:
                    kolam.step()
            frame_count += 1

        screen.fill((30, 30, 30))
        kolam.draw()

        screen.blit(
            font.render(
                "R: restart  SPACE: fast toggle  P: pause  Click: restart",
                True,
                (0, 0, 0),
            ),
            (8, HEIGHT - 24),
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
