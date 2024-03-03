"""Rendering functions."""
from __future__ import annotations

import numpy as np
import tcod.camera
import tcod.console
from tcod.ecs import Registry

from game.components import Graphic, MapTiles, Position
from game.tags import IsPlayer
from game.tiles import TILE_DB


def render_map(world: Registry, console: tcod.console.Console) -> None:
    """Draw the visible map."""
    (player,) = world.Q.all_of(tags=[IsPlayer])
    center_pos = player.components[Position]
    tiles = center_pos.z.components[MapTiles]
    screen_shape = console.height, console.width
    camera_y, camera_x = tcod.camera.get_camera(screen_shape, center_pos.ij, (tiles.shape, 0.5))

    screen_slices, world_slices = tcod.camera.get_slices(screen_shape, tiles.shape, (camera_y, camera_x))

    console.rgb[screen_slices] = np.choose(tiles[world_slices], TILE_DB["graphic"])

    for entity in world.Q.all_of(components=[Position, Graphic]):
        pos = entity.components[Position]
        entity_x = pos.x - camera_x
        entity_y = pos.y - camera_y
        if not (0 <= entity_x < console.width and 0 <= entity_y < console.height):
            continue
        graphic = entity.components[Graphic]
        console.rgb[["ch", "fg"]][entity_y, entity_x] = graphic.ch, graphic.fg
