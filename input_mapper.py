from __future__ import annotations

from typing import Set, Iterable
from pynput.keyboard import Key
from utils import send_key_press, send_key_release


def press_key(k: object) -> None:
    send_key_press(k)


def release_key(k: object) -> None:
    send_key_release(k)


def update_stick_keys(stick_id: str, target_keys: Iterable[object], currently_held: Set[object]) -> Set[object]:
    target = set(target_keys)
    # Release keys no longer needed
    for key in currently_held - target:
        release_key(key)
    # Press newly needed keys
    for key in target - currently_held:
        press_key(key)
    return target


