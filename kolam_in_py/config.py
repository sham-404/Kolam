from core.tile_data import *


class gVar:
    TILE_DATA = KolamTiles1  # Add your needed tile set
    TILE_SET = [KolamTiles1, KolamTiles0, Circuit]
    TILE_PATH = TILE_DATA.path
    IMAGE_COUNT = TILE_DATA.img_count

    DIM: int = 8
    WIDTH = 560
    HEIGHT = 560
    FPS = 60
