"""Collection of actions."""
from __future__ import annotations

import attrs
from tcod.ecs import Entity

from game.action import Action, Done, ExecuteResult, Impossible, Planner, PlanResult
from game.components import MapTiles, Position


@attrs.define
class MoveAction(Action):
    """Handle basic movement."""

    direction: tuple[int, int]

    def plan(self, entity: Entity) -> PlanResult:
        """Verify movement."""
        pos = entity.components[Position]
        dest = pos + self.direction
        tiles = pos.z.components[MapTiles]
        if tiles[dest.y, dest.x] == 0:
            return Impossible("Path is blocked.")
        return self

    def execute(self, entity: Entity) -> ExecuteResult:
        """Move the entity."""
        entity.components[Position] += self.direction
        return Done()


@attrs.define
class BumpAction(Planner):
    """Context sensitive action."""

    direction: tuple[int, int]

    def plan(self, entity: Entity) -> PlanResult:
        """Defer to a connext sensitive action."""
        return MoveAction(self.direction).plan(entity)
