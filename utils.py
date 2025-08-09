
import sys
from os import path
from typing import Literal
from pathlib import Path
import traceback
import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
import platform

# Constants
JOYCON_MANUFACTURER_ID = 1363
JOYCON_MANUFACTURER_PREFIX = bytes([0x01, 0x00, 0x03, 0x7E])

# BLE GATT Characteristics UUID
INPUT_REPORT_UUID = "ab7de9be-89fe-49ad-828f-118f09df7fd2"
WRITE_COMMAND_UUID = "649d4ac9-8eb7-4e6c-af44-1ea54fe5f005"

# COMMANDS
COMMAND_LEDS = 0x09
COMMAND_VIBRATION = 0x0A

# SUBCOMMANDS
SUBCOMMAND_SET_PLAYER_LEDS = 0x07
SUBCOMMAND_PLAY_VIBRATION_PRESET = 0x02


def decode_joystick(data):
    try:
        if len(data) != 3:
            return 0, 0
        x = ((data[1] & 0x0F) << 8) | data[0]
        y = (data[2] << 4) | ((data[1] & 0xF0) >> 4)
        x = (x - 2048) / 2048.0
        y = (y - 2048) / 2048.0
        deadzone = 0.08
        if abs(x) < deadzone and abs(y) < deadzone:
            return 0, 0
        x = max(-1.0, min(1.0, x * 1.7))
        y = max(-1.0, min(1.0, y * 1.7))
        return int(x * 32767), int(y * 32767)
    except:
        return 0, 0
    

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    system = platform.system()
    if system == "Windows":
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    else:
        return relative_path


# Global controllers (requires Accessibility permission on macOS)
mouse_controller = MouseController()
keyboard_controller = KeyboardController()


def send_mouse_move(dx: int, dy: int) -> None:
    try:
        x, y = mouse_controller.position
        mouse_controller.position = (x + dx, y + dy)
    except Exception:
        pass


def send_key_press(k: object) -> None:
    try:
        keyboard_controller.press(k)
    except Exception:
        pass


def send_key_release(k: object) -> None:
    try:
        keyboard_controller.release(k)
    except Exception:
        pass


def get_bluetooth_authorization_status() -> Literal["allowed", "denied", "restricted", "not_determined", "unknown"]:
    """Returns CoreBluetooth authorization state on macOS if available.
    Values: 'allowed', 'denied', 'restricted', 'not_determined', 'unknown'."""
    try:
        # Prefer CBManager.authorization() if available (macOS 10.15+)
        from CoreBluetooth import CBManager
        try:
            auth_val = CBManager.authorization()
        except Exception:
            auth_val = None

        if auth_val is None:
            # Fallback to instance property
            from CoreBluetooth import CBCentralManager
            mgr = CBCentralManager.alloc().init()
            if hasattr(mgr, "authorization"):
                auth_val = mgr.authorization()

        # Map numeric to names if needed
        try:
            from CoreBluetooth import (
                CBManagerAuthorizationNotDetermined,
                CBManagerAuthorizationRestricted,
                CBManagerAuthorizationDenied,
                CBManagerAuthorizationAllowedAlways,
            )
            if auth_val == CBManagerAuthorizationAllowedAlways:
                return "allowed"
            if auth_val == CBManagerAuthorizationDenied:
                return "denied"
            if auth_val == CBManagerAuthorizationRestricted:
                return "restricted"
            if auth_val == CBManagerAuthorizationNotDetermined:
                return "not_determined"
        except Exception:
            # Some PyObjC versions don't expose the constants; use integers
            # Known mapping: 0=not_determined, 1=restricted, 2=denied, 3=allowed
            if auth_val == 3:
                return "allowed"
            if auth_val == 2:
                return "denied"
            if auth_val == 1:
                return "restricted"
            if auth_val == 0:
                return "not_determined"
    except Exception:
        pass
    return "unknown"


def _get_app_data_dir() -> Path:
    # Reuse user_preferences path to stay consistent
    try:
        from user_preferences import get_settings_path
        return Path(get_settings_path()).parent
    except Exception:
        # Fallback to home directory if anything goes wrong
        return Path.home() / ".joycon2mouse"


def write_crash_log(text: str) -> None:
    try:
        data_dir = _get_app_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "last_error.log").write_text(text, encoding="utf-8")
    except Exception:
        pass


def show_error_dialog(title: str, message: str) -> None:
    try:
        # Create a transient, hidden root for the dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        # As a fallback, write to crash log
        write_crash_log(f"{title}\n\n{message}\n\n{traceback.format_exc()}")
