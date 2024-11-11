#!/bin/bash

# Указываем директорию с подключенной платой (замените 'CIRCUITPY' при необходимости)
MOUNT_POINT="/Volumes/CIRCUITPY"

# Проверяем, смонтирована ли плата
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Ошибка: Плата CircuitPython не найдена. Проверьте подключение."
    exit 1
fi

# Копируем все .py файлы с платы в текущую директорию
cp "$MOUNT_POINT"/*.py .

echo "Файлы .py успешно скопированы из $MOUNT_POINT в текущую директорию."
