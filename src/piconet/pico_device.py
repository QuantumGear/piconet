#!/usr/bin/env python3
import ctypes
import numpy as np

from picosdk.functions import adc2mV, assert_pico_ok, assert_pico2000_ok, mV2adc

#!/usr/bin/env python3
from picosdk.discover import find_all_units
from picosdk.errors import DeviceNotFoundError

import matplotlib.pyplot as plt


def list_devices() -> list:
    # We need to do try-except because picosdk throws an error if no devices connected.
    # In this case we just return an empty list.
    try:
        return find_all_units()
    except DeviceNotFoundError:
        return []

class Ps2000Device():
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__('picosdk.ps2000')
        self.ps = module.ps2000.ps2000

        # picoscope channels
        self.channels = {'A' : 0, 'B' : 1}
        self.ch_range = 7 # 2V

        preTriggerSamples = 1000
        postTriggerSamples = 1000
        self.maxSamples = preTriggerSamples + postTriggerSamples

        self.timebase = 8
        self.timeInterval = ctypes.c_int32()
        self.timeUnits = ctypes.c_int32()
        self.oversample = ctypes.c_int16(1)
        self.maxSamplesReturn = ctypes.c_int32()

    # Open the picoscope
    def initialize(self):
        self.status["openUnit"] = self.ps.ps2000_open_unit()
        # self.status["openunit"] = self.ps.open_unit(ctypes.byref(self.chandle))
        assert_pico2000_ok(self.status["openUnit"])

    def set_channel(self, ch_name):
        self.chandle = ctypes.c_int16(self.status["openUnit"])
        channel = self.channels[ch_name]
        coupling = 1 # DC

        self.status[f"setCh{ch_name}"] = self.ps.ps2000_set_channel(self.chandle, channel, 1, coupling, self.ch_range)

    def set_trigger(self):
        self.status["trigger"] = self.ps.ps2000_set_trigger(self.chandle, 0, 64, 0, 0, 1000)


    def get_timebase(self):
        self.status["getTimebase"] = self.ps.ps2000_get_timebase(self.chandle, self.timebase, self.maxSamples, 
            ctypes.byref(self.timeInterval), ctypes.byref(self.timeUnits), self.oversample, 
            ctypes.byref(self.maxSamplesReturn))

    def run_block(self):
        timeIndisposedms = ctypes.c_int32()
        self.status["runBlock"] = self.ps.ps2000_run_block(self.chandle, self.maxSamples, self.timebase, self.oversample, ctypes.byref(timeIndisposedms))

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = self.ps.ps2000_ready(self.chandle)
            ready = ctypes.c_int16(self.status["isReady"])

        bufferA = (ctypes.c_int16 * self.maxSamples)()
        bufferB = (ctypes.c_int16 * self.maxSamples)()

        cmaxSamples = ctypes.c_int32(self.maxSamples)
        self.status["getValues"] = self.ps.ps2000_get_values(self.chandle, ctypes.byref(bufferA), 
            ctypes.byref(bufferB), None, None, ctypes.byref(self.oversample), cmaxSamples)

        maxADC = ctypes.c_int16(32767)

        # convert ADC counts data to mV
        adc2mVChA =  adc2mV(bufferA, self.ch_range, maxADC)

        # Create time data
        time = np.linspace(0, (cmaxSamples.value -1) * self.timeInterval.value, cmaxSamples.value)

        # plot data from channel A and B
        plt.plot(time, adc2mVChA[:])
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()

        # Stop the scope
        # handle = chandle
        self.status["stop"] = self.ps.ps2000_stop(self.chandle)

        # Close unitDisconnect the scope
        # handle = chandle
        self.status["close"] = self.ps.ps2000_close_unit(self.chandle)
        assert_pico2000_ok(self.status["close"])
        print(self.status)





class Ps5000aDevice():
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__('picosdk.ps5000a')
        self.ps = module.ps5000a.ps5000a

        # picoscope channels
        self.channels = {i : f'PS5000a_CHANNEL_{i}' for i in ['A', 'B']}

        self.resolution = self.ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]

    # Open the picoscope
    def initialize(self):
        self.status["openunit"] = self.ps.ps5000aOpenUnit(
            ctypes.byref(self.chandle),
            None,
            self.resolution)
        # self.status["openunit"] = self.ps.open_unit(ctypes.byref(self.chandle))
        print(self.status)
        assert_pico_ok(self.status["openunit"])

    def set_channel(self, ch_name):
        channel = self.ps.PS5000A_CHANNEL[self.channels[ch_name]]
        ch_range = self.ps.PS5000A_RANGE["PS5000A_20V"]
        coupling = 1 # DC

        status[f"setCh{ch_name}"] = self.ps.ps5000aSetChannel(chandle, channel, 1, coupling, ch_range)
        assert_pico_ok(status[f"setCh{ch_name}"])




class Ps6000Device():
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__('picosdk.ps6000')
        self.ps = module.ps6000.ps6000

    # Open the picoscope
    def initialize(self):
        self.status["openunit"] = self.ps.ps6000OpenUnit(ctypes.byref(self.chandle))
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
    # bla = make_device_class('ps5000')
    # bla.call()

    # blup = make_device_class('ps6000')
    # blup.call()
    # dev = list_devices()
    # print(dev)

    test = Ps2000Device()
    test.initialize()
    test.set_channel('A')
    test.set_trigger()
    test.get_timebase()
    test.run_block()

    # print(const.k)
