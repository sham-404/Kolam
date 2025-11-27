from core.tile_data import *


class gVar:
    TILE_DATA = KolamTiles1  # Add your needed tile set
    TILE_SET = [KolamTiles1, KolamTiles0, Circuit]
    TILE_PATH = TILE_DATA.path
    IMAGE_COUNT = TILE_DATA.img_count

    DIM: int = 5
    WIDTH = 550
    HEIGHT = 550
    FPS = 60


class Symmetry(gVar):
    def make_symmetry(self, on_x: bool = False, on_y: bool = False):
        if on_x:
            self.SCREEN_WIDTH = self.WIDTH // 2

        if on_y:
            self.SCREEN_HIGHT = self.HEIGHT // 2

    def remove_symmetry(self, on_x: bool = False, on_y: bool = False):
        if on_x:
            self.SCREEN_WIDTH = self.WIDTH

        if on_y:
            self.SCREEN_HIGHT = self.HEIGHT
