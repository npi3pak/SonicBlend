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
from .utils import *
from ..ui.generate_waveform_bitmap import *
from .audio_utils import *


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

        self.note = synthio.Note(400)

        self.init_ui()
        self.init_audio()

        self.wave = saw_up()

        



    def __del__(self):
        self.deinit_audio()

    def init_ui(self):
        # Parameters
        wave_size = 100
        wave_volume = 30000
        bitmap_width = 32
        bitmap_height = 32

        # Generate the waveform
        # sine_wave = synthio.SineWave(frequency=440)

        self.wave = sine(wave_size, wave_volume)
        # self.wave = saw_down(size=512)
        # self.wave = sine_wave

        # Create the bitmap
        waveform1 = saw_down(size=512)
        waveform_bitmap = generate_waveform_pixel_art(self.wave)

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

        self.mixer = audiomixer.Mixer(voice_count=1, sample_rate=44100//2, channel_count=1,
                         bits_per_sample=16, samples_signed=True, buffer_size=32768)

        self.synth = synthio.Synthesizer(sample_rate=44100//2, waveform=self.wave)
        # self.synth = synthio.Synthesizer(sample_rate=44100, voices=[self.wave])
        
        i2s.play(self.mixer)
        self.mixer.voice[0].level = 0.2 # turn down the volume a bit since this can get loud
        self.mixer.voice[0].play(self.synth)


        # note = synthio.Note(300)
        self.synth.press(self.note)
        # self.synth.press(62)

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
        self.display.refresh()
        pass

    def update_input(self):
        knob1, knob2 = self.hardware.get_knobs()
        knob_value1 = get_normalized_value(knob1)
        knob_value2 = get_normalized_value(knob2)

        if self.note.frequency != knob_value1 + knob_value2:
            self.note.frequency = knob_value1 + knob_value2
        # note = synthio.Note(knob_value)
        # self.synth.press(note)
        print(knob_value1)
        # self.synth.releaseAll()
        # self.synth.press(knob_value)
        pass

    def get_synth(self):
        return self.synth

    def knob1_callback(self):
        pass

    def knob2_callback(self):
        pass