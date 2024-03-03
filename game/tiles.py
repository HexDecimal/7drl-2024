"""Functions for working with maps."""
from __future__ import annotations

from typing import NamedTuple

import numpy as np
import tcod.console

TILE_DTYPE = np.dtype(
    [
        ("name", object),
        ("graphic", tcod.console.rgb_graphic),
        ("move_cost", np.int16),
        ("dig_cost", np.int16),
        ("transparent", bool),
    ]
)


class _Tile(NamedTuple):
    name: str
    graphic: tuple[int, tuple[int, int, int], tuple[int, int, int]]
    move_cost: int = 0
    dig_cost: int = 0
    transparent: bool = False


TILE_DB = np.array(
    [
        _Tile(
            name="solid wall",
            graphic=(ord("#"), (255, 255, 255), (0, 0, 0)),
        ),
        _Tile(
            name="floor",
            graphic=(ord("."), (64, 64, 64), (0, 0, 0)),
            move_cost=100,
            transparent=True,
        ),
        _Tile(  # https://paletton.com/#uid=7000I0kllllaFw0g0qFqFg0w0aF
            name="loam wall",
            graphic=(ord("-"), (128, 82, 21), (209, 166, 108)),
            dig_cost=100,
        ),
        _Tile(
            name="loam floor",
            graphic=(ord("."), (209, 166, 108), (85, 49, 0)),
            move_cost=100,
        ),
        _Tile(  # https://paletton.com/#uid=1000I0k00f+07rC01lv029L0u18
            name="rock wall",
            graphic=(ord("="), (78, 78, 78), (171, 171, 171)),
            dig_cost=250,
        ),
        _Tile(
            name="rock floor",
            graphic=(ord("."), (191, 191, 191), (9, 9, 9)),
            move_cost=100,
        ),
    ],
    dtype=TILE_DTYPE,
)
TILES = {str(item["name"]): i for i, item in enumerate(TILE_DB)}
