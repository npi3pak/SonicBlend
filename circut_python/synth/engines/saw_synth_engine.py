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

# size=512, volume=30000
def sine(size=512, volume=30000):
    return np.array(np.sin(np.linspace(0, 2*np.pi, size, endpoint=False)) * volume, dtype=np.int16)

def square(size=512, volume=30000):
    return np.concatenate((np.ones(size//2, dtype=np.int16) * volume,
                            np.ones(size//2, dtype=np.int16) * -volume))

def triangle(size=512, min_vol=0, max_vol=30000):
    return np.concatenate((np.linspace(min_vol, max_vol, num=size//2, dtype=np.int16),
                            np.linspace(max_vol, min_vol, num=size//2, dtype=np.int16)))

def saw_down(size=512, volume=30000):
    return np.linspace(volume, -volume, num=size, dtype=np.int16)

def saw_up(size=512, volume=30000):
    return np.linspace(-volume, volume, num=size, dtype=np.int16)

def generate_waveform_bitmap_ofy(waveform, width=32, height=32, offset_x=0):
    """
    Генерирует bitmap для отображения волны на дисплее.

    :param waveform: Массив значений волны (numpy.array)
    :param width: Ширина дисплея
    :param height: Высота дисплея
    :param offset_x: Смещение по оси X
    :param offset_y: Смещение по оси Y
    :return: Bitmap, содержащий изображение волны
    """

    offset_y = int(height/2)
    # Нормализуем значения волны к высоте экрана
    max_val = np.max(waveform)
    min_val = np.min(waveform)
    
    if max_val == min_val:
        raise ValueError("Все значения в waveform одинаковы, нормализация невозможна.")
    
    # Центрируем волну по вертикали
    # normalized_waveform = ((waveform - min_val) / (max_val - min_val)) * (height - 1) - (height - 1) / 2
    normalized_waveform = ((waveform - min_val) / (max_val - min_val)) * (height - 1)
    
    
    # Применяем offset_y
    normalized_waveform += offset_y
    
    # Создаем пустой bitmap
    bitmap = displayio.Bitmap(width, height, 2)  # 2 цвета: черный и белый
    
    # Масштабируем волну на ширину экрана
    interpolated_waveform = np.interp(
        np.linspace(0, len(waveform) - 1, width - offset_x),  # Новые точки
        np.arange(len(waveform)),                            # Исходные индексы
        normalized_waveform                                  # Исходные значения
    )
    
    # Заполняем bitmap
    for x in range(width):
        index = x - offset_x  # Учитываем offset_x
        if index >= len(interpolated_waveform):
            break
        y = int(interpolated_waveform[index])
        
        # Ограничиваем y в пределах экрана
        if 0 <= y < height:
            if y>=offset_y:
                y -= offset_y
            else:
                y += offset_y
            # if y<=offset_y:
            #     y += 16
            bitmap[x, height - 1 - y] = 1  # Цвет 1 - белый

    return bitmap



def generate_waveform_bitmap(waveform, width=128, height=32):
    """
    Генерирует bitmap для отображения волны на дисплее.

    :param waveform: Массив значений волны (numpy.array)
    :param width: Ширина дисплея
    :param height: Высота дисплея
    :return: Bitmap, содержащий изображение волны
    """
    # Нормализуем значения волны к высоте экрана
    max_val = np.max(waveform)
    min_val = np.min(waveform)
    
    # Центрируем волну по вертикали
    normalized_waveform = ((waveform - min_val) / (max_val - min_val)) * (height - 1)
    
    # Инвертируем ось Y для отображения сверху вниз
    normalized_waveform = height - 1 - normalized_waveform
    
    # Создаем пустой bitmap
    bitmap = displayio.Bitmap(width, height, 2)  # 2 цвета: черный и белый
    
    # print(normalized_waveform)
    # test = []
    # Заполняем bitmap
    for x in range(width):
        # Вычисляем индекс в массиве волны
        index = int((x / width) * len(waveform))
        y = int(normalized_waveform[index])
        # print(y, 'y')
        
        # Ограничиваем y в пределах 0 и height - 1
        y = max(0, min(height - 1, y))
        # Рисуем точку на экране
        bitmap[x, y] = 1  # Цвет 1 - белый
        # test.append([x, y])
    # print(test)
    return bitmap


def generate_waveform_bitmap_smoothed(waveform, width=128, height=32, thickness=1):
    """
    Генерирует bitmap для отображения волны на дисплее с интерполяцией и утолщением линий.
    
    :param waveform: Массив значений волны (numpy.array)
    :param width: Ширина дисплея
    :param height: Высота дисплея
    :param thickness: Толщина линии в пикселях
    :return: Bitmap, содержащий изображение волны
    """

    offset_y = int(height/2)
    # Нормализуем значения волны к высоте экрана
    max_val = np.max(waveform)
    min_val = np.min(waveform)
    normalized_waveform = ((waveform - min_val) / (max_val - min_val)) * (height - 1)
    normalized_waveform += offset_y
    
    # Увеличиваем количество точек через линейную интерполяцию
    interpolated_waveform = np.interp(
        np.linspace(0, len(waveform) - 1, width),  # Новые точки для интерполяции
        np.arange(len(waveform)),                 # Исходные индексы
        normalized_waveform                       # Исходные значения
    )
    
    # Создаем пустой bitmap
    bitmap = displayio.Bitmap(width, height, 2)  # 2 цвета: черный и белый
    
    # Заполняем bitmap
    for x in range(width):
        y = int(interpolated_waveform[x])
        
        # Ограничиваем y в пределах 0 и height - 1
        y = max(0, min(height - 1, y))

        if 0 <= y < height:
            if y>=offset_y:
                y -= offset_y
            else:
                y += offset_y
        
        # Рисуем "жирную" линию с интерполяцией
        for t in range(-thickness // 2, thickness // 2 + 1):
            if 0 <= y + t < height:
                # bitmap[x, height - 1 - (y + t)] = 1  # Цвет 1 - белый
                bitmap[x, height - 1 - (y + t)] = 1  # Цвет 1 - белый
                
    return bitmap

def generate_waveform_pixel_art(waveform, width=30, height=25, pixel_size=2, gap=1, offset_x=0):
    """
    Генерирует bitmap для отображения волны в стиле пиксель-арт с учётом реального дисплея.
    
    :param waveform: Массив значений волны (numpy.array)
    :param width: Ширина дисплея
    :param height: Высота дисплея
    :param pixel_size: Размер "пикселя" в прямоугольниках
    :param gap: Отступ между "пикселями"
    :param offset_x: Смещение изображения по оси X
    :param offset_y: Смещение изображения по оси Y
    :return: Bitmap, содержащий изображение волны
    """

    offset_y = int(height/2)
    # Нормализуем значения волны к высоте экрана
    max_val = np.max(waveform)
    min_val = np.min(waveform)
    
    # Масштабируем значения к диапазону 0...height с учётом offset_y
    normalized_waveform = ((waveform - min_val) / (max_val - min_val)) * (height - 1)
    normalized_waveform = normalized_waveform + offset_y
    
    # Ограничиваем значения в пределах экрана
    normalized_waveform = np.clip(normalized_waveform, 0, height - 1)
    
    # Создаем пустой bitmap
    bitmap = displayio.Bitmap(width, height, 2)  # 2 цвета: черный и белый
    
    # Увеличиваем количество точек через интерполяцию
    interpolated_waveform = np.interp(
        np.linspace(0, len(waveform) - 1, (width - offset_x) // (pixel_size + gap)),  # Новые точки
        np.arange(len(waveform)),                                                    # Исходные индексы
        normalized_waveform                                                          # Исходные значения
    )
    
    # Рисуем пиксель-арт
    for x in range(0, width - offset_x, pixel_size + gap):
        pixel_index = x // (pixel_size + gap)
        if pixel_index >= len(interpolated_waveform):
            break
        y = int(interpolated_waveform[pixel_index])

        if 0 <= y < height:
            if y>=offset_y:
                y -= offset_y
            else:
                y += offset_y
        
        # Ограничиваем y в пределах 0 и height - 1
        if y < 0 or y >= height:
            continue  # Пропускаем пиксели вне экрана
        
        # Заполняем прямоугольник "пикселя"
        for px in range(pixel_size):
            for py in range(pixel_size):
                if 0 <= x + px + offset_x < width and 0 <= y - py < height:
                    bitmap[x + px + offset_x, height - 1 - (y - py)] = 1  # Цвет 1 - белый
                    
    return bitmap

# waveform1 = sine(size=512, volume=30000)  # Пример: синусоида
# waveform_bitmap = generate_waveform_bitmap(waveform1)

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
        self.wave = sine(wave_size, wave_volume)

        # Create the bitmap
        waveform1 = saw_down(size=512)  # Пример: синусоида
        # waveform_bitmap = generate_waveform_bitmap_ofy(waveform1)
        # waveform_bitmap = generate_waveform_bitmap_smoothed(waveform1)
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

        self.mixer = audiomixer.Mixer(voice_count=1, sample_rate=44100, channel_count=1,
                         bits_per_sample=16, samples_signed=True, buffer_size=32768)

        # saw_wave = saw_down()
        # saw_wave = saw_up()
        

        # wave_saw = np.linspace(30000,-30000, num=512, dtype=np.int16)
        self.synth = synthio.Synthesizer(sample_rate=44100, waveform=self.wave)
        
        i2s.play(self.mixer)
        self.mixer.voice[0].level = 0.2 # turn down the volume a bit since this can get loud
        self.mixer.voice[0].play(self.synth)

        self.synth.press(62)

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
