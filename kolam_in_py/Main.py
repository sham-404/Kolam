from TileData import *
from typing import List, Optional, cast
from utils import *
import os, sys, random, pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TILE_SET = [KolamTiles1, KolamTiles0, Circuit]
tile_data = KolamTiles1  # Add your needed tile set

TILE_PATH = tile_data.path
IMAGE_COUNT = tile_data.img_count
DIM = 10
WIDTH = 500
HEIGHT = 500
width = WIDTH
height = HEIGHT
FPS = 60


class WFCGenerator:
    def __init__(self, screen, tile_images):
        self.screen = screen
        self.tile_images = tile_images
        self.tiles: List[Tile] = []
        self.grid: List[Cell] = []
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
        edge_socket = tile_data.edge_constraint

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

        for j in range(DIM):
            for i in range(DIM):
                is_on_edge = i == 0 or i == DIM - 1 or j == 0 or j == DIM - 1
                if not is_on_edge:
                    continue

                idx = i + j * DIM
                cell_options = set(self.grid[idx].options)

                if j == 0:
                    cell_options.intersection_update(valid_up_indices)
                if j == DIM - 1:
                    cell_options.intersection_update(valid_down_indices)
                if i == 0:
                    cell_options.intersection_update(valid_left_indices)
                if i == DIM - 1:
                    cell_options.intersection_update(valid_right_indices)

                self.grid[idx].options = list(cell_options)

    def start_over(self):
        self.grid = []
        for _ in range(DIM * DIM):
            self.grid.append(Cell(len(self.tiles)))

        if tile_data.edge_constraint is not None:
            self.edge_filling()

    def setup_tiles(self):
        base_edges = tile_data.base_edges  # Socket rules

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
        next_grid: List[Optional[Cell]] = [None] * (DIM * DIM)
        for j in range(DIM):
            for i in range(DIM):
                idx = i + j * DIM
                if self.grid[idx].collapsed:
                    next_grid[idx] = self.grid[idx]

                else:
                    # start with all options
                    options = list(self.grid[idx].options)

                    # up neighbor
                    if j > 0:
                        up = self.grid[i + (j - 1) * DIM]
                        valid_options = []
                        for opt in up.options:
                            valid_options.extend(self.tiles[opt].down)
                        self.check_valid(options, valid_options)

                    # right neighbor
                    if i < DIM - 1:
                        right = self.grid[i + 1 + j * DIM]
                        valid_options = []
                        for opt in right.options:
                            valid_options.extend(self.tiles[opt].left)
                        self.check_valid(options, valid_options)

                    # down neighbor
                    if j < DIM - 1:
                        down = self.grid[i + (j + 1) * DIM]
                        valid_options = []
                        for opt in down.options:
                            valid_options.extend(self.tiles[opt].up)
                        self.check_valid(options, valid_options)

                    # left neighbor
                    if i > 0:
                        left = self.grid[i - 1 + j * DIM]
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
        w = width / DIM
        h = height / DIM
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
                    pygame.draw.rect(self.screen, Colors.MEDIUM_GRAY, rect, 1)



def load_tile_images(path, count, tile_size=64):
    images = []
    for i in range(count):
        fname = os.path.join(BASE_DIR, path, f"{i}.png")
        img = pygame.image.load(fname).convert_alpha()
        img = pygame.transform.smoothscale(img, (tile_size, tile_size))
        images.append(img)

    return images

def change_tileset(screen):
    global TILE_PATH, IMAGE_COUNT, tile_data, tile_images, kolam
    tile_data = TILE_SET[(TILE_SET.index(tile_data) + 1) % len(TILE_SET)]
    TILE_PATH = tile_data.path
    IMAGE_COUNT = tile_data.img_count
    tile_images = load_tile_images(TILE_PATH, IMAGE_COUNT, tile_size=64)
    return WFCGenerator(screen, tile_images)


def main():
    global DIM, width, height
    pygame.init()
    pygame.display.set_caption("Wave Function Collapse (pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))
    clock = pygame.time.Clock()

    # Creating Buttons

    btn_pad_x = (WIDTH - 360) // 5
    btn_pad_y = 7
    dim_inc_btn = Button(
        x=btn_pad_x,
        y=HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Increase Dim",
    )

    dim_dcr_btn = Button(
        x=dim_inc_btn.get_topright()[0] + btn_pad_x,
        y=HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Decrease Dim",
    )

    restart_btn = Button(
        x=dim_dcr_btn.get_topright()[0] + btn_pad_x,
        y=HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Restart (r)",
    )

    pause_btn = Button(
        x=restart_btn.get_topright()[0] + btn_pad_x,
        y=HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Pause (p)",
        toggle=True,
    )

    fast_toggle_btn = Button(
        x=dim_inc_btn.get_bottomleft()[0],
        y=dim_inc_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Fast Toggle",
        toggle=True,
    )

    exit_btn = Button(
        x=dim_dcr_btn.get_bottomleft()[0],
        y=dim_dcr_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Exit (Esc)",
    )

    tile_switch_btn = Button(
        x=restart_btn.get_bottomleft()[0],
        y=restart_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Change tiles",
    )

    # Start of program logic

    tile_images = load_tile_images(TILE_PATH, IMAGE_COUNT, tile_size=64)
    kolam = WFCGenerator(screen, tile_images)

    running = True
    paused = False

    # we will run step() once per N frames to slow things a bit (so you can watch it)
    # but we also allow a faster mode by pressing SPACE to run fast.
    frames_between_steps = 1
    frame_count = 0

    # font = pygame.font.SysFont("Arial", 12)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    restart_btn.trigger_key_action()
                    kolam.start_over()

                elif event.key == pygame.K_p:
                    pause_btn.trigger_key_action()
                    paused = not paused

            if dim_inc_btn.check_click(event):
                DIM += 1
                if width % DIM != 0:
                    width = height = (WIDTH // DIM) * DIM

                kolam.start_over()

            elif dim_dcr_btn.check_click(event):
                if DIM == 2:
                    continue

                DIM -= 1
                if width % DIM != 0:
                    width = height = (WIDTH // DIM) * DIM

                kolam.start_over()

            elif restart_btn.check_click(event):
                kolam.start_over()

            elif pause_btn.check_click(event):
                paused = not paused

            elif fast_toggle_btn.check_click(event):
                if frames_between_steps == 1:
                    frames_between_steps = 0
                else:
                    frames_between_steps = 1

            elif exit_btn.check_click(event):
                running = False

            elif tile_switch_btn.check_click(event):
                kolam = change_tileset(screen)
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

        screen.fill(Colors.DARK_GRAY)
        kolam.draw()

        dim_inc_btn.draw(screen)
        dim_dcr_btn.draw(screen)
        restart_btn.draw(screen)
        pause_btn.draw(screen)
        fast_toggle_btn.draw(screen)
        exit_btn.draw(screen)
        tile_switch_btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
