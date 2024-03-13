"""Action base classes."""

from __future__ import annotations

from typing import Literal, Protocol, TypeAlias

import attrs
from tcod.ecs import Entity


class Planner(Protocol):
    """Handle complex actions via a planner hierarchy."""

    __slots__ = ()

    def plan(self, entity: Entity) -> PlanResult:
        """Decide how an actions goal will be reached."""
        raise NotImplementedError()


class Executer(Protocol):
    """Base class for executable actions."""

    __slots__ = ()

    def execute(self, entity: Entity) -> ExecuteResult:
        """Perform the actual action."""
        raise NotImplementedError()


class Action(Planner, Executer):
    """Base class for actions."""

    __slots__ = ()


@attrs.define
class Impossible:
    """This action can not be performed."""

    reason: str

    def __bool__(self) -> Literal[False]:
        """This result is falsy."""
        return False


@attrs.define
class Done:
    """Action is finished."""

    time_cost: int = 100


PlanResult: TypeAlias = "Impossible | Executer"
ExecuteResult: TypeAlias = "Done"
