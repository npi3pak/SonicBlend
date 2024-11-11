import microcontroller
from utils import *
import asyncio
from hardware_module import Hardware
from test_synth_engine import TestSynthEngine
from app_state import AppState
import time
microcontroller.cpu.frequency = 250_000_000


hardware = Hardware()
# test_synth = TestSynthEngine(hardware)
app = AppState(hardware, [TestSynthEngine])

async def display_updater():
    # display
    # menu
    # dialog
    while True:
        app.update_ui()
        await asyncio.sleep(0.001)

async def input_handler():
    # pass
    # prev_note = 0
    # synth = test_synth.get_synth()
    # cv_in = hardware.get_cv_in()

    while True:
        # move inside of the engine

        # hz = int(get_hz_from_cv(cv_in))
        # note = hz_to_midi(hz)
        # if note != prev_note:
        #     synth.release(prev_note)
        #     synth.press(note)
        #     prev_note = note

        app.update_input()
        await asyncio.sleep(0.001)

# async def main():
#     task1 = asyncio.create_task(display_updater())
#     task2 = asyncio.create_task(input_handler())
#     await asyncio.gather(task1, task2)

# asyncio.run(main())



while True:
    app.update_ui()
    app.update_input()
    # time.sleep(0.0001)
