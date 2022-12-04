from .pico_device import Ps2000Device
import qcontrol4.gui.web.widgets as qw
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import logging
import sys
from typing import Optional, Callable, Union
from abc import abstractmethod, ABCMeta

"""
To do:
- implement abstract class
- implement dummy class
- add doc strings
- add types
"""

class AbstractScope(metaclass=ABCMeta):
    @abstractmethod
    def update(self):
        raise NotImplementedError()

    @abstractmethod
    async def capture_coro(self):
        raise NotImplementedError()

    @abstractmethod
    def singleshot(self):
        raise NotImplementedError()

    @abstractmethod
    def start_capture(self):
        raise NotImplementedError()

    @abstractmethod
    def stop_capture(self):
        raise NotImplementedError()



class DummyScope(AbstractScope):
    def __init__(self):
        self.ch_range = 0.1
        self._running = False

    def update(self):
        return

    async def capture_coro(self):
        n = 50
        while self._running:
            if self._capture_cb:
                x = np.linspace(0, 5, n)
                y = x**2 + np.rand.normal(0, 1, n)
                fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
                ax.plot(x, y)
                self._capture_cb(fig)

    def singleshot(self):
        x = np.linspace(0, 5, 20)
        y = np.linspace(0, 5, 20)
        fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
        ax.plot(x, y)
        return fig

    def start_capture(self, cb=None):
        self._capture_cb = cb
        if self._running:
            return
        self._running = True
        asyncio.get_event_loop().create_task(self.capture_coro())

    def stop_capture(self):
        self._running = False


class PicoScope:
    def __init__(self):
        self.ch_range = 0.1
        self.channel_name = "A"
        self._running = False

        self.sc = Ps2000Device()
        self.sc.open()
        self.sc.set_channel(self.channel_name)
        self.sc.set_trigger()
        self.sc.get_timebase()

    def update(self):
        self.sc.ch_A_range = self.ch_range
        self.sc.set_channel(self.channel_name)
        self.sc.set_trigger()
        self.sc.get_timebase()

    async def capture_coro(self):
        while self._running:
            if self._capture_cb:
                data = await self.sc.acquire_data_coro()
                fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
                ax.plot(*data)
                self._capture_cb(fig)

    def singleshot(self):
        x = np.linspace(0, 5, 20)
        y = np.linspace(0, 5, 20)
        fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
        ax.plot(x, y)
        return fig

    def start_capture(self, cb=None):
        self._capture_cb = cb
        if self._running:
            return
        self._running = True
        asyncio.get_event_loop().create_task(self.capture_coro())

    def stop_capture(self):
        self._running = False

    def __del__(self):
        self.sc.close()


def main():
    plt.style.use("dark_background")
    # scope = PicoScope()
    scope = DummyScope()
    with qw.Blocks() as app:
        with qw.Row():
            plot = qw.Plot(scale=3)
            with qw.Column():
                vrange = qw.Radio(
                    label="Voltage range", value="0.1", choices=["0.1", "1", "10"]
                )
        with qw.Row():
            singleshot = qw.Button("Single shot")
        with qw.Row():
            btn_start = qw.Button("Start")
            btn_stop = qw.Button("Stop")

    def update_plot(data):
        plot.value = data

    singleshot.click(fn=scope.singleshot, outputs=plot)
    btn_start.click(fn=lambda: scope.start_capture(cb=update_plot))
    btn_stop.click(fn=scope.stop_capture)

    app.launch(debug=True)


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)s]: %(message)s"
    )
    # asyncio.run(main())

    asyncio.run(main())
