"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

def crc8_pedal(data):
    """
    Calculate CRC8 checksum for pedal commands.
    BlackPanda may not use CRC8, so this can be removed if not needed.
    """
    crc = 0xFF    # standard init value
    poly = 0xD5   # standard crc8: x8+x7+x6+x4+x2+1
    size = len(data)
    for i in range(size - 1, -1, -1):
        crc ^= data[i]
        for _ in range(8):
            if (crc & 0x80) != 0:
                crc = ((crc << 1) ^ poly) & 0xFF
            else:
                crc <<= 1
    return crc


def create_gas_interceptor_command(packer, gas_amount, idx):
    """
    Generate gas interceptor command compatible with BlackPanda.
    Modified to match expected CAN message format for BlackPanda.
    """
    # BlackPanda typically expects values in range [0, 255] for gas commands
    gas_scaled = int(gas_amount * 255) if gas_amount > 0.001 else 0

    values = {
        "GAS_COMMAND": gas_scaled,
        "GAS_COMMAND2": gas_scaled,  # Some implementations use duplicate fields
        "ENABLE": gas_scaled > 0,
        "COUNTER_PEDAL": idx & 0xF,  # BlackPanda may expect different counter naming
    }

    # BlackPanda may not use CRC8 checksum, so we can optionally include it
    if hasattr(packer, 'needs_checksum') and packer.needs_checksum:
        dat = packer.make_can_msg("GAS_COMMAND", 0, values)[1]
        values["CHECKSUM_PEDAL"] = crc8_pedal(dat[:-1])

    return packer.make_can_msg("GAS_COMMAND", 0, values)