"""
main.py - мониторинг USB-устройств
"""

import os
import sys
import time
from port_scanner import PortScanner


def clear_console():
    """Очищает консоль"""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Основная функция мониторинга"""
    scanner = PortScanner()
    
    devices = [
        (0x0403, 0x6001, "Энергометр"),
        (0x0403, 0x6011, "Лазер (контроллер)"),  # НОВЫЙ ЛАЗЕР
        (0x0957, 0x1796, "Осциллограф"),
        (0x0547, 0x1005, "Монохроматор")
    ]
    
    print("=" * 70)
    print("МОНИТОРИНГ USB-УСТРОЙСТВ")
    print("=" * 70)
    print("Для выхода нажмите Ctrl+C")
    print("=" * 70)
    print()
    
    try:
        while True:
            clear_console()
            
            print("=" * 70)
            print(f"МОНИТОРИНГ USB-УСТРОЙСТВ (обновление: {time.strftime('%H:%M:%S')})")
            print("=" * 70)
            print("Для выхода нажмите Ctrl+C")
            print("=" * 70)
            print()
            
            for vid, pid, name in devices:
                if vid == 0x0403 and pid == 0x6011:
                    # Специальный вывод для лазера
                    laser_info = scanner.get_laser_info()
                    if laser_info["found"]:
                        ports = laser_info.get("ports", [])
                        print(f"{name:20} : ✅ ПОДКЛЮЧЕН ({len(ports)}/4 портов)")
                        for port_info in ports:
                            print(f"                   └─ {port_info['port']}: {port_info['function']}")
                    else:
                        print(f"{name:20} : ❌ НЕ ПОДКЛЮЧЕН")
                else:
                    # Обычный вывод для других устройств
                    info = scanner.scan_device(vid, pid, name)
                    if not info["found"]:
                        print(f"{name:20} : ❌ НЕ ПОДКЛЮЧЕН")
                    elif info.get("method") == "com":
                        print(f"{name:20} : ✅ ПОДКЛЮЧЕН | Порт: {info['port']}")
                    else:
                        print(f"{name:20} : ✅ ПОДКЛЮЧЕН")
            
            print()
            print("-" * 70)
            print("Доступные COM-порты:")
            
            com_ports = scanner.get_available_com_ports()
            for port in com_ports:
                if port['vid'] == 0x0403 and port['pid'] == 0x6011:
                    print(f"  🔴 {port['port']}: {port['description']} (ЛАЗЕР)")
                elif port['vid'] == 0x0403 and port['pid'] == 0x6001:
                    print(f"  💚 {port['port']}: {port['description']} (Энергометр)")
                elif port['vid'] == 0x067B and port['pid'] == 0x2303:
                    print(f"  💛 {port['port']}: {port['description']} (Лазер-старый)")
                else:
                    print(f"  📌 {port['port']}: {port['description']}")
            
            print("=" * 70)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена.")
        sys.exit(0)


if __name__ == "__main__":
    main()