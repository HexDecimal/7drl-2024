"""Rendering functions."""
from __future__ import annotations

import numpy as np
import tcod.console
from tcod.ecs import Registry

from game.components import Graphic, MapTiles, Position
from game.tags import IsPlayer


def render_map(world: Registry, console: tcod.console.Console) -> None:
    """Draw the visible map."""
    (player,) = world.Q.all_of(tags=[IsPlayer])
    tiles = player.components[Position].z.components[MapTiles]

    TILE_GRAPHICS = np.array(
        [
            (ord("#"), (255, 255, 255), (0, 0, 0)),
            (ord("."), (64, 64, 64), (0, 0, 0)),
        ],
        dtype=tcod.console.rgb_graphic,
    )

    console.rgb[:] = np.choose(tiles[: console.height, : console.width], TILE_GRAPHICS)

    for entity in world.Q.all_of(components=[Position, Graphic]):
        pos = entity.components[Position]
        if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
            continue
        graphic = entity.components[Graphic]
        console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg
