#!/usr/bin/env python3
import ctypes
import numpy as np

from picosdk.functions import adc2mV, assert_pico_ok, mV2adc



class Ps5000Device():
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__('picosdk.ps5000')
        self.ps = module.ps5000

        # picoscope channels
        self.channels = {i : f'PS5000_CHANNEL_{i}' for i in ['A', 'B']}

    # Open the picoscope
    def initialize(self):
        self.status["openunit"] = self.ps.ps5000OpenUnit(ctypes.byref(chandle))
        print(self.status)
        assert_pico_ok(status["openunit"])

    def set_channel(self, ch_name):
        channel = self.ps.PS5000_CHANNEL[self.channels[ch_name]]
        ch_range = self.ps.PS5000_RANGE["PS5000_20V"]
        coupling = 1 # DC

        status[f"setCh{ch_name}"] = self.ps.ps5000SetChannel(chandle, channel, 1, coupling, ch_range)
        assert_pico_ok(status[f"setCh{ch_name}"])



class Ps6000Device():
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__('picosdk.ps6000')
        self.ps = module.ps6000

    # Open the picoscope
    def initialize(self):
        self.status["openunit"] = self.ps.ps6000OpenUnit(ctypes.byref(chandle))
        print(self.status)
        assert_pico_ok(status["openunit"])



class PicoDevice1():
    def __init__(self):
        scipy = __import__('scipy.constants')
        self.const = scipy.constants
        print(1)
    def call(self):
        print('dumm')
        print(self.const.k)
        test = {i : f'PS5000_CHANNEL_{i}' for i in ['A', 'B']}
        print(test)

class PicoDevice2():
    def __init__(self):
        print(2)
    def call(self):
        print('batz')

def make_device_class(version):
    if version == 'ps5000':
        device = PicoDevice1()
    else:
        device = PicoDevice2()
    return device

if __name__ == '__main__':
    bla = make_device_class('ps5000')
    bla.call()

    blup = make_device_class('ps6000')
    blup.call()

    # test = Ps5000Device()

    # print(const.k)
