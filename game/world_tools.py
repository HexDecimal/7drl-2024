"""Functions for working with worlds."""
from __future__ import annotations

from random import Random

from tcod.ecs import Registry

from game.components import Graphic, Position
from game.tags import IsActor, IsPlayer


def new_world() -> Registry:
    """Return a freshly generated world."""
    world = Registry()

    rng = world[None].components[Random] = Random()

    player = world[object()]
    player.components[Position] = Position(5, 5)
    player.components[Graphic] = Graphic(ord("@"))
    player.tags |= {IsPlayer, IsActor}

    return world
