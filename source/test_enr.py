import sys
import os
import time
from pathlib import Path

current_dir = os.getcwd()
library_path = os.path.join(current_dir, "..", "library")
library_path = os.path.abspath(library_path)

sys.path.insert(0, library_path)

from powermeter import Powermeter


def main():
    print("=" * 60)
    print("ТЕСТ ЭНЕРГОМЕТРА")
    print("=" * 60)
    
    print("\n1. Подключение к энергометру...")
    power_meter = Powermeter()
    
    if not power_meter.connect():
        print("   Ошибка подключения!")
        print("   Проверьте:")
        print("     1. Подключен ли энергометр по USB")
        print("     2. Установлены ли драйверы")
        return
    
    print("   ✓ Подключено успешно")
    print(f"   Порт: {power_meter.port_name}")
    
    print("\n2. Информация об устройстве...")
    version_string = power_meter.get_version()
    print(f"   Версия: {version_string}")
    
    status_string = power_meter.get_status()
    print(f"   Статус: {status_string}")
    
    print("\n3. Основные измерения...")
    print("   Одиночные измерения мощности:")
    
    power_values = []
    for measurement_index in range(10):
        power_value = power_meter.get_power()
        power_values.append(power_value)
        print(f"     {measurement_index + 1}: {power_value:.6f} Вт")
        time.sleep(0.2)
    
    print("\n   Статистика измерений:")
    min_power = min(power_values)
    max_power = max(power_values)
    avg_power = sum(power_values) / len(power_values)
    print(f"     Минимальная: {min_power:.6f} Вт")
    print(f"     Максимальная: {max_power:.6f} Вт")
    print(f"     Средняя: {avg_power:.6f} Вт")
    
    print("\n4. Измерения с усреднением:")
    average_power = power_meter.get_average_power(10, 0.05)
    print(f"   Средняя мощность (10 измерений): {average_power:.6f} Вт")
    
    print("\n5. Проверка дополнительных возможностей...")
    
    wavelength_value = power_meter.get_wavelength()
    if wavelength_value != 0:
        print(f"   Длина волны: {wavelength_value} нм")
    else:
        print("   Длина волны: не поддерживается")
    
    current_scale = power_meter.get_current_scale_index()
    if current_scale != 0:
        print(f"   Текущий масштаб: {current_scale}")
    else:
        print("   Масштаб: не поддерживается")
    
    autoscale_status = power_meter.get_autoscale()
    print(f"   Автомасштаб: {'Включен' if autoscale_status else 'Выключен'}")
    
    print("\n6. Отключение...")
    power_meter.disconnect()
    print("   ✓ Отключено")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()