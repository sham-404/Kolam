from core.tile_data import *

class gVar:
    TILE_DATA = KolamTiles1  # Add your needed tile set
    TILE_SET = [KolamTiles1, KolamTiles0, Circuit]
    TILE_PATH = TILE_DATA.path
    IMAGE_COUNT = TILE_DATA.img_count
    DIM:int = 10
    WIDTH = 550
    HEIGHT = 550
    FPS = 60
    width = WIDTH
    height = HEIGHT
