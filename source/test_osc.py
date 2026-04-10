import sys
import csv
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "library"))

from oscilloscope import Oscilloscope


def main():
    oscilloscope = Oscilloscope()
    
    print("Подключение к осциллографу...")
    if not oscilloscope.connect():
        print("Не удалось подключиться к осциллографу")
        return
    
    print(f"Подключено: {oscilloscope.identification()}")
    
    print("Настройка и захват данных...")
    time_values, voltage_values = oscilloscope.capture_waveform(channel_number=1, points_count=2000)
    
    if not time_values or not voltage_values:
        print("Ошибка: не удалось получить данные")
        oscilloscope.disconnect()
        return
    
    print(f"Получено {len(time_values)} точек")
    print(f"Диапазон времени: {time_values[0]:.6f} - {time_values[-1]:.6f} с")
    print(f"Диапазон напряжения: {min(voltage_values):.3f} - {max(voltage_values):.3f} В")
    
    with open('oscilloscope_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['TimeSeconds', 'VoltageVolts'])
        
        for time_value, voltage_value in zip(time_values, voltage_values):
            csv_writer.writerow([f"{time_value:.6f}", f"{voltage_value:.6f}"])
    
    print("Данные сохранены в oscilloscope_data.csv")
    
    oscilloscope.disconnect()
    print("Отключено")


if __name__ == "__main__":
    main()