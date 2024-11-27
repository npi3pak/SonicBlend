import audiomixer
import displayio
import terminalio
import displayio, terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import time
import synthio
from collections import namedtuple
from micropython import const
import ulab.numpy as np
from .utils import *
from ..ui.generate_waveform_bitmap import *
from ..ui.focus_manager import FocusManager
# from ..core.rotate_encoder import RotateEncoderHandler
from .audio_utils import *

WAVE_LIST = [sine(), saw_up(), saw_down(), triangle(), square()]

# Display the bitmap (example using displayio.TileGrid)
palette = displayio.Palette(2)
palette[0] = 0x000000  # Background color
palette[1] = 0xFFFFFF  # Wave color

# Константы делителя напряжения
R1 = 33000  # Сопротивление первого резистора, Ом
R2 = 10000  # Сопротивление второго резистора, Ом
divider_ratio = (R1 + R2) / R2

# Калибровочный коэффициент (установите после калибровки)
calibration_coefficient = 1.0  # Изначально 1.0, потом скорректируйте

def read_voltage(value):
    # Считываем значение с ADC (от 0 до 65535)
    print(value)
    raw_adc = value
    # Преобразуем в напряжение на выходе делителя
    v_out = (raw_adc / 65535) * 3.3  # 3.3V - опорное напряжение
    # Восстанавливаем исходное напряжение
    v_in = v_out * divider_ratio * calibration_coefficient
    return v_out, v_in

class MonoWaveSynthEngine:
    title = "Mono Wave"

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

        self.wave_index = 0
        self.wave = WAVE_LIST[self.wave_index]

        self.saw_pic = None

        self.focus_manager = FocusManager(self.hardware)

        self.init_ui()
        self.init_audio()

        # self.encoder_handler = RotateEncoderHandler(
        #     self.hardware, self.enc_a, self.enc_b
        # )

        self.val_a = 0
        self.val_b = 0

    def enc_a(self):
        new_index = self.wave_index + 1

        if new_index > len(WAVE_LIST) - 1:
            return

        self.wave_index = new_index
        self.set_wave(self.wave_index)

    def enc_b(self):
        new_index = self.wave_index - 1

        if new_index < 0:
            return

        self.wave_index = new_index
        self.set_wave(self.wave_index)

    def set_wave(self, index):
        self.wave = WAVE_LIST[index]
        self.note.waveform = self.wave

        self.update_wave_image()

        self.display.refresh()

    def update_wave_image(self):
        # Удаляем старое изображение
        if self.saw_pic in self.group:
            self.group.remove(self.saw_pic)
        # self.group.remove(self.saw_pic)

        # Генерируем новое изображение
        waveform_bitmap = generate_waveform_pixel_art(self.wave)
        self.saw_pic = displayio.TileGrid(
            waveform_bitmap, pixel_shader=palette, x=25, y=2
        )

        # Добавляем новое изображение в группу
        self.group.append(self.saw_pic)

        # Обновляем UI
        self.update_ui()

    def __del__(self):
        self.deinit_audio()

    def init_ui(self):
        self.update_wave_image()
        self.ui["cv_in"] = label.Label(terminalio.FONT, text="", x=5, y=15, scale=2)
        self.ui["cv_in"].hidden = True

        self.ui["test_a_focus"] = label.Label(terminalio.FONT, text=">", x=80, y=15, scale=1)
        self.ui["test_a"] = label.Label(terminalio.FONT, text="0", x=80, y=5, scale=1)
        self.ui["test_b"] = label.Label(terminalio.FONT, text="0", x=80, y=20, scale=1)
        self.ui["test_b_focus"] = label.Label(terminalio.FONT, text=">", x=110, y=15, scale=1)
        
        self.ui["test_a_focus"].hidden = True
        self.ui["test_b_focus"].hidden = True

        for ui_item in self.ui.keys():
            self.group.append(self.ui[ui_item])

        rect_base_width = 30
        rect_base_height = 25

        self.add_arrows(
            self.saw_pic.x, self.saw_pic.y, rect_base_width, rect_base_height
        )

        self.update_ui()

        self.focus_manager.add_focusable_object({
            'focus_handler': self.show_arrows,
            'blur_handler': self.hide_arrows,
            'enc_a_handler': self.enc_a,
            'enc_b_handler': self.enc_b,
        })

        # self.focus_manager.add_focusable_object({
        #     'focus_handler': self.focus(self.ui["test_a_focus"]),
        #     'blur_handler': self.blur(self.ui["test_a_focus"]),
        #     'enc_a_handler': self.inc1,
        #     'enc_b_handler': self.dec1,
        # })
            

        # self.focus_manager.add_focusable_object({
        #     'focus_handler': self.focus(self.ui["test_b_focus"]),
        #     'blur_handler': self.blur(self.ui["test_b_focus"]),
        #     'enc_a_handler': self.inc2,
        #     'enc_b_handler': self.dec2,
        # })


    def inc1(self):
        self.val_a += 1
        self.ui["test_a"].text = str(self.val_a)

    def dec1(self):
        self.val_a -= 1
        self.ui["test_a"].text = str(self.val_a)

    def inc2(self):
        self.val_b += 1
        self.ui["test_b"].text = str(self.val_b)

    def dec2(self):
        self.val_b -= 1
        self.ui["test_b"].text = str(self.val_b)

    def focus(self, element):
        def focus_handler():
            element.hidden = False
        
        return focus_handler
    
    def blur(self, element):
        def focus_handler():
            element.hidden = True
        
        return focus_handler

    def init_audio(self):
        i2s = self.hardware.get_i2s()

        self.mixer = audiomixer.Mixer(
            voice_count=1,
            sample_rate=44100 // 2,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=4096,
        )

        self.synth = synthio.Synthesizer(sample_rate=44100 // 2, waveform=self.wave)

        i2s.play(self.mixer)
        self.mixer.voice[0].level = (
            0.2  # turn down the volume a bit since this can get loud
        )
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

    def add_arrows(self, x, y, width, height):
        # Позиции для стрелок
        offset = 10
        
        left_arrow_x = x - offset  # Слева от объекта
        right_arrow_x = x + width + offset  # Справа от объекта
        arrow_y = y + height // 2  # Вертикально по центру объекта

        # Создаем текстовые метки для стрелок
        self.left_arrow = label.Label(
            font=terminalio.FONT,
            text="<",
            anchored_position=(left_arrow_x, arrow_y),
            anchor_point=(0, 0.5),
        )

        self.right_arrow = label.Label(
            font=terminalio.FONT,
            text=">",
            anchored_position=(right_arrow_x, arrow_y),
            anchor_point=(0, 0.5),
        )

        # Добавляем стрелки в группу
        self.group.append(self.left_arrow)
        self.group.append(self.right_arrow)

        self.hide_arrows()

    def hide_arrows(self):
        self.left_arrow.hidden = True
        self.right_arrow.hidden = True

    def show_arrows(self):
        self.left_arrow.hidden = False
        self.right_arrow.hidden = False


    def show_debug_hardware(self):
        knob1, knob2 = self.hardware.get_knobs()
        cv_in = self.hardware.get_cv_in()

        if self.hardware.get_encoder_button().value:  # Кнопка не нажата
            self.ui["button_state"].text = "[ ]"
        else:  # Кнопка нажата
            self.ui["button_state"].text = "[x]"

        position = self.hardware.get_encoder().position
        self.ui["enc_state"].text = "enc: " + str(position)

        self.ui["knob_a"].text = "fx_a: " + str(get_normalized_value(knob1))
        self.ui["knob_b"].text = "fx_b: " + str(get_normalized_value(knob2))

        # cv_in_label.text = "cv: " + str(get_voltage(cv_in))
        self.ui["cv_in"].text = "cv: " + str(get_hz_from_cv(cv_in))

    def update_ui(self):
        self.display.refresh()
        pass

    def update_input(self):
        # self.encoder_handler.update()
        self.focus_manager.update()

        cv_in = self.hardware.get_cv_in().value

        vin, vout = read_voltage(cv_in)

        self.ui["test_a"].text = str(vout)
        self.ui["test_a"].text = str(vin)


        knob1, knob2 = self.hardware.get_knobs()
        knob_value1 = get_normalized_value(knob1)
        knob_value2 = get_normalized_value(knob2)

        self.ui["cv_in"].text = str(knob_value1 + knob_value2)

        if self.note.frequency != knob_value1 + knob_value2:
            self.note.frequency = knob_value1 + knob_value2

        # note = synthio.Note(knob_value)
        # self.synth.press(note)
        # print(knob_value1)
        # self.synth.releaseAll()
        # self.synth.press(knob_value)
        pass

    def get_synth(self):
        return self.synth

    def knob1_callback(self):
        pass

    def knob2_callback(self):
        pass
