"""Functions for working with maps."""
from __future__ import annotations

import numpy as np
from tcod.ecs import Entity, Registry

from game.components import MapShape, MapTiles


def new_map(world: Registry) -> Entity:
    """Return a new map."""
    map_ = world[object()]
    shape = map_.components[MapShape] = (2048, 2048)
    tiles = map_.components[MapTiles] = np.zeros(shape=shape, dtype=np.uint8)
    tiles[1:-1, 1:-1] = 1

    return map_
