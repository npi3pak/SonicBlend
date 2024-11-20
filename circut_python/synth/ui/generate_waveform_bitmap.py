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