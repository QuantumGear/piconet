#!/usr/bin/env python3
from picosdk.discover import find_all_units
from picosdk.errors import DeviceNotFoundError


def list_devices() -> list:
    # We need to do try-except because picosdk throws an error if no devices connected.
    # In this case we just return an empty list.
    try:
        return find_all_units()
    except DeviceNotFoundError:
        return []
