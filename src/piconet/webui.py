from .pico_device import Ps2000Device
import qcontrol4.gui.web.widgets as qw
import asyncio
import matplotlib.pyplot as plt


async def capture_coro(plot):
    time = 0
    voltage = 0
    with Ps2000Device() as sc:
        sc.ch_A_range = 0.1
        sc.set_channel("A")
        sc.set_trigger()
        sc.get_timebase()
        while True:
            data = await sc.acquire_data_coro()
            fig, ax = plt.subplots(figsize=(1000 / 72, 400 / 72))
            ax.plot(*data)
            plot.value = fig


async def main():
    plt.style.use("dark_background")
    with qw.Blocks() as app:
        plot = qw.Plot()

    await asyncio.gather(app.launch_task(), capture_coro(plot))


if __name__ == "__main__":
    asyncio.run(main())
