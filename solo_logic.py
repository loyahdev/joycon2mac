import asyncio
from joycon import JoyCon

# from mouse_simulator import *

# Button masks

def decode_gyro(data: bytes):
    if len(data) < 0x3C:
        return None

    def to_signed_16(b1, b2):
        return int.from_bytes(bytes([b1, b2]), byteorder='little', signed=True)

    gyro_x_raw = to_signed_16(data[0x36], data[0x37])
    gyro_y_raw = to_signed_16(data[0x38], data[0x39])
    gyro_z_raw = to_signed_16(data[0x3A], data[0x3B])

    scale = 360 / 48000

    gyro_x = gyro_x_raw * scale
    gyro_y = gyro_y_raw * scale
    gyro_z = gyro_z_raw * scale

    return gyro_x, gyro_y, gyro_z

def decode_accel(data: bytes):
    if len(data) < 0x36:  # accel bytes end at 0x35 (0x30..0x35)
        return None

    def to_signed_16(b1, b2):
        return int.from_bytes(bytes([b1, b2]), byteorder='little', signed=True)

    accel_x_raw = to_signed_16(data[0x30], data[0x31])
    accel_y_raw = to_signed_16(data[0x32], data[0x33])
    accel_z_raw = to_signed_16(data[0x34], data[0x35])

    scale = 1 / 4096  # 4096 = 1G

    accel_x = accel_x_raw * scale
    accel_y = accel_y_raw * scale
    accel_z = accel_z_raw * scale

    return accel_x, accel_y, accel_z
# BC CB 00 00 10 00 00 E0 FF 0F FF F7 7F DD 07 7E A4 00 74 01 77 11 77 0C 00 00 00 00 00 00 00 4D 0E 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
# SR


async def handle_single_notification(sender, data, is_left, gamepad: JoyCon, upright):
    if gamepad:
        # Buttons -> keyboard
        gamepad.process_buttons(data)
        # Sticks -> keyboard (and optional deltas for mouse)
        move_x, move_y = gamepad.process_sticks(data)
        # If you want to move the cursor using a sensor, do it elsewhere. For safety, we don't move mouse here continuously.