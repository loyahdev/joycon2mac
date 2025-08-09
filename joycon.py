import logging
from typing import Dict, Set, Tuple
import math
from pynput.keyboard import Key
from input_mapper import press_key, release_key, update_stick_keys
from app_state import is_single_controller_mode, which_single_controller

MASKS = {
    "right": {
        "A":    0x000800,
        "B":    0x000400,
        "X":    0x000200,
        "Y":    0x000100,
        "PLUS": 0x000002,
        "STICK":0x000004,
        "SL":  0x002000,
        "SR":  0x001000,
        "R":  0x004000,
        "ZR":  0x008000,
        "HOME": 0x000010,
        "CHAT": 0x000040,
    },
    "left": {
        "UP":     0x000002,
        "DOWN":   0x000001,
        "LEFT":   0x000008,
        "RIGHT":  0x000004,
        "MINUS":  0x000100,
        "STICK":  0x000800,
        "SHARE":  0x002000,
        "SL":  0x000020,
        "SR":  0x000010,
        "L": 0x000040,
        "ZL": 0x000080
    }
}
class JoyCon:
    def __init__(self, side: str = "right"):
        self.side = side
        self.is_left = side != "right"
        self._last_data: bytes | None = None
        self._prev_buttons_state: int = 0
        # Track which stick-direction keys are currently held to avoid repeats
        self._held_left_stick_keys: Set[object] = set()
        self._held_right_stick_keys: Set[object] = set()

    def process_buttons(self, data: bytes) -> None:
        button_map = MASKS[self.side]

        offset = 4 if self.is_left else 3
        bits_now = int.from_bytes(data[offset:offset+3], "big")
        bits_prev = int.from_bytes(self._last_data[offset:offset+3], "big") if self._last_data else 0

        # Map Joy-Con buttons to keyboard keys
        single_mode = is_single_controller_mode()
        single_which = which_single_controller() if single_mode else None

        if self.is_left:
            # Base mapping for LEFT Joy-Con
            key_mapping: Dict[str, object] = {
                "UP": Key.up,
                "DOWN": Key.down,
                "LEFT": Key.left,
                "RIGHT": Key.right,
                "ZL": "1",
                "L": "2",
                "SL": "3",
                "SR": "4",
                "MINUS": "5",
                "SHARE": "z",
            }
            # Single-mode override for D-Pad mapping
            if single_mode and single_which == "left":
                key_mapping.update({
                    # Arrow outputs remapped: UP/DOWN/LEFT/RIGHT = DPAD RIGHT/LEFT/UP/DOWN
                    "RIGHT": Key.up,
                    "LEFT": Key.down,
                    "UP": Key.left,
                    "DOWN": Key.right,
                })
        else:
            # Base mapping for RIGHT Joy-Con
            key_mapping = {
                # Default dual-mode face buttons: I=Y, J=X, K=B, L=A
                "X": "i",
                "Y": "j",
                "B": "k",
                "A": "l",
                "R": "9",
                "ZR": "0",
                "SR": "7",
                "SL": "8",
                "PLUS": "6",
                "HOME": "n",
                "CHAT": "m",
            }
            # Single-mode override for face buttons: IJKL = Y B A X
            if single_mode and single_which == "right":
                key_mapping.update({
                    "Y": "i",
                    "B": "j",
                    "A": "k",
                    "X": "l",
                    # Swap 7 and 8 for right Joy-Con SL/SR in single mode
                    "SR": "8",
                    "SL": "7",
                })

        for name, mask in button_map.items():
            now = bool(bits_now & mask)
            prev = bool(bits_prev & mask)
            if name in key_mapping:
                mapped_key = key_mapping[name]
                if now and not prev:
                    press_key(mapped_key)
                elif not now and prev:
                    release_key(mapped_key)
        self._last_data = data
                    

    def process_sticks(self, data: bytes) -> Tuple[int, int]:
        stick_data = data[10:13] if self.is_left else data[13:16]
        if len(stick_data) != 3:
            return 0, 0
        raw_x = ((stick_data[1] & 0x0F) << 8) | stick_data[0]
        raw_y = (stick_data[2] << 4) | ((stick_data[1] & 0xF0) >> 4)
        x = (raw_x - 2048) / 2048.0
        y = (raw_y - 2048) / 2048.0

        # Digitalize to keys per requested mapping (8-direction quantization)
        target_keys: Set[object] = set()
        single_mode = is_single_controller_mode()
        single_which = which_single_controller() if single_mode else None

        # Compute 8-direction sector if outside deadzone
        deadzone = 0.15
        r = math.hypot(x, y)
        sector = None
        if r >= deadzone:
            # Angle: 0=Right, 90=Up, 180=Left, 270=Down (y negative is up in our stick space)
            angle = (math.degrees(math.atan2(-y, x)) + 360.0) % 360.0
            sector = int((angle + 22.5) // 45) % 8  # 0..7 centered sectors

        def add_dir(dir_code: str) -> None:
            if self.is_left:
                if single_mode and single_which == "left":
                    # Left-only: custom mapping: W=RIGHT, A=UP, S=LEFT, D=DOWN
                    mapping = {"U": "D", "D": "A", "L": "s", "R": "w"}
                else:
                    # Dual-mode: Left stick → WASD, with W/S swapped per your request
                    mapping = {"U": "s", "D": "w", "L": "a", "R": "d"}
            else:
                if single_mode and single_which == "right":
                    # Right-only: W A S D = LEFT, DOWN, RIGHT, UP respectively
                    # Swap A and D as requested
                    mapping = {"L": "w", "D": "d", "R": "s", "U": "a"}
                else:
                    # Dual-mode: Right stick → TFGH with T/G swapped per your request
                    mapping = {"U": "g", "D": "t", "L": "f", "R": "h"}
            key = mapping.get(dir_code)
            if key:
                target_keys.add(key)

        if self.is_left:
            if sector is not None:
                if sector in (0, 7):
                    add_dir("R")
                if sector in (1,):
                    add_dir("U"); add_dir("R")
                if sector in (2,):
                    add_dir("U")
                if sector in (3,):
                    add_dir("U"); add_dir("L")
                if sector in (4,):
                    add_dir("L")
                if sector in (5,):
                    add_dir("D"); add_dir("L")
                if sector in (6,):
                    add_dir("D")
                if sector in (7,):
                    add_dir("D"); add_dir("R")
            self._held_left_stick_keys = update_stick_keys("left", target_keys, self._held_left_stick_keys)
        else:
            if sector is not None:
                if sector in (0, 7):
                    add_dir("R")
                if sector in (1,):
                    add_dir("U"); add_dir("R")
                if sector in (2,):
                    add_dir("U")
                if sector in (3,):
                    add_dir("U"); add_dir("L")
                if sector in (4,):
                    add_dir("L")
                if sector in (5,):
                    add_dir("D"); add_dir("L")
                if sector in (6,):
                    add_dir("D")
                if sector in (7,):
                    add_dir("D"); add_dir("R")
            self._held_right_stick_keys = update_stick_keys("right", target_keys, self._held_right_stick_keys)

        # For potential mouse usage by another layer, return scaled deltas
        sensitivity = 4
        move_x = -int(max(-1.0, min(1.0, x * 1.7)) * sensitivity)
        move_y = int(max(-1.0, min(1.0, y * 1.7)) * sensitivity)
        return move_x, move_y