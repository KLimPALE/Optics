import sys
import os
import time
from pathlib import Path

current_dir = os.getcwd()
library_path = os.path.join(current_dir, "..", "library")
library_path = os.path.abspath(library_path)

sys.path.insert(0, library_path)

from laser_source import LaserSource


def main():
    print("=" * 60)
    print("ТЕСТ ЛАЗЕРА OPO 2350")
    print("=" * 60)
    
    print("\n1. Подключение к лазеру...")
    laser = LaserSource()
    
    if not laser.connect():
        print("   Ошибка подключения!")
        return
    
    print(f"   ✓ Подключено к {laser.port_name}")
    
    print("\n2. Информация об устройстве...")
    print(f"   Модель: {laser.get_model()}")
    
    print("\n3. Параметры моторов...")
    
    for motor in [1, 2]:
        print(f"\n   Мотор {motor}:")
        print(f"     Позиция: {laser.get_position(motor)}")
        print(f"     Статус: {laser.get_status(motor)}")
        print(f"     Скорость: {laser.get_speed(motor)} Гц")
    
    print("\n4. Управление моторами...")
    
    for motor in [1, 2]:
        print(f"\n   Мотор {motor}:")
        
        print("     Включение двигателя...")
        if laser.enable_motor(motor):
            print("       ✓ Двигатель включен")
        else:
            print("       ✗ Ошибка включения")
        
        print("     Перемещение на позицию 3000...")
        if laser.set_absolute_position(motor, 3000):
            print("       ✓ Команда отправлена")
        else:
            print("       ✗ Ошибка")
        
        time.sleep(1)
        
        print(f"     Текущая позиция: {laser.get_position(motor)}")
        
        print("     Выключение двигателя...")
        laser.disable_motor(motor)
        print("       ✓ Двигатель выключен")
    
    print("\n5. Управление затворами...")
    
    print("   Открытие затвора 1...")
    if laser.set_shutter(1, True):
        print("     ✓ Затвор 1 открыт")
    else:
        print("     ✗ Ошибка открытия")
    time.sleep(0.5)
    print(f"     Затвор 1: {'Открыт' if laser.get_shutter(1) else 'Закрыт'}")
    
    print("   Открытие затвора 2...")
    if laser.set_shutter(2, True):
        print("     ✓ Затвор 2 открыт")
    else:
        print("     ✗ Ошибка открытия")
    time.sleep(0.5)
    print(f"     Затвор 2: {'Открыт' if laser.get_shutter(2) else 'Закрыт'}")
    
    print("   Закрытие затвора 1...")
    laser.set_shutter(1, False)
    print(f"     Затвор 1: {'Открыт' if laser.get_shutter(1) else 'Закрыт'}")
    
    print("   Закрытие затвора 2...")
    laser.set_shutter(2, False)
    print(f"     Затвор 2: {'Открыт' if laser.get_shutter(2) else 'Закрыт'}")
    
    print("\n6. Управление длиной волны...")
    
    print("   Установка длины волны 500...")
    laser.set_wavelength(500)
    time.sleep(1)
    print(f"     Текущая длина волны: {laser.get_wavelength():.0f}")
    
    print("   Установка длины волны 600...")
    laser.set_wavelength(600)
    time.sleep(1)
    print(f"     Текущая длина волны: {laser.get_wavelength():.0f}")
    
    print("\n7. Отключение...")
    laser.disconnect()
    print("   ✓ Отключено")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()