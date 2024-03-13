"""Collection of common components."""

from __future__ import annotations

from typing import Self

import attrs
import numpy as np
import tcod.ecs.callbacks
from numpy.typing import NDArray
from tcod.ecs import Entity

from game.tags import ChildOf


@attrs.define(frozen=True)
class Position:
    """An entities position."""

    x: int
    y: int
    z: Entity

    @property
    def ij(self) -> tuple[int, int]:
        """Return the ij coordinates as a tuple."""
        return self.y, self.x

    def __add__(self, direction: tuple[int, int]) -> Self:
        """Add a vector to this position."""
        x, y = direction
        return self.__class__(self.x + x, self.y + y, self.z)


@tcod.ecs.callbacks.register_component_changed(component=Position)
def on_position_changed(entity: Entity, old: Position | None, new: Position | None) -> None:
    """Mirror position components as a tag."""
    if old == new:
        return
    if old is not None:
        entity.tags.discard(old)
    if new is not None:
        entity.tags.add(new)
        if entity.relation_tag.get(ChildOf) != new.z:
            entity.relation_tag[ChildOf] = new.z
    else:  # new is None
        del entity.relation_tag[ChildOf]


@attrs.define(frozen=True)
class Graphic:
    """An entities icon and color."""

    ch: int = ord("!")
    fg: tuple[int, int, int] = (255, 255, 255)


MapShape = ("MapShape", tuple[int, int])
"""Map shape (height, width)."""
MapTiles = ("MapTiles", NDArray[np.uint8])
"""Map tile indexes."""
