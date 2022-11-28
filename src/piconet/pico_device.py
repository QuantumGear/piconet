#!/usr/bin/env python3
import ctypes
import numpy as np
from abc import abstractmethod, ABCMeta

from picosdk.functions import adc2mV, assert_pico_ok, assert_pico2000_ok, mV2adc
from picosdk.discover import find_all_units
from picosdk.errors import DeviceNotFoundError

import matplotlib.pyplot as plt
import asyncio

def list_devices() -> list:
    # We need to do try-except because picosdk throws an error if no devices connected.
    # In this case we just return an empty list.
    try:
        return find_all_units()
    except DeviceNotFoundError:
        return []


class OpenError(Exception):
    pass


class AbstractScope(metaclass=ABCMeta):
    @abstractmethod
    def open(self):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()


class Ps2000Device(AbstractScope):
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}

        # import the pidcodsk module
        module = __import__("picosdk.ps2000")
        self.ps = module.ps2000.ps2000

        # picoscope channels
        self.channels = {"A": 0, "B": 1}
        self._ch_A_range = 7  # 2V
        self._ch_B_range = 7  # 2V

        preTriggerSamples = 1000
        postTriggerSamples = 1000
        self.maxSamples = preTriggerSamples + postTriggerSamples

        self.timebase = 8
        self.timeInterval = ctypes.c_int32()
        self.timeUnits = ctypes.c_int32()
        self.oversample = ctypes.c_int16(1)
        self.maxSamplesReturn = ctypes.c_int32()

        # allowed channel values in volts
        self.allowed_ch_ranges = {
            0.02: 1,
            0.05: 2,
            0.1: 3,
            0.2: 4,
            0.5: 5,
            1.0: 6,
            2.0: 7,
            5.0: 8,
            10.0: 9,
            20.0: 10,
        }

    # __enter__  method is executed when entering 'with'
    def __enter__(self):
        self.open()
        return self

    # __exit__ method is executed when leabing 'with'
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # Open the picoscope
    def open(self):
        self.status["openUnit"] = self.ps.ps2000_open_unit()
        # self.status["openunit"] = self.ps.open_unit(ctypes.byref(self.chandle))
        assert_pico2000_ok(self.status["openUnit"])

    def close(self):
        # Stop the scope
        self.status["stop"] = self.ps.ps2000_stop(self.chandle)

        # Close unitDisconnect the scope
        self.status["close"] = self.ps.ps2000_close_unit(self.chandle)
        assert_pico2000_ok(self.status["close"])

    @property
    def ch_A_range(self):
        return self._ch_A_range

    @ch_A_range.setter
    def ch_A_range(self, value):
        if value not in self.allowed_ch_ranges:
            print("Wrong channel range")
        else:
            if self._ch_A_range != self.allowed_ch_ranges[value]:
                self._ch_A_range = self.allowed_ch_ranges[value]

    @property
    def ch_B_range(self):
        return self._ch_B_range

    @ch_B_range.setter
    def ch_B_range(self, value):
        if self._ch_B_range != value:
            self._ch_B_range = value

    def set_channel(self, ch_name):
        self.chandle = ctypes.c_int16(self.status["openUnit"])
        channel = self.channels[ch_name]
        coupling = 1  # DC
        if ch_name == "A":
            ch_range = self._ch_A_range
        else:
            ch_range = self._ch_B_range

        self.status[f"setCh{ch_name}"] = self.ps.ps2000_set_channel(
            self.chandle, channel, 1, coupling, ch_range
        )

    def set_trigger(self):
        self.status["trigger"] = self.ps.ps2000_set_trigger(
            self.chandle, 0, 64, 0, 0, 1000
        )

    def get_timebase(self):
        self.status["getTimebase"] = self.ps.ps2000_get_timebase(
            self.chandle,
            self.timebase,
            self.maxSamples,
            ctypes.byref(self.timeInterval),
            ctypes.byref(self.timeUnits),
            self.oversample,
            ctypes.byref(self.maxSamplesReturn),
        )

    def acquire_data(self, blocking=True):
        timeIndisposedms = ctypes.c_int32()
        self.status["runBlock"] = self.ps.ps2000_run_block(
            self.chandle,
            self.maxSamples,
            self.timebase,
            self.oversample,
            ctypes.byref(timeIndisposedms),
        )

        if not blocking:
            return None
        data = None
        while data is None:
            data = self.get_aquired_data()
        return data

    def get_aquired_data(self):
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        self.status["isReady"] = self.ps.ps2000_ready(self.chandle)
        ready = ctypes.c_int16(self.status["isReady"])
        if ready.value == check.value:
            return None

        bufferA = (ctypes.c_int16 * self.maxSamples)()
        bufferB = (ctypes.c_int16 * self.maxSamples)()

        cmaxSamples = ctypes.c_int32(self.maxSamples)
        self.status["getValues"] = self.ps.ps2000_get_values(
            self.chandle,
            ctypes.byref(bufferA),
            ctypes.byref(bufferB),
            None,
            None,
            ctypes.byref(self.oversample),
            cmaxSamples,
        )

        maxADC = ctypes.c_int16(32767)

        # convert ADC counts data to mV
        adc2mVChA = adc2mV(bufferA, self._ch_A_range, maxADC)

        # Create time data
        time = np.linspace(
            0, (cmaxSamples.value - 1) * self.timeInterval.value, cmaxSamples.value
        )

        return time, adc2mVChA[:]

    async def acquire_data_coro(self):
        self.acquire_data(blocking=False)
        data = None
        while data is None:
            await asyncio.sleep(0)
            data = self.get_aquired_data()
        return data

    @property
    def is_running(self):
        return True

    def measure_permanent(self):
        import random

        while self.is_running:
            time, data = self.acquire_data()
            yield [time, data]



if __name__ == "__main__":
    time = 0
    voltage = 0
    with Ps2000Device() as sc:
        sc.ch_A_range = 0.1
        sc.set_channel("A")
        sc.set_trigger()
        sc.get_timebase()

        sc.acquire_data(blocking=False)
        data = None
        while data is None:
            data = sc.get_aquired_data()
            asyncio.wait(0.01)
        # gen = sc.measure_permanent()
        # for i in range(3):
        #     data = gen.next()
        # for i, data in enumerate(sc.measure_permanent()):
        #     if i > 10:
        #         break
        # test yield generator
        # for data in sc.measure_permanent():
        # print(data)

        time, voltage = sc.acquire_data()

    # plot data from channel A and B
    plt.plot(time, voltage)
    plt.xlabel("Time (ns)")
    plt.ylabel("Voltage (mV)")
    plt.show()

    # print(const.k)