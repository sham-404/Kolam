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
