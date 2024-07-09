"""Functions for working with maps."""

from __future__ import annotations

from collections.abc import Iterator
from random import Random
from typing import Final

import numpy as np
import scipy.ndimage  # type: ignore[import-untyped]
import tcod.noise
from numpy.typing import NDArray
from tcod.ecs import Entity, Registry

from game.components import Graphic, MapShape, MapTiles, Position
from game.tags import IsStart
from game.tiles import TILES


def iter_random_walk(rng: Random, start: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Iterate over tiles of a random walk."""
    x, y = start
    dirs: Final = ((-1, 0), (1, 0), (0, -1), (0, 1))
    while True:
        dx, dy = rng.choice(dirs)
        x += dx
        y += dy
        yield (x, y)


class Zone:
    """Track open zones."""

    def __init__(self, labeled: NDArray[np.integer], index: int, slice_i: slice, slice_j: slice) -> None:
        """Initialize a zone."""
        self.slice_i = slice_i
        self.slice_j = slice_j
        self.mask: NDArray[np.bool_] = labeled[slice_i, slice_j] == index

    def iter_open_tiles_ij(self) -> Iterator[tuple[int, int]]:
        """Iterate over the ij coordinates of open spaces."""
        ii, jj = self.mask.nonzero()
        ii += self.slice_i.start
        jj += self.slice_j.start
        return zip(ii.tolist(), jj.tolist(), strict=True)

    def random_tile_xy(self, rng: Random) -> tuple[int, int]:
        """Return a random open coordinate from this zone."""
        return rng.choice(list(self.iter_open_tiles_ij()))[::-1]


def new_map(world: Registry) -> Entity:
    """Return a new map."""
    map_ = world[object()]
    shape = map_.components[MapShape] = (512, 512)
    center_ij = shape[0] // 2, shape[1] // 2
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

    labeled, count = scipy.ndimage.label(is_open, np.ones((3, 3), int))

    zones = [
        Zone(labeled, i, slice_i, slice_j)
        for i, (slice_i, slice_j) in enumerate(scipy.ndimage.find_objects(labeled), start=1)
    ]
    zones.sort(key=lambda z: abs(z.slice_i.start - center_ij[0]) + abs(z.slice_j.start - center_ij[1]))

    start_zone = zones.pop(0)
    start = world[object()]
    start.components[Position] = Position(*start_zone.random_tile_xy(rng), map_)
    start.tags |= {IsStart}

    for zone in zones:
        item = world[object()]
        item.components[Position] = Position(*zone.random_tile_xy(rng), map_)
        item.components[Graphic] = Graphic(ord("$"))

    return map_
