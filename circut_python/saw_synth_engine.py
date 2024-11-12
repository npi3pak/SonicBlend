import audiomixer
import displayio
import terminalio
import displayio, terminalio
from adafruit_display_text import label
import time
import synthio
from collections import namedtuple
from micropython import const
import ulab.numpy as np
from utils import *

def sine(size, volume):
    return np.array(np.sin(np.linspace(0, 2*np.pi, size, endpoint=False)) * volume, dtype=np.int16)

def square(size, volume):
    return np.concatenate((np.ones(size//2, dtype=np.int16) * volume,
                            np.ones(size//2, dtype=np.int16) * -volume))

def triangle(size, min_vol, max_vol):
    return np.concatenate((np.linspace(min_vol, max_vol, num=size//2, dtype=np.int16),
                            np.linspace(max_vol, min_vol, num=size//2, dtype=np.int16)))

def saw_down(size, volume):
    return np.linspace(volume, -volume, num=size, dtype=np.int16)

def saw_up(size, volume):
    return np.linspace(-volume, volume, num=size, dtype=np.int16)

def generate_waveform_bitmap(wave, width, height):
    """
    Generate a bitmap from the waveform for displayio.

    Args:
        wave (np.array): The waveform array (e.g., from saw_down).
        width (int): The width of the bitmap.
        height (int): The height of the bitmap.

    Returns:
        displayio.Bitmap: Bitmap containing the waveform.
    """
    # Normalize wave to fit within the display height
    min_val = wave.min()
    max_val = wave.max()
    normalized_wave = ((wave - min_val) / (max_val - min_val)) * (height - 1)

    # Create an empty bitmap
    bitmap = displayio.Bitmap(width, height, 2)  # 2 colors: 0 (background), 1 (wave)

    # Draw the waveform onto the bitmap
    for x in range(width):
        y = int(normalized_wave[int(x / width * len(wave))])  # Scale wave to bitmap width
        bitmap[x, height - 1 - y] = 1  # Invert y to match displayio's top-left origin

    return bitmap


class SawSynthEngine:
    title = 'Saw'

    def __init__(self, hardware):
        self.hardware = hardware
        self.parameters = {}
        self.ui = {}
        self.mixer = None
        self.synth = None

        self.display = self.hardware.get_display()

        self.group = displayio.Group()
        self.display.root_group = self.group
        self.display.auto_refresh = False

        self.init_ui()
        self.init_audio()


    def __del__(self):
        self.deinit_audio()

    def init_ui(self):
        # Parameters
        wave_size = 100
        wave_volume = 30000
        bitmap_width = 32
        bitmap_height = 32

        # Generate the waveform
        wave = saw_down(wave_size, wave_volume)

        # Create the bitmap
        waveform_bitmap = generate_waveform_bitmap(wave, bitmap_width, bitmap_height)

        # Display the bitmap (example using displayio.TileGrid)
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Background color
        palette[1] = 0xFFFFFF  # Wave color

        tile_grid = displayio.TileGrid(waveform_bitmap, pixel_shader=palette)

        self.ui['cv_in'] = label.Label(terminalio.FONT, text="", x=78, y=10)

        for ui_item in self.ui.keys():
            self.group.append(self.ui[ui_item])

        self.group.append(tile_grid)
        self.update_ui()

    def init_audio(self):
        i2s = self.hardware.get_i2s();

        self.mixer = audiomixer.Mixer(voice_count=1, sample_rate=44100, channel_count=1,
                         bits_per_sample=16, samples_signed=True, buffer_size=32768)

        self.synth = synthio.Synthesizer(sample_rate=44100)
        i2s.play(self.mixer)
        self.mixer.voice[0].level = 0.2 # turn down the volume a bit since this can get loud
        self.mixer.voice[0].play(self.synth)

    def deinit_audio(self):
        if self.mixer:
            for voice in self.mixer.voice:
                voice.stop()  # Stop any active voices
            self.mixer.deinit()  # Deinitialize the mixer
            self.mixer = None  # Remove reference to the mixer
        
        if self.synth:
            self.synth = None  # Clear reference to the synthesizer

        i2s = self.hardware.get_i2s()

        if i2s:
            i2s.stop()

    def show_debug_hardware(self):
        knob1, knob2 = self.hardware.get_knobs()
        cv_in = self.hardware.get_cv_in()

        if self.hardware.get_encoder_button().value:  # Кнопка не нажата
            self.ui['button_state'].text = "[ ]"
        else:  # Кнопка нажата
            self.ui['button_state'].text = "[x]"

        position = self.hardware.get_encoder().position
        self.ui['enc_state'].text = "enc: "+ str(position)

        self.ui['knob_a'].text = "fx_a: " + str(get_normalized_value(knob1))
        self.ui['knob_b'].text = "fx_b: " + str(get_normalized_value(knob2))

        # cv_in_label.text = "cv: " + str(get_voltage(cv_in))
        self.ui['cv_in'].text = "cv: " + str(get_hz_from_cv(cv_in))

    def update_ui(self):
        # self.show_debug_hardware()
        self.display.refresh()
        pass

    def update_input(self):
        pass

    def get_synth(self):
        return self.synth
