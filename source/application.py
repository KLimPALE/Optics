# application.py
import sys
import time
import json
from datetime import datetime
from typing import Dict, Optional, List

from port_scanner import PortScanner
from laser_source import LaserSource
from chromator import Chromator
from oscilloscope import Oscilloscope
from powermeter import Powermeter


class ExperimentApp:
    """Консольное приложение для тестирования оборудования"""
    
    def __init__(self):
        self.scanner = PortScanner()
        
        self.laser: Optional[LaserSource] = None
        self.chromator: Optional[Chromator] = None
        self.oscilloscope: Optional[Oscilloscope] = None
        self.powermeter: Optional[Powermeter] = None
        
        self.device_status = {
            'laser': False,
            'chromator': False,
            'oscilloscope': False,
            'powermeter': False
        }
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        symbol = symbols.get(level, "📌")
        print(f"{symbol} [{timestamp}] {message}")
    
    def scan_and_connect(self):
        """Сканирование и подключение всех устройств"""
        self.log("=" * 50, "INFO")
        self.log("ПОИСК И ПОДКЛЮЧЕНИЕ УСТРОЙСТВ", "INFO")
        self.log("=" * 50, "INFO")
        
        devices = self.scanner.scan_all_devices()
        
        print("\n📋 НАЙДЕННЫЕ УСТРОЙСТВА:")
        print("-" * 40)
        for dev in devices:
            if dev['found']:
                status = "✅ НАЙДЕН"
                if dev.get('method') == 'com':
                    print(f"  {dev['name']}: {status} (порт: {dev['port']})")
                elif dev.get('is_laser_controller'):
                    ports = dev.get('connected_ports', [])
                    print(f"  {dev['name']}: {status} (порты: {ports})")
                else:
                    print(f"  {dev['name']}: {status}")
            else:
                print(f"  {dev['name']}: ❌ НЕ НАЙДЕН")
        print("-" * 40)
        
        # Подключение монохроматора
        self.log("\n📡 Подключение монохроматора...", "INFO")
        self.chromator = Chromator(sdk_path="../sdk")
        if self.chromator.connect():
            self.device_status['chromator'] = True
            self.log("Монохроматор подключен", "SUCCESS")
        else:
            self.log("Монохроматор не найден (проверьте питание и USB)", "ERROR")
        
        # Подключение осциллографа (с pyvisa-py)
        self.log("\n📺 Подключение осциллографа...", "INFO")
        try:
            self.oscilloscope = Oscilloscope()
            if self.oscilloscope.connect():
                idn = self.oscilloscope.idn()
                self.device_status['oscilloscope'] = True
                self.log(f"Осциллограф подключен: {idn[:60]}...", "SUCCESS")
                self.log(f"  └─ Ресурс: {self.oscilloscope.resource_string}", "INFO")
            else:
                self.log("Осциллограф не найден (проверьте USB и питание)", "ERROR")
        except Exception as e:
            self.log(f"Ошибка подключения осциллографа: {e}", "ERROR")
        
        # Подключение энергометра
        self.log("\n⚡ Подключение энергометра...", "INFO")
        energo_info = self.scanner.get_energometer_info()
        if energo_info['found'] and energo_info.get('port'):
            try:
                com_num = int(energo_info['port'].replace('COM', ''))
                self.powermeter = Powermeter()
                self.powermeter.connect(com_num)
                self.device_status['powermeter'] = True
                self.log(f"Энергометр подключен на {energo_info['port']}", "SUCCESS")
            except Exception as e:
                self.log(f"Ошибка подключения энергометра: {e}", "ERROR")
        else:
            self.log("Энергометр не найден", "ERROR")
        
        # Подключение лазера (используем второй порт - индекс 1)
        self.log("\n🔫 Подключение лазера...", "INFO")
        laser_info = self.scanner.get_laser_info()
        if laser_info['found']:
            connected_ports = laser_info.get('connected_ports', [])
            if len(connected_ports) >= 2:
                control_port = connected_ports[1]
                try:
                    self.laser = LaserSource()
                    self.laser.connect(control_port, baudrate=115200)
                    self.device_status['laser'] = True
                    self.log(f"Лазер подключен на {control_port} (порт управления)", "SUCCESS")
                except Exception as e:
                    self.log(f"Ошибка подключения лазера: {e}", "ERROR")
            elif len(connected_ports) >= 1:
                control_port = connected_ports[0]
                self.log(f"Предупреждение: используется первый порт {control_port}, но управление лазером обычно на втором", "WARNING")
                try:
                    self.laser = LaserSource()
                    self.laser.connect(control_port, baudrate=115200)
                    self.device_status['laser'] = True
                    self.log(f"Лазер подключен на {control_port}", "SUCCESS")
                except Exception as e:
                    self.log(f"Ошибка подключения лазера: {e}", "ERROR")
            else:
                self.log("Порты лазера не найдены", "ERROR")
        else:
            self.log("Лазер не найден", "ERROR")
        
        self.print_status()
    
    def print_status(self):
        """Вывод статуса подключения"""
        print("\n" + "=" * 50)
        print("СТАТУС ПОДКЛЮЧЕНИЯ")
        print("=" * 50)
        
        devices = [
            ('laser', '🔫 Лазер'),
            ('chromator', '📡 Монохроматор'),
            ('oscilloscope', '📺 Осциллограф'),
            ('powermeter', '⚡ Энергометр')
        ]
        
        for key, name in devices:
            status = self.device_status[key]
            icon = "✅" if status else "❌"
            print(f"{icon} {name}")
        
        print("=" * 50)
    
    def test_connections(self):
        """Тест связи с каждым устройством"""
        self.log("\n" + "=" * 50, "INFO")
        self.log("ТЕСТ СВЯЗИ С УСТРОЙСТВАМИ", "INFO")
        self.log("=" * 50, "INFO")
        
        results = {}
        
        # Тест монохроматора
        if self.device_status['chromator']:
            try:
                wl = self.chromator.get_wavelength()
                status = self.chromator.get_status()
                status_text = ["BUSY", "READY", "ERROR"][status] if status in [0,1,2] else "UNKNOWN"
                self.log(f"Монохроматор: длина волны = {wl:.1f} нм, статус = {status_text}", "SUCCESS")
                results['chromator'] = {'wavelength': wl, 'status': status}
            except Exception as e:
                self.log(f"Монохроматор: ОШИБКА - {e}", "ERROR")
                results['chromator'] = {'error': str(e)}
        
        # Тест осциллографа
        if self.device_status['oscilloscope']:
            try:
                idn = self.oscilloscope.idn()
                timebase = self.oscilloscope.get_timebase_scale()
                self.log(f"Осциллограф: {idn[:60]}...", "SUCCESS")
                self.log(f"  └─ Таймбаза: {timebase} с/дел", "INFO")
                results['oscilloscope'] = {'idn': idn, 'timebase': timebase}
            except Exception as e:
                self.log(f"Осциллограф: ОШИБКА - {e}", "ERROR")
                results['oscilloscope'] = {'error': str(e)}
        
        # Тест энергометра
        if self.device_status['powermeter']:
            try:
                wl = self.powermeter.get_wavelength()
                power = self.powermeter.get_power()
                self.log(f"Энергометр: длина волны = {wl:.0f} нм", "SUCCESS")
                self.log(f"  └─ Мощность: {power:.6f} Вт", "INFO")
                results['powermeter'] = {'wavelength': wl, 'power': power}
            except Exception as e:
                self.log(f"Энергометр: ОШИБКА - {e}", "ERROR")
                results['powermeter'] = {'error': str(e)}
        
        # Тест лазера
        if self.device_status['laser']:
            try:
                wl = self.laser.get_wavelength()
                self.log(f"Лазер: длина волны = {wl:.1f} нм", "SUCCESS")
                results['laser'] = {'wavelength': wl}
            except Exception as e:
                self.log(f"Лазер: ОШИБКА - {e}", "ERROR")
                results['laser'] = {'error': str(e)}
        
        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_connection_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"\nРезультаты сохранены в {filename}", "SUCCESS")
        return results
    
    def single_measurement(self, wavelength_nm: float = 1000):
        """Одиночное измерение"""
        if not self.device_status['oscilloscope']:
            self.log("Осциллограф не подключен!", "ERROR")
            return None
        
        self.log(f"\n🎯 ОДИНОЧНОЕ ИЗМЕРЕНИЕ на {wavelength_nm} нм", "INFO")
        print("-" * 40)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'target_wavelength': wavelength_nm
        }
        
        # Установка длины волны на лазере
        if self.device_status['laser']:
            try:
                self.laser.set_wavelength(wavelength_nm)
                time.sleep(0.3)
                actual_laser = self.laser.get_wavelength()
                self.log(f"Лазер: {actual_laser:.1f} нм", "INFO")
                result['laser_wavelength'] = actual_laser
            except Exception as e:
                self.log(f"Ошибка лазера: {e}", "ERROR")
        
        # Установка длины волны на монохроматоре
        if self.device_status['chromator']:
            try:
                self.chromator.set_wavelength(wavelength_nm)
                time.sleep(0.5)
                actual_mono = self.chromator.get_wavelength()
                self.log(f"Монохроматор: {actual_mono:.1f} нм", "INFO")
                result['monochromator_wavelength'] = actual_mono
            except Exception as e:
                self.log(f"Ошибка монохроматора: {e}", "ERROR")
        
        # Измерение энергии
        if self.device_status['powermeter']:
            try:
                self.powermeter.set_wavelength(int(wavelength_nm))
                time.sleep(0.1)
                energy = self.powermeter.get_average_energy(5)
                self.log(f"Энергия: {energy:.3f} мДж", "INFO")
                result['laser_energy_mj'] = energy
            except Exception as e:
                self.log(f"Ошибка энергометра: {e}", "ERROR")
        
        # Захват сигнала с осциллографа
        if self.device_status['oscilloscope']:
            try:
                self.log("Захват сигнала...", "INFO")
                if self.device_status['laser']:
                    self.laser.fire()
                time.sleep(0.1)
                
                time_axis, voltage_axis = self.oscilloscope.acquire_waveform(channel=1)
                
                if voltage_axis:
                    max_v = max(voltage_axis)
                    min_v = min(voltage_axis)
                    self.log(f"Сигнал: макс={max_v:.3f} В, мин={min_v:.3f} В", "SUCCESS")
                    result['signal_max_v'] = max_v
                    result['signal_min_v'] = min_v
                    result['signal_peak_to_peak'] = max_v - min_v
                    result['time_axis'] = time_axis[:100]
                    result['voltage_axis'] = voltage_axis[:100]
                else:
                    self.log("Сигнал не получен", "WARNING")
            except Exception as e:
                self.log(f"Ошибка осциллографа: {e}", "ERROR")
        
        # Сохранение
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"measure_{timestamp}_{wavelength_nm:.0f}nm.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        self.log(f"\nРезультат сохранен в {filename}", "SUCCESS")
        return result
    
    def run_menu(self):
        """Интерактивное меню"""
        while True:
            print("\n" + "=" * 50)
            print("ГЛАВНОЕ МЕНЮ")
            print("=" * 50)
            print("1. Тест подключения устройств")
            print("2. Одиночное измерение")
            print("3. Быстрое тестирование (все вместе)")
            print("4. Показать статус устройств")
            print("5. Выход")
            print("=" * 50)
            
            choice = input("Выберите действие (1-5): ").strip()
            
            if choice == '1':
                self.test_connections()
            
            elif choice == '2':
                try:
                    wl_input = input("Введите длину волны (нм) [1000]: ").strip()
                    wl = float(wl_input) if wl_input else 1000
                    self.single_measurement(wl)
                except ValueError:
                    self.log("Неверный формат числа", "ERROR")
            
            elif choice == '3':
                self.quick_test()
            
            elif choice == '4':
                self.print_status()
            
            elif choice == '5':
                self.log("Выход из программы", "INFO")
                break
            
            else:
                self.log("Неверный выбор", "WARNING")
    
    def quick_test(self):
        """Быстрое тестирование всех функций"""
        self.log("\n🚀 ЗАПУСК БЫСТРОГО ТЕСТА", "INFO")
        print("-" * 40)
        
        self.test_connections()
        
        if self.device_status['oscilloscope']:
            self.single_measurement(1000)
        
        self.log("\n✅ Быстрый тест завершен", "SUCCESS")


def main():
    print("\n" + "=" * 60)
    print("АВТОМАТИЗАЦИЯ ЭКСПЕРИМЕНТОВ ПО ИЗУЧЕНИЮ СИНГЛЕТНОГО КИСЛОРОДА")
    print("=" * 60)
    
    app = ExperimentApp()
    app.scan_and_connect()
    
    if any(app.device_status.values()):
        app.run_menu()
    else:
        print("\n❌ НЕ НАЙДЕНО НИ ОДНОГО УСТРОЙСТВА!")
        print("\nПроверьте:")
        print("  1. Все ли приборы включены в розетку")
        print("  2. Все ли USB кабели подключены")
        print("  3. Установлены ли драйверы для устройств")
        print("\nНажмите Enter для выхода...")
        input()


if __name__ == "__main__":
    main()