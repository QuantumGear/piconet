#!/usr/bin/env python3
import argparse
import sys
from .pico import list_devices


class PiconetError(Exception):
    """Expected exception that doesn't require traceback"""

    pass


def parse_args():
    """Defines cli arguments for the module"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--device",
        "-d",
        default=None,
        help="device to use, default - first available device",
    )
    subparsers = argparser.add_subparsers(help="command to run", dest="subparser_name")
    listparser = subparsers.add_parser(
        "list", help="lists all connected picoscopes and their info"
    )
    infoparser = subparsers.add_parser(
        "info", help="returns information about specific device"
    )
    return argparser.parse_args()


def print_devices(devices: list) -> None:
    """Prints a list of connected devices and their info (id and other stuff)"""
    if not devices:
        # special print if no devices connected
        print("No devices found")
        return
    print(f"Found {len(devices)} devices:")
    for device in devices:
        device_id = device.info.serial.decode()
        print(f"- [{device_id}] {device.info}")


def print_info(device) -> None:
    print(device.info)


def get_device_by_id(devices: list, device_id):
    for dev in devices:
        if dev.info.serial.decode() == device_id:
            return dev


def main():
    args = parse_args()
    cmd = args.subparser_name
    devices = list_devices()
    selected_device = None
    if args.device is None and devices:
        selected_device = devices[0]
    else:
        selected_device = get_device_by_id(devices, args.device)
    try:
        if cmd == "list":
            print_devices(devices)
        elif cmd == "info":
            if not devices:
                raise PiconetError("No devices connected!")
            if selected_device is None:
                raise PiconetError(f"Invalid device id: {args.device}")
            print_info(selected_device)
        else:
            print(f"No arguments provided. Type `{sys.argv[0]} -h` for help.")
    except PiconetError as e:
        print(f"Error while command:\n  {e}")
        # exit with error
        sys.exit(1)
