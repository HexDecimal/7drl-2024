"""Functions for working with maps."""
from __future__ import annotations

from collections.abc import Iterator
from random import Random

import numpy as np
import tcod.noise
from tcod.ecs import Entity, Registry

from game.components import MapShape, MapTiles, Position
from game.tags import IsStart
from game.tiles import TILE_DB, TILES


def iter_random_walk(rng: Random, start: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Iterate over tiles of a random walk."""
    x, y = start
    DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))
    while True:
        dx, dy = rng.choice(DIRS)
        x += dx
        y += dy
        yield (x, y)


def new_map(world: Registry) -> Entity:
    """Return a new map."""
    map_ = world[object()]
    shape = map_.components[MapShape] = (1024, 1024)
    tiles = map_.components[MapTiles] = np.zeros(shape=shape, dtype=np.uint8)

    rng = world[None].components[Random]
    n_open = tcod.noise.Noise(2, seed=rng.getrandbits(32))
    n_hardness = tcod.noise.Noise(2, seed=rng.getrandbits(32))

    hardness = n_hardness[tcod.noise.grid(shape, 1 / 12)]
    openness = n_open[tcod.noise.grid(shape, 1 / 6)]

    is_rock = hardness > 0
    is_open = openness > 0.25  # noqa: PLR2004

    tiles[:] = TILES["loam wall"]
    tiles[is_rock] = TILES["rock wall"]
    tiles[is_open] += 1

    tiles[[0, -1], :] = 0
    tiles[:, [0, -1]] = 0

    start = world[object()]
    open_area = TILE_DB["move_cost"][tiles] != 0
    for ij in iter_random_walk(rng, (shape[0] // 2, shape[1] // 2)):
        if open_area[ij]:
            start.components[Position] = Position(ij[1], ij[0], map_)
            break
    start.tags |= {IsStart}

    return map_
