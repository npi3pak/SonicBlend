import microcontroller
from utils import *
import asyncio
from hardware_module import Hardware
from test_synth_engine import TestSynthEngine
# from app_state import AppState

microcontroller.cpu.frequency = 250_000_000

hardware = Hardware()
test_synth = TestSynthEngine(hardware)

async def display_updater():
    # display
    # menu
    # dialog
    while True:
        test_synth.update_ui()
        await asyncio.sleep(0.1)

async def input_handler():
    # pass
    prev_note = 0
    synth = test_synth.get_synth()
    cv_in = hardware.get_cv_in()

    while True:
        hz = int(get_hz_from_cv(cv_in))
        note = hz_to_midi(hz)
        if note != prev_note:
            synth.release(prev_note)
            synth.press(note)
            prev_note = note

        
        await asyncio.sleep(0.1)

async def main():
    task1 = asyncio.create_task(display_updater())
    task2 = asyncio.create_task(input_handler())
    await asyncio.gather(task1, task2)

asyncio.run(main())
