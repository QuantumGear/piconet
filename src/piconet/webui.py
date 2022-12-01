from .pico_device import Ps2000Device
import qcontrol4.gui.web.widgets as qw
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import logging
import sys


class Osci:
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
                print("time")
                print(data[0][:10])
                print("volatge")
                print(data[1][:10])
                self._capture_cb(fig)

            # await asyncio.sleep(0.01)
            # if self._capture_cb:
            #     x = np.linspace(0, 5, 20)
            #     y = x**2 + np.random.normal(0, 0.5, 20)
            #     fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
            #     ax.plot(x, y)
            #     self._capture_cb(fig)

    def oneshot(self):
        print("test")
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


def main():
    plt.style.use("dark_background")
    scope = Osci()
    with qw.Blocks() as app:
        with qw.Row():
            plot = qw.Plot()
            with qw.Column():
                vrange = qw.Radio(
                    label="Voltage range", value="0.1", choices=["0.1", "1", "10"]
                )
        with qw.Row():
            oneshot = qw.Button("One shot")
        with qw.Row():
            btn_start = qw.Button("Start")
            btn_stop = qw.Button("Stop")

    def update_plot(data):
        plot.value = data

    oneshot.click(fn=scope.oneshot, outputs=plot)
    btn_start.click(fn=lambda: scope.start_capture(cb=update_plot))
    btn_stop.click(fn=scope.stop_capture)

    app.launch(debug=True)


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)s]: %(message)s"
    )
    # asyncio.run(main())

    asyncio.run(main())
