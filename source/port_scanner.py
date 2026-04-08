"""
port_scanner.py - модуль для поиска и мониторинга USB-устройств
"""

import serial.tools.list_ports
import subprocess
import re
from typing import Dict, List, Optional, Tuple


class PortScanner:
    """Класс для сканирования и поиска устройств по VID/PID"""

    # Предопределенные устройства
    DEVICES = [
        (0x0403, 0x6001, "Энергометр (базовый)"),
        (0x0403, 0x6001, "Энергометр (виртуальный)"),
        (0x0403, 0x6011, "Лазер (контроллер)"),  # НОВЫЙ ЛАЗЕР - FT4232H
        (0x0957, 0x1796, "Осциллограф"),
        (0x0547, 0x1005, "Монохроматор")
    ]

    # Специальная обработка для лазера (4 порта)
    LASER_VID = 0x0403
    LASER_PID = 0x6011
    LASER_PORT_SUFFIXES = ['01', '02', '03', '04']  # Суффиксы портов
    
    # Назначение портов лазера (если известно)
    LASER_PORT_FUNCTIONS = {
        '01': 'Управление моторами',
        '02': 'Управление лазером',
        '03': 'Датчики/обратная связь',
        '04': 'Дополнительный порт'
    }

    def __init__(self):
        """Инициализация сканера портов"""
        self.last_known_devices = {}

    def get_laser_ports_info(self) -> Dict:
        """
        Специальный метод для получения информации о всех 4 портах лазера
        
        Returns:
            Словарь с информацией о всех портах лазера
        """
        result = {
            "found": False,
            "ports": [],
            "connected_ports": [],
            "device_name": "Лазер (контроллер)",
            "vid": self.LASER_VID,
            "pid": self.LASER_PID
        }
        
        com_ports = serial.tools.list_ports.comports()
        
        for port in com_ports:
            if port.vid == self.LASER_VID and port.pid == self.LASER_PID:
                result["found"] = True
                
                # Определяем суффикс порта
                port_name = port.device  # например, COM5
                suffix = None
                
                # Пытаемся определить суффикс из описания или номера порта
                if port.serial_number:
                    # Обычно у FT4232H серийный номер содержит суффикс
                    match = re.search(r'([0-9A-F]{2})$', port.serial_number)
                    if match:
                        suffix = match.group(1)
                
                port_info = {
                    "port": port_name,
                    "description": port.description,
                    "serial_number": port.serial_number,
                    "suffix": suffix,
                    "function": self.LASER_PORT_FUNCTIONS.get(suffix, "Неизвестная функция"),
                    "hardware_id": port.hwid,
                    "vid": port.vid,
                    "pid": port.pid
                }
                
                result["ports"].append(port_info)
                result["connected_ports"].append(port_name)
        
        return result

    def get_device_info(self, vid: int, pid: int, device_name: str = None) -> Dict:
        """
        Универсальная функция для получения информации об устройстве.

        Args:
            vid: Vendor ID (например, 0x0403)
            pid: Product ID (например, 0x6001)
            device_name: Название устройства (опционально)

        Returns:
            Словарь с полями
        """
        # Специальная обработка для лазера (4 порта)
        if vid == self.LASER_VID and pid == self.LASER_PID:
            laser_info = self.get_laser_ports_info()
            if laser_info["found"]:
                return {
                    "found": True,
                    "method": "com_multi",
                    "ports": laser_info["ports"],
                    "connected_ports": laser_info["connected_ports"],
                    "port_count": len(laser_info["ports"]),
                    "port": laser_info["ports"][0]["port"] if laser_info["ports"] else None,
                    "description": f"FTDI FT4232H - 4-портовый контроллер лазера",
                    "serial": laser_info["ports"][0]["serial_number"] if laser_info["ports"] else None,
                    "friendly_name": "Лазерный контроллер (4 порта)",
                    "status": "OK" if len(laser_info["ports"]) == 4 else "Partial",
                    "status_message": f"✅ Найдено {len(laser_info['ports'])} из 4 портов",
                    "instance_id": None,
                    "name": device_name or "Лазер (контроллер)",
                    "vid": vid,
                    "pid": pid,
                    "has_driver": True,
                    "is_working": len(laser_info["ports"]) == 4,
                    "is_laser_controller": True
                }
            else:
                return {
                    "found": False,
                    "method": None,
                    "port": None,
                    "description": None,
                    "serial": None,
                    "friendly_name": None,
                    "status": None,
                    "status_message": "❌ Контроллер лазера не найден",
                    "instance_id": None,
                    "name": device_name or "Лазер (контроллер)",
                    "vid": vid,
                    "pid": pid,
                    "has_driver": False,
                    "is_working": False,
                    "is_laser_controller": True,
                    "ports": []
                }

        # Обычная обработка для других устройств (COM-порты)
        com_ports = serial.tools.list_ports.comports()
        for port in com_ports:
            if port.vid == vid and port.pid == pid:
                return {
                    "found": True,
                    "method": "com",
                    "port": port.device,
                    "description": port.description,
                    "serial": port.serial_number,
                    "friendly_name": None,
                    "status": "OK",
                    "status_message": "✅ Работает (COM-порт)",
                    "instance_id": None,
                    "name": device_name,
                    "vid": vid,
                    "pid": pid,
                    "has_driver": True,
                    "is_working": True
                }

        # Если не COM-порт, используем PowerShell
        hw_filter = f"VID_{vid:04X}&PID_{pid:04X}"
        try:
            ps_command = f"""
            $device = Get-PnpDevice -PresentOnly | Where-Object {{ $_.HardwareId -like '*{hw_filter}*' }}
            if ($device) {{
                $status = $device.Status
                $friendly = $device.FriendlyName
                $instance = $device.InstanceId
                [PSCustomObject]@{{
                    FriendlyName = $friendly
                    Status = $status
                    InstanceId = $instance
                }} | ConvertTo-Csv -NoTypeInformation
            }}
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split(',')
                    if len(parts) >= 3:
                        friendly = parts[0].strip('"')
                        status = parts[1].strip('"')
                        instance = parts[2].strip('"')
                        
                        return {
                            "found": True,
                            "method": "pnp",
                            "port": None,
                            "description": None,
                            "serial": None,
                            "friendly_name": friendly,
                            "status": status,
                            "status_message": "✅ Устройство найдено" if status == "OK" else f"⚠️ Статус: {status}",
                            "instance_id": instance,
                            "name": device_name,
                            "vid": vid,
                            "pid": pid,
                            "has_driver": True,
                            "is_working": status == "OK"
                        }
        except Exception:
            pass

        # Не найдено
        return {
            "found": False,
            "method": None,
            "port": None,
            "description": None,
            "serial": None,
            "friendly_name": None,
            "status": None,
            "status_message": "❌ Не найден",
            "instance_id": None,
            "name": device_name,
            "vid": vid,
            "pid": pid,
            "has_driver": False,
            "is_working": False
        }

    def scan_device(self, vid: int, pid: int, device_name: str = None) -> Dict:
        """Сканирует конкретное устройство по VID/PID"""
        return self.get_device_info(vid, pid, device_name)

    def scan_all_devices(self, devices_list: List[Tuple[int, int, str]] = None) -> List[Dict]:
        """Сканирует все устройства из списка"""
        if devices_list is None:
            devices_list = self.DEVICES

        results = []
        for vid, pid, name in devices_list:
            info = self.get_device_info(vid, pid, name)
            results.append(info)

        return results

    def get_laser_controller_ports(self) -> List[str]:
        """Возвращает список COM-портов контроллера лазера"""
        laser_info = self.get_laser_ports_info()
        return laser_info["connected_ports"]

    def get_laser_port_by_function(self, function: str) -> Optional[str]:
        """
        Возвращает COM-порт лазера по его функции
        
        Args:
            function: "Управление моторами", "Управление лазером", "Датчики/обратная связь", "Дополнительный порт"
        
        Returns:
            Имя COM-порта или None
        """
        laser_info = self.get_laser_ports_info()
        for port_info in laser_info["ports"]:
            if port_info["function"] == function:
                return port_info["port"]
        return None

    def get_laser_motor_port(self) -> Optional[str]:
        """Возвращает COM-порт для управления моторами лазера"""
        return self.get_laser_port_by_function("Управление моторами")

    def get_laser_control_port(self) -> Optional[str]:
        """Возвращает COM-порт для управления лазером"""
        return self.get_laser_port_by_function("Управление лазером")

    def get_laser_sensor_port(self) -> Optional[str]:
        """Возвращает COM-порт для датчиков/обратной связи"""
        return self.get_laser_port_by_function("Датчики/обратная связь")

    def get_available_com_ports(self) -> List[Dict]:
        """Возвращает список всех доступных COM-портов с информацией"""
        ports = []
        com_ports = serial.tools.list_ports.comports()
        for port in com_ports:
            ports.append({
                "port": port.device,
                "description": port.description,
                "hardware_id": port.hwid,
                "vid": port.vid,
                "pid": port.pid,
                "serial_number": port.serial_number,
                "product": port.product,
                "manufacturer": port.manufacturer
            })
        return ports

    def is_device_connected(self, vid: int, pid: int) -> bool:
        """Быстрая проверка, подключено ли устройство"""
        info = self.get_device_info(vid, pid)
        return info["found"]

    def get_device_com_port(self, vid: int, pid: int) -> Optional[str]:
        """Получает COM-порт для устройства (если это COM-устройство)"""
        info = self.get_device_info(vid, pid)
        if info["found"] and info.get("method") == "com":
            return info["port"]
        return None

    def get_energometer_info(self) -> Dict:
        """Специальный метод для получения информации об энергометре"""
        info = self.get_device_info(0x0403, 0x6001, "Энергометр (базовый)")
        if info["found"]:
            return info
        return self.get_device_info(0x0403, 0x6001, "Энергометр (виртуальный)")

    def get_laser_info(self) -> Dict:
        """Специальный метод для получения информации о лазере (контроллере)"""
        return self.get_device_info(self.LASER_VID, self.LASER_PID, "Лазер (контроллер)")

    def get_oscilloscope_info(self) -> Dict:
        """Специальный метод для получения информации об осциллографе"""
        return self.get_device_info(0x0957, 0x1796, "Осциллограф")

    def get_monochromator_info(self) -> Dict:
        """Специальный метод для получения информации о монохроматоре"""
        return self.get_device_info(0x0547, 0x1005, "Монохроматор")

    def print_device_info(self, device_info: Dict) -> None:
        """Красиво выводит информацию об устройстве"""
        if not device_info:
            print("Нет информации об устройстве")
            return

        name = device_info.get("name", "Неизвестное устройство")
        vid = device_info.get("vid", "?")
        pid = device_info.get("pid", "?")

        # Специальный вывод для контроллера лазера
        if device_info.get("is_laser_controller"):
            print(f"[{name}] (VID=0x{vid:04X}, PID=0x{pid:04X})")
            if device_info["found"]:
                print(f"    ✅ НАЙДЕН (FTDI FT4232H - 4-портовый контроллер)")
                ports = device_info.get("ports", [])
                print(f"    └─ Найдено портов: {len(ports)}/4")
                for port_info in ports:
                    print(f"       📌 {port_info['port']}: {port_info['function']}")
                    if port_info['description']:
                        print(f"          └─ {port_info['description']}")
            else:
                print(f"    ❌ НЕ НАЙДЕН")
            return

        # Обычный вывод для других устройств
        print(f"[{name}] (VID=0x{vid:04X}, PID=0x{pid:04X})" if isinstance(vid, int) else f"[{name}] (VID={vid}, PID={pid})")

        if device_info["found"]:
            if device_info.get("method") == "com":
                print(f"    ✅ НАЙДЕН (COM-порт)")
                print(f"       Порт: {device_info['port']}")
                if device_info["description"]:
                    print(f"       Описание: {device_info['description']}")
            elif device_info.get("method") == "com_multi":
                print(f"    ✅ НАЙДЕН (многопортовый)")
            else:
                print(f"    ✅ НАЙДЕН (USB-устройство)")
                if device_info["friendly_name"]:
                    print(f"       Имя: {device_info['friendly_name']}")
                print(f"       {device_info['status_message']}")
        else:
            print(f"    ❌ НЕ НАЙДЕН")

    def scan_and_print_all(self) -> None:
        """Сканирует все устройства и выводит информацию в консоль"""
        print("=" * 70)
        print("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ УСТРОЙСТВ")
        print("=" * 70)
        print()

        devices_info = self.scan_all_devices()
        for device_info in devices_info:
            self.print_device_info(device_info)
            print()

        com_ports = self.get_available_com_ports()
        if com_ports:
            print("Доступные COM-порты:")
            for port in com_ports:
                # Отмечаем порты лазера
                if port['vid'] == self.LASER_VID and port['pid'] == self.LASER_PID:
                    print(f"  🔴 {port['port']}: {port['description']} (ЛАЗЕР)")
                else:
                    print(f"  📌 {port['port']}: {port['description']}")
        print("=" * 70)


if __name__ == "__main__":
    scanner = PortScanner()
    scanner.scan_and_print_all()