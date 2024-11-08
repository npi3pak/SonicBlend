import audiomixer
import displayio
import terminalio
import displayio, terminalio
from adafruit_display_text import label
from utils import *



class TestSynthEngine:
    title = ' Knob test '
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
        # self.init_menu()
        self.init_audio()


    def init_ui(self):

        self.ui['knob_a'] = label.Label(terminalio.FONT, text="", x=10, y=28)
        self.ui['knob_b'] = label.Label(terminalio.FONT, text="", x=69, y=28)
        self.ui['cv_in'] = label.Label(terminalio.FONT, text="", x=78, y=10)

        self.ui['button_state'] = label.Label(terminalio.FONT, text="", x=10, y=10)
        self.ui['enc_state'] = label.Label(terminalio.FONT, text="", x=30, y=10)


        for ui_item in self.ui.keys():
            self.group.append(self.ui[ui_item])

        self.update_ui()

    def init_audio(self):
        i2s = self.hardware.get_i2s();

        self.mixer = audiomixer.Mixer(voice_count=1, sample_rate=44100, channel_count=1,
                         bits_per_sample=16, samples_signed=True, buffer_size=32768)

        self.synth = synthio.Synthesizer(sample_rate=44100)
        i2s.play(self.mixer)
        self.mixer.voice[0].level = 0.2 # turn down the volume a bit since this can get loud
        self.mixer.voice[0].play(self.synth)

    def init_menu(self):
        self.ui['item_1'] = label.Label(terminalio.FONT, text="Menu 1", x=10, y=5)
        self.ui['item_2'] = label.Label(terminalio.FONT, text="Menu 2", x=10, y=15, background_color=0xffffff, color=0x000000)
        self.ui['item_3'] = label.Label(terminalio.FONT, text="Menu 3", x=10, y=25)

        # self.ui['item_1'] = label.Label(
        #     terminalio.FONT, 
        #     text="Menu 1", 
        #     x=10, 
        #     y=5,
        #     **({"background_color": 0xffffff, "color": 0x000000} if use_colors else {})
        # )

        for ui_item in self.ui.keys():
            self.group.append(self.ui[ui_item])

        self.update_ui()
        pass

    def show_menu(self):
        pass

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
        self.show_debug_hardware()
        self.display.refresh()
        # Обновление параметров на основе ввода
        pass

    def update_input(self):
        pass

    def get_synth(self):
        return self.synth
