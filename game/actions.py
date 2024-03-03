"""Collection of actions."""
from __future__ import annotations

import attrs
from tcod.ecs import Entity

from game.action import Action, Done, ExecuteResult, Impossible, Planner, PlanResult
from game.components import MapTiles, Position
from game.tiles import TILE_DB


@attrs.define
class MoveAction(Action):
    """Handle basic movement."""

    direction: tuple[int, int]

    def plan(self, entity: Entity) -> PlanResult:
        """Verify movement."""
        pos = entity.components[Position]
        dest = pos + self.direction
        tiles = pos.z.components[MapTiles]

        if TILE_DB["move_cost"][tiles[dest.y, dest.x]]:
            return self
        if TILE_DB["dig_cost"][tiles[dest.y, dest.x]]:
            return self
        return Impossible("Path is blocked.")

    def execute(self, entity: Entity) -> ExecuteResult:
        """Move the entity."""
        pos = entity.components[Position] = entity.components[Position] + self.direction
        tiles = pos.z.components[MapTiles]

        if TILE_DB["dig_cost"][tiles[pos.y, pos.x]]:
            tiles[pos.y, pos.x] += 1  # The next index is always the dug-out tile.
            return Done(TILE_DB["dig_cost"][tiles[pos.y, pos.x]])
        return Done(TILE_DB["move_cost"][tiles[pos.y, pos.x]])


@attrs.define
class BumpAction(Planner):
    """Context sensitive action."""

    direction: tuple[int, int]

    def plan(self, entity: Entity) -> PlanResult:
        """Defer to a connext sensitive action."""
        return MoveAction(self.direction).plan(entity)
