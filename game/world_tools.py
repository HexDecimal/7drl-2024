"""Functions for working with worlds."""
from __future__ import annotations

from random import Random

from tcod.ecs import Registry

import game.map_tools
from game.components import Graphic, Position
from game.tags import ChildOf, IsActor, IsPlayer, IsStart


def new_world() -> Registry:
    """Return a freshly generated world."""
    world = Registry()

    world[None].components[Random] = Random()
    map_ = game.map_tools.new_map(world)

    (start,) = world.Q.all_of(tags=[IsStart], relations=[(ChildOf, map_)])

    player = world[object()]
    player.components[Position] = start.components[Position]
    player.components[Graphic] = Graphic(ord("@"))
    player.tags |= {IsPlayer, IsActor}

    return world
