from __future__ import annotations

from typing import Set

_connected_sides: Set[str] = set()


def register_controller(side: str) -> None:
    side_norm = side.lower()
    _connected_sides.add(side_norm)


def unregister_controller(side: str) -> None:
    side_norm = side.lower()
    _connected_sides.discard(side_norm)


def is_single_controller_mode() -> bool:
    return len(_connected_sides) == 1


def which_single_controller() -> str | None:
    if len(_connected_sides) == 1:
        return next(iter(_connected_sides))
    return None


