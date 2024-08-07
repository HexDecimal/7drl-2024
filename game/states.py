"""A collection of game states."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import attrs
import tcod.console
import tcod.event
from tcod.ecs import Entity
from tcod.event import KeySym

import g
import game.actions
import game.rendering
import game.world_tools
from game.action import Impossible, Planner
from game.components import Position
from game.state import Pop, Push, Rebase, State, StateResult
from game.tags import IsPlayer

DIRECTION_KEYS: Final = {
    # Arrow keys
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    # Arrow key diagonals
    KeySym.HOME: (-1, -1),
    KeySym.END: (-1, 1),
    KeySym.PAGEUP: (1, -1),
    KeySym.PAGEDOWN: (1, 1),
    # Keypad
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_8: (0, -1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_1: (-1, 1),
    KeySym.KP_9: (1, -1),
    KeySym.KP_3: (1, 1),
    # VI keys
    KeySym.h: (-1, 0),
    KeySym.l: (1, 0),
    KeySym.k: (0, -1),
    KeySym.j: (0, 1),
    KeySym.y: (-1, -1),
    KeySym.b: (-1, 1),
    KeySym.u: (1, -1),
    KeySym.n: (1, 1),
}


def do_action(entity: Entity, action: Planner) -> StateResult:
    """Perform an action."""
    plan_result = action.plan(entity)
    match plan_result:
        case Impossible(reason=_reason):
            pass
        case _:
            plan_result.execute(entity)
    return None


@attrs.define(eq=False)
class InGame(State):
    """Primary in-game state."""

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events for the in-game state."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                return do_action(player, game.actions.BumpAction(DIRECTION_KEYS[sym]))
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw the standard screen."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        game.rendering.render_map(g.world, console)
        console.print(0, 0, str(player.components[Position]), fg=(255, 255, 255), bg=(0, 0, 0))


@attrs.define()
class MenuItem:
    """Clickable menu item."""

    label: str
    callback: Callable[[], StateResult]


@attrs.define(eq=False)
class ListMenu(State):
    """Simple list menu state."""

    items: tuple[MenuItem, ...]
    selected: int | None = 0
    x: int = 0
    y: int = 0

    def on_event(self, event: tcod.event.Event) -> StateResult:  # noqa: PLR0911
        """Handle events for menus."""
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                dx, dy = DIRECTION_KEYS[sym]
                if dx != 0 or dy == 0:
                    return None
                if self.selected is not None:
                    self.selected += dy
                else:
                    self.selected = 0 if dy == 1 else -1
                self.selected %= len(self.items)
                return None
            case tcod.event.MouseMotion(position=(_, y)):
                y -= self.y
                self.selected = y if 0 <= y < len(self.items) else -1
                return None
            case tcod.event.KeyDown(sym=KeySym.RETURN):
                return self.activate_selected()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.LEFT):
                return self.activate_selected()
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return self.on_cancel()
            case _:
                return None

    def activate_selected(self) -> StateResult:
        """Call the selected menu items callback."""
        if self.selected is not None:
            return self.items[self.selected].callback()
        return None

    def on_cancel(self) -> StateResult:
        """Handle escaped being pressed on menus."""
        return Pop()

    def on_draw(self, console: tcod.console.Console) -> None:
        """Render the menu."""
        current_index = g.states.index(self)
        if current_index > 0:
            g.states[current_index - 1].on_draw(console)
        if g.states[-1] is self:
            console.rgb["fg"] //= 4
            console.rgb["bg"] //= 4
        for i, item in enumerate(self.items):
            is_selected = i == self.selected
            console.print(
                self.x,
                self.y + i,
                item.label,
                fg=(255, 255, 255),
                bg=(64, 64, 64) if is_selected else (0, 0, 0),
            )


class MainMenu(ListMenu):
    """Main/escape menu."""

    __slots__ = ()

    def __init__(self) -> None:
        """Initialize the main menu."""
        items = [
            MenuItem("New game", self.new_game),
            MenuItem("Quit", self.quit),
        ]
        if hasattr(g, "world"):
            items.insert(0, MenuItem("Continue", self.continue_))

        super().__init__(
            items=tuple(items),
            x=5,
            y=5,
        )

    def continue_(self) -> StateResult:
        """Return to the game."""
        return Rebase(InGame())

    def new_game(self) -> StateResult:
        """Begin a new game."""
        g.world = game.world_tools.new_world()
        return Rebase(InGame())

    def quit(self) -> StateResult:
        """Close the program."""
        raise SystemExit
