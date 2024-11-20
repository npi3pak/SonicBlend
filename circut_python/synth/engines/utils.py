import audiocore
import array
import math
import synthio

adc_to_voct = lambda value: max(0, min(12, (value / 2.79) * 12))


# Константы для работы с частотой и напряжением
MAX_ADC_VALUE = 65535  # максимальное значение АЦП (16-битный результат)
MAX_VOLTAGE = 3.3      # максимальное опорное напряжение АЦП
INPUT_MAX_VOLTAGE = 12 # максимальное входное напряжение после делителя
BASE_FREQUENCY = 32.703 # Частота ноты C1 в Гц для 1 В
BASE_FREQUENCY_C0 = 16.35
# DIVIDER_RATIO = 0.2326
DIVIDER_RATIO = 0.9326

def map_range(s, a1, a2, b1, b2):
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def get_normalized_value(pin):
    return int(pin.value / 65535 * 127)


def get_voltage(pin, round_factor=4):
    # I use 33k and 10k divider on ADC, max V = 2.79V
    # mapped = map_range(pin.value, 0, 65535, 0.0, 2.79)
    mapped = map_range(pin.value, 0, 65535, 0.0, 3.3)
    return mapped

def voltage_to_frequency(voltage_adc):
    # Преобразуем входное напряжение (0–3.3 В) в диапазон от 0 до 12 В
        # Пересчитываем значение с АЦП в исходное напряжение до делителя
    input_voltage = voltage_adc / DIVIDER_RATIO
    
    # Рассчитываем частоту: каждые 1 В увеличивают частоту вдвое (на октаву)
    frequency = BASE_FREQUENCY_C0 * (2 ** input_voltage)
    return frequency

def hz_to_midi(frequency):
    if frequency <= 0:
        return 0
    midi_note = 69 + 12 * (math.log(frequency / 440.0) / math.log(2))
    return round(midi_note)  # Rounding to the nearest whole number

def get_hz_from_cv(pin):
    MAX_VOLTAGE = 5
    MAX_ADC = 2.79
    ERROR_SHIFT = 0.3

    input_voltage = round(get_voltage(pin), 3)
    
    fake_voct = 0
    if input_voltage < 0:
        fake_voct = 0
    else:
        fake_voct = (input_voltage / 2.79) * 12
    #     fake_voct = ((MAX_VOLTAGE / MAX_ADC) * input_voltage)
    #     # 4.3010752688

    print('iv', input_voltage)
    print('fv', fake_voct)
    print(synthio.voct_to_hz(round(fake_voct, 2)))

    return round(synthio.voct_to_hz(fake_voct))
    # return fake_voct

    # input_voltage = (pin.value / MAX_ADC_VALUE) * 3.3

    # vf = voltage_to_frequency(input_voltage)
    # print(vf)
    # # print("V", input_voltage, " F", vf, "Hz")

    # return vf

def file_to_play():
    f = open("cw_amen_oldskool.wav", "rb")
    return audiocore.WaveFile(f)


def sin_wave(frequency, sample_rate=44100):
    # Количество семплов для одного периода
    period_length = int(sample_rate / frequency)

    # Создание массива для одного периода синусоидального сигнала
    sine_wave = array.array("H", [0] * period_length)

    # Заполнение массива значениями одного периода синусоиды
    for i in range(period_length):
        # Синусоидальное значение для текущего семпла
        sine_wave[i] = int(
            math.sin(2 * math.pi * i / period_length) * (2**15 - 1) + 2**15
        )

    return audiocore.RawSample(sine_wave, sample_rate=44100)


# sine_wave = sin_wave(500)
