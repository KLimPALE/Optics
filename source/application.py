import sys
import csv
import time
import os
from datetime import datetime

# Добавляем путь к библиотеке
current_dir = os.getcwd()
library_path = os.path.join(current_dir, "..", "library")
library_path = os.path.abspath(library_path)
sys.path.insert(0, library_path)

from chromator import Chromator
from oscilloscope import Oscilloscope


def main():
    print("=" * 60)
    print("СПЕКТРОСКОПИЧЕСКИЙ ЭКСПЕРИМЕНТ")
    print("=" * 60)
    
    # Пути к оборудованию
    sdk_path = os.path.join(current_dir, "..", "sdk")
    sdk_path = os.path.abspath(sdk_path)
    
    print("\n1. Подключение к монохроматору...")
    chromator = Chromator(sdk_path)
    if not chromator.connect():
        print("   Ошибка подключения монохроматора")
        return
    print(f"   Подключено: {chromator.get_instrument_name()}")
    print(f"   Серийный номер: {chromator.get_instrument_serial()}")
    
    print("\n2. Подключение к осциллографу...")
    oscilloscope = Oscilloscope()
    if not oscilloscope.connect():
        print("   Ошибка подключения осциллографа")
        chromator.disconnect()
        return
    print(f"   Подключено: {oscilloscope.identification()}")
    
    print("\n3. Параметры эксперимента...")
    
    start_wavelength = float(input("   Начальная длина волны (нм) [400]: ") or "400")
    end_wavelength = float(input("   Конечная длина волны (нм) [700]: ") or "700")
    step_wavelength = float(input("   Шаг длины волны (нм) [50]: ") or "50")
    slit_width = float(input("   Ширина входной щели (мкм) [100]: ") or "100")
    
    wavelengths = []
    current = start_wavelength
    while current <= end_wavelength + 0.001:
        wavelengths.append(current)
        current += step_wavelength
    
    print(f"\n   Диапазон: {start_wavelength} - {end_wavelength} нм")
    print(f"   Шаг: {step_wavelength} нм")
    print(f"   Количество точек: {len(wavelengths)}")
    print(f"   Ширина щели: {slit_width} мкм")
    
    print("\n4. Настройка оборудования...")
    
    print("   Установка ширины входной щели...")
    if chromator.set_slit_width(0, slit_width):
        print(f"     ✓ Щель установлена: {chromator.get_slit_width(0):.1f} мкм")
    else:
        print(f"     ✗ Ошибка: {chromator.get_last_error()}")
        oscilloscope.disconnect()
        chromator.disconnect()
        return
    
    print("   Настройка осциллографа...")
    oscilloscope.setup_for_experiment(channel_number=1, volts_per_division=1.0, seconds_per_division=0.01)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_folder = os.path.join(current_dir, f"experiment_{timestamp}")
    os.makedirs(experiment_folder, exist_ok=True)
    print(f"   Папка сохранения: {experiment_folder}")
    
    print("\n5. Запуск эксперимента...")
    
    results = []
    
    for index, wavelength in enumerate(wavelengths, 1):
        print(f"\n   --- Шаг {index}/{len(wavelengths)}: {wavelength:.1f} нм ---")
        
        print(f"     Установка длины волны...")
        if not chromator.set_wavelength(wavelength):
            print(f"       ✗ Ошибка: {chromator.get_last_error()}")
            continue
        
        time.sleep(0.3)
        
        print(f"     Захват сигнала...")
        time_values, voltage_values = oscilloscope.capture_waveform(channel_number=1, points_count=2000)
        
        if not time_values or not voltage_values:
            print(f"       ✗ Ошибка захвата сигнала")
            continue
        
        amplitude = max(voltage_values) - min(voltage_values)
        print(f"     Амплитуда: {amplitude:.3f} В")
        
        filename = f"signal_{wavelength:.1f}nm.csv"
        filepath = os.path.join(experiment_folder, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['TimeSeconds', 'VoltageVolts'])
            for tv, vv in zip(time_values, voltage_values):
                writer.writerow([f"{tv:.6f}", f"{vv:.6f}"])
        
        results.append({
            'wavelength_nm': wavelength,
            'amplitude_v': amplitude,
            'filename': filename
        })
    
    print("\n6. Сохранение результатов...")
    
    results_filename = os.path.join(experiment_folder, "results.csv")
    with open(results_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Wavelength_nm', 'Amplitude_V', 'Filename'])
        for result in results:
            writer.writerow([f"{result['wavelength_nm']:.2f}", f"{result['amplitude_v']:.6f}", result['filename']])
    
    print(f"   Сохранено: {results_filename}")
    
    print("\n7. Отключение оборудования...")
    oscilloscope.disconnect()
    chromator.disconnect()
    
    print("\n" + "=" * 60)
    print("ЭКСПЕРИМЕНТ ЗАВЕРШЕН")
    print(f"Результаты сохранены в: {experiment_folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()