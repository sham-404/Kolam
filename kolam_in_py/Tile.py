import pygame, os


class Tile:
    def __init__(self, img, edges, index):
        self.img = img
        self.edges = list(edges)  # [up, right, down, left]
        self.up = []
        self.right = []
        self.down = []
        self.left = []
        self.index = index

    def compare_edge(self, tile1, tile2):
        return tile1 == tile2[::-1]

    def analyze(self, tiles):
        for i, tile in enumerate(tiles):
            if tile.index == 5 and self.index == 5:
                continue

            if self.compare_edge(tile.edges[2], self.edges[0]):
                self.up.append(i)

            if self.compare_edge(tile.edges[3], self.edges[1]):
                self.right.append(i)

            if self.compare_edge(tile.edges[0], self.edges[2]):
                self.down.append(i)

            if self.compare_edge(tile.edges[1], self.edges[3]):
                self.left.append(i)

    def rotate(self, num: int):
        angle = -90 * num
        new_img = pygame.transform.rotate(self.img, angle)
        len_e = len(self.edges)
        new_edges = [self.edges[(i - num) % len_e] for i in range(len_e)]
        return Tile(new_img, new_edges, self.index)


class Cell:
    def __init__(self, value):
        self.collapsed = False
        if isinstance(value, list):
            self.options = list(value)
        else:
            self.options = [i for i in range(value)]


class Circuit:
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

    img_count = 13
    path = os.path.join("tiles", "Circuit")


class KolamTiles0:
    base_edges = [
        ["00", "00", "00", "00"],  # Edge socket for each img
        ["00", "00", "01", "10"],  # runs clockwise (UP, RIGHT, DOWN, LEFT)
        ["10", "00", "01", "11"],
        ["10", "01", "11", "11"],
        ["11", "11", "11", "11"],
        ["10", "01", "10", "01"],
    ]

    img_count = 6
    path = os.path.join("tiles", "KolamTiles0")


class KolamTiles1:
    base_edges = [
        ["000", "010", "010", "000"],  # Edge socket for each img
        ["010", "010", "010", "000"],  # runs clockwise (UP, RIGHT, DOWN, LEFT)
        ["010", "010", "010", "010"],
        ["000", "010", "000", "000"],
        ["010", "000", "010", "000"],
    ]

    img_count = 5
    path = os.path.join("tiles", "KolamTiles1")
