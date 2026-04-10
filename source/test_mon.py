import sys
import os
import time
from pathlib import Path

# Получаем текущую рабочую директорию
current_dir = os.getcwd()
library_path = os.path.join(current_dir, "..", "library")
library_path = os.path.abspath(library_path)

sys.path.insert(0, library_path)

from chromator import Chromator


def main():
    print("Подключение к монохроматору...")
    
    sdk_path = os.path.join(current_dir, "..", "sdk")
    sdk_path = os.path.abspath(sdk_path)
    
    chromator = Chromator(sdk_path)
    
    if not chromator.connect():
        print("Ошибка подключения к монохроматору")
        if chromator.get_last_error():
            print(f"Ошибка: {chromator.get_last_error()}")
        return
    
    print(f"Подключено: {chromator.get_instrument_name()}")
    print(f"Серийный номер: {chromator.get_instrument_serial()}")
    
    print(f"\nКоличество решеток: {chromator.get_grating_count()}")
    for i in range(chromator.get_grating_count()):
        grooves, min_wl, max_wl, blaze = chromator.get_grating_parameters(i)
        print(f"  Решетка {i}: {grooves} шт/мм, {min_wl:.0f}-{max_wl:.0f} нм")
    
    print(f"\nТекущая длина волны: {chromator.get_wavelength():.2f} нм")
    
    test_wavelength = 550.0
    print(f"\nУстановка длины волны {test_wavelength} нм...")
    if chromator.set_wavelength(test_wavelength):
        time.sleep(0.5)
        print(f"  Установлено: {chromator.get_wavelength():.2f} нм")
    
    print(f"\nШирина входной щели: {chromator.get_slit_width(0):.1f} мкм")
    
    chromator.disconnect()
    print("\nОтключено")


if __name__ == "__main__":
    main()