"""
Модуль для управления монохроматором через SDK SolarLS
"""

import ctypes
import os
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any


class MonochromatorError(Exception):
    """Исключение для ошибок монохроматора"""
    pass


class ShutterState:
    """Состояния затвора"""
    UNKNOWN = 0
    OPEN = 1
    CLOSE = 2


class InstrumentStatus:
    """Статусы инструмента"""
    BUSY = 0
    READY = 1
    ERROR = 2


class Monochromator:
    """
    Класс для управления монохроматором через SDK SolarLS
    
    Пример использования:
        mono = Monochromator(sdk_path="sdk")
        if mono.connect():
            mono.set_wavelength(500)
            print(f"Текущая длина волны: {mono.get_wavelength()} нм")
            mono.disconnect()
    """
    
    def __init__(self, sdk_path: str = "sdk", config_path: Optional[str] = None):
        """
        Инициализация монохроматора
        
        Args:
            sdk_path: Путь к папке с DLL файлами SDK
            config_path: Путь к конфигурационному файлу (если None, используется папка с DLL)
        """
        self.sdk_path = Path(sdk_path)
        self.config_path = config_path
        self.dll = None
        self.is_initialized = False
        self.instrument_count = 0
        self.instrument_name = None
        self.current_instrument_idx = 0
        
        # Кэш для параметров
        self._grating_count = None
        self._gratings_cache = None
        self._slit_count = None
        self._filter_count = None
        self._mirror_count = None
        self._shutter_count = None
        
    def _add_dll_directory(self):
        """Добавление пути к DLL в системный поиск"""
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(str(self.sdk_path.absolute()))
            except Exception:
                pass
    
    def _configure_function_types(self):
        """Настройка типов аргументов для функций DLL"""
        
        # Общие функции
        self.dll.sls_Init.argtypes = [ctypes.c_char_p]
        self.dll.sls_Init.restype = ctypes.c_int
        
        self.dll.sls_GetInstrumentCount.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetInstrumentCount.restype = ctypes.c_int
        
        self.dll.sls_GetInstrumentName.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetInstrumentName.restype = ctypes.c_int
        
        self.dll.sls_GetInstrumentSerial.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetInstrumentSerial.restype = ctypes.c_int
        
        self.dll.sls_GetInstrumentStatus.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetInstrumentStatus.restype = ctypes.c_int
        
        self.dll.sls_GetLastErrorText.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetLastErrorText.restype = None
        
        # Управление длиной волны
        self.dll.sls_SetWl.argtypes = [ctypes.c_int, ctypes.c_double]
        self.dll.sls_SetWl.restype = ctypes.c_int
        
        self.dll.sls_SetWlAsync.argtypes = [ctypes.c_int, ctypes.c_double]
        self.dll.sls_SetWlAsync.restype = ctypes.c_int
        
        self.dll.sls_GetWl.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        self.dll.sls_GetWl.restype = ctypes.c_int
        
        self.dll.sls_IsValidWl.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_IsValidWl.restype = ctypes.c_int
        
        self.dll.sls_ResetGrating.argtypes = [ctypes.c_int]
        self.dll.sls_ResetGrating.restype = ctypes.c_int
        
        self.dll.sls_ResetSetGrating.argtypes = [ctypes.c_int, ctypes.c_double]
        self.dll.sls_ResetSetGrating.restype = ctypes.c_int
        
        self.dll.sls_GetDispersion.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        self.dll.sls_GetDispersion.restype = ctypes.c_int
        
        # Управление решётками
        self.dll.sls_GetGratingCount.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetGratingCount.restype = ctypes.c_int
        
        self.dll.sls_GetActiveGrating.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetActiveGrating.restype = ctypes.c_int
        
        self.dll.sls_SetActiveGrating.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.sls_SetActiveGrating.restype = ctypes.c_int
        
        self.dll.sls_GetGratingPrm.argtypes = [
            ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double)
        ]
        self.dll.sls_GetGratingPrm.restype = ctypes.c_int
        
        # Управление щелями
        self.dll.sls_GetSlitCount.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetSlitCount.restype = ctypes.c_int
        
        self.dll.sls_GetSlitName.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetSlitName.restype = ctypes.c_int
        
        self.dll.sls_SetSlitWidth.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
        self.dll.sls_SetSlitWidth.restype = ctypes.c_int
        
        self.dll.sls_GetSlitWidth.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        self.dll.sls_GetSlitWidth.restype = ctypes.c_int
        
        # Управление затворами
        self.dll.sls_GetShutterCount.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetShutterCount.restype = ctypes.c_int
        
        self.dll.sls_GetShutterName.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetShutterName.restype = ctypes.c_int
        
        self.dll.sls_ShutterOpen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.sls_ShutterOpen.restype = ctypes.c_int
        
        self.dll.sls_ShutterClose.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.sls_ShutterClose.restype = ctypes.c_int
        
        self.dll.sls_GetShutterState.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetShutterState.restype = ctypes.c_int
        
        # Управление фильтрами
        self.dll.sls_GetFilterCount.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetFilterCount.restype = ctypes.c_int
        
        self.dll.sls_GetFilterName.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.dll.sls_GetFilterName.restype = ctypes.c_int
        
        self.dll.sls_GetFilterStateCount.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetFilterStateCount.restype = ctypes.c_int
        
        self.dll.sls_GetFilterStateIdx.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.dll.sls_GetFilterStateIdx.restype = ctypes.c_int
        
        self.dll.sls_SetFilterStateIdx.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.dll.sls_SetFilterStateIdx.restype = ctypes.c_int
        
        # Калибровка
        self.dll.sls_GetPixelClbr.argtypes = [
            ctypes.c_int, ctypes.c_double, ctypes.c_int,
            ctypes.c_double, ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        ]
        self.dll.sls_GetPixelClbr.restype = ctypes.c_int
        
    def _get_last_error(self) -> str:
        """Получение текста последней ошибки"""
        error_buffer = ctypes.create_string_buffer(512)
        if self.dll:
            self.dll.sls_GetLastErrorText(error_buffer, 512)
        return error_buffer.value.decode('utf-8', errors='ignore')
    
    def _check_result(self, result: int, operation: str) -> bool:
        """
        Проверка результата операции
        
        Args:
            result: Код возврата из DLL
            operation: Название операции для сообщения об ошибке
            
        Returns:
            True если успешно, иначе False
            
        Raises:
            MonochromatorError: Если операция не удалась
        """
        if result:
            return True
        else:
            error_msg = self._get_last_error()
            raise MonochromatorError(f"{operation} failed: {error_msg}")
    
    def connect(self) -> bool:
        """
        Подключение к монохроматору
        
        Returns:
            True если подключение успешно, иначе False
        """
        try:
            # Добавляем путь к DLL
            self._add_dll_directory()
            
            # Загружаем DLL
            dll_path = self.sdk_path / "SolarLS.Sdk.dll"
            if not dll_path.exists():
                raise MonochromatorError(f"DLL not found: {dll_path}")
            
            self.dll = ctypes.CDLL(str(dll_path))
            self._configure_function_types()
            
            # Инициализация библиотеки
            config_path_bytes = None
            if self.config_path:
                config_path_bytes = self.config_path.encode('utf-8')
            elif self.sdk_path:
                # Используем папку с SDK как путь к конфигурации
                config_path_bytes = str(self.sdk_path).encode('utf-8')
            
            result = self.dll.sls_Init(config_path_bytes)
            if not result:
                error_msg = self._get_last_error()
                raise MonochromatorError(f"Init failed: {error_msg}")
            
            # Получаем количество инструментов
            count = ctypes.c_int()
            result = self.dll.sls_GetInstrumentCount(ctypes.byref(count))
            if not result or count.value == 0:
                raise MonochromatorError("No instruments found")
            
            self.instrument_count = count.value
            
            # Получаем имя первого инструмента
            name_buffer = ctypes.create_string_buffer(256)
            result = self.dll.sls_GetInstrumentName(0, name_buffer, 256)
            if result:
                self.instrument_name = name_buffer.value.decode('utf-8', errors='ignore')
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.is_initialized = False
            raise MonochromatorError(f"Connection failed: {e}")
    
    def disconnect(self):
        """Отключение от монохроматора"""
        # SDK не предоставляет явной функции деинициализации
        self.is_initialized = False
        self.dll = None
    
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self.is_initialized and self.dll is not None
    
    def get_status(self) -> int:
        """
        Получение статуса инструмента
        
        Returns:
            InstrumentStatus: 0-BUSY, 1-READY, 2-ERROR
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        status = ctypes.c_int()
        result = self.dll.sls_GetInstrumentStatus(self.current_instrument_idx, ctypes.byref(status))
        self._check_result(result, "Get instrument status")
        
        return status.value
    
    def is_ready(self) -> bool:
        """Проверка готовности инструмента"""
        return self.get_status() == InstrumentStatus.READY
    
    def wait_for_ready(self, timeout: float = 30.0, check_interval: float = 0.5) -> bool:
        """
        Ожидание готовности инструмента
        
        Args:
            timeout: Таймаут в секундах
            check_interval: Интервал проверки в секундах
            
        Returns:
            True если инструмент готов, False если таймаут
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_ready():
                return True
            time.sleep(check_interval)
        return False
    
    def ensure_ready(self) -> bool:
        """Гарантирует готовность монохроматора к работе"""
        try:
            status = self.get_status()
            if status == InstrumentStatus.ERROR:
                self.reset_grating()
                time.sleep(3)
                return self.get_status() == InstrumentStatus.READY
            return status == InstrumentStatus.READY
        except MonochromatorError as e:
            if "offline" in str(e).lower():
                # Переподключаемся
                self.disconnect()
                time.sleep(1)
                self.connect()
                time.sleep(2)
                self.reset_grating()
                time.sleep(3)
                return self.get_status() == InstrumentStatus.READY
            raise

    # ==================== Управление длиной волны ====================
    
    def set_wavelength(self, wavelength: float, async_mode: bool = False, wait: bool = True) -> bool:
        """
        Установка длины волны
        
        Args:
            wavelength: Длина волны в нанометрах
            async_mode: Асинхронный режим (не ждать завершения)
            wait: Ожидать готовности после установки (только для синхронного режима)
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_SetWlAsync(self.current_instrument_idx, ctypes.c_double(wavelength))
            self._check_result(result, f"Set wavelength async to {wavelength} nm")
        else:
            result = self.dll.sls_SetWl(self.current_instrument_idx, ctypes.c_double(wavelength))
            self._check_result(result, f"Set wavelength to {wavelength} nm")
            
            if wait:
                self.wait_for_ready()
        
        return True
    
    def get_wavelength(self) -> float:
        """
        Получение текущей длины волны
        
        Returns:
            Текущая длина волны в нанометрах
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        wavelength = ctypes.c_double()
        result = self.dll.sls_GetWl(self.current_instrument_idx, ctypes.byref(wavelength))
        self._check_result(result, "Get wavelength")
        
        return wavelength.value
    
    def is_valid_wavelength(self, wavelength: float) -> bool:
        """
        Проверка возможности установки длины волны
        
        Args:
            wavelength: Длина волны в нанометрах
            
        Returns:
            True если длина волны доступна
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        is_valid = ctypes.c_int()
        result = self.dll.sls_IsValidWl(self.current_instrument_idx, ctypes.c_double(wavelength), ctypes.byref(is_valid))
        self._check_result(result, "Check valid wavelength")
        
        return bool(is_valid.value)
    
    def reset_grating(self, async_mode: bool = False) -> bool:
        """
        Сброс решётки (перемещение в реперную позицию)
        
        Args:
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_ResetGratingAsync(self.current_instrument_idx)
        else:
            result = self.dll.sls_ResetGrating(self.current_instrument_idx)
        
        self._check_result(result, "Reset grating")
        return True
    
    def reset_and_set_wavelength(self, wavelength: float, async_mode: bool = False) -> bool:
        """
        Сброс решётки и установка длины волны
        
        Args:
            wavelength: Длина волны в нанометрах
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_ResetSetGrating(self.current_instrument_idx, ctypes.c_double(wavelength))
        else:
            result = self.dll.sls_ResetSetGrating(self.current_instrument_idx, ctypes.c_double(wavelength))
        
        self._check_result(result, f"Reset and set wavelength to {wavelength} nm")
        return True
    
    def get_dispersion(self) -> float:
        """
        Получение дисперсии для активной решётки при текущей длине волны
        
        Returns:
            Дисперсия
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        dispersion = ctypes.c_double()
        result = self.dll.sls_GetDispersion(self.current_instrument_idx, ctypes.byref(dispersion))
        self._check_result(result, "Get dispersion")
        
        return dispersion.value
    
    # ==================== Управление решётками ====================
    
    def get_grating_count(self) -> int:
        """Получение количества решёток"""
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if self._grating_count is None:
            count = ctypes.c_int()
            result = self.dll.sls_GetGratingCount(self.current_instrument_idx, ctypes.byref(count))
            self._check_result(result, "Get grating count")
            self._grating_count = count.value
        
        return self._grating_count
    
    def get_active_grating(self) -> int:
        """Получение индекса активной решётки"""
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        grating_idx = ctypes.c_int()
        result = self.dll.sls_GetActiveGrating(self.current_instrument_idx, ctypes.byref(grating_idx))
        self._check_result(result, "Get active grating")
        
        return grating_idx.value
    
    def set_active_grating(self, grating_idx: int, async_mode: bool = False) -> bool:
        """
        Установка активной решётки
        
        Args:
            grating_idx: Индекс решётки
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        count = self.get_grating_count()
        if grating_idx < 0 or grating_idx >= count:
            raise MonochromatorError(f"Grating index {grating_idx} out of range (0-{count-1})")
        
        if async_mode:
            result = self.dll.sls_SetActiveGratingAsync(self.current_instrument_idx, grating_idx)
        else:
            result = self.dll.sls_SetActiveGrating(self.current_instrument_idx, grating_idx)
        
        self._check_result(result, f"Set active grating to {grating_idx}")
        return True
    
    def get_grating_parameters(self, grating_idx: int) -> Dict[str, Any]:
        """
        Получение параметров решётки
        
        Args:
            grating_idx: Индекс решётки
            
        Returns:
            Словарь с параметрами: grooves, min_wl, max_wl, blaze_angle
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        grooves = ctypes.c_int()
        min_wl = ctypes.c_double()
        max_wl = ctypes.c_double()
        blaze_angle = ctypes.c_double()
        
        result = self.dll.sls_GetGratingPrm(
            self.current_instrument_idx, grating_idx,
            ctypes.byref(grooves),
            ctypes.byref(min_wl),
            ctypes.byref(max_wl),
            ctypes.byref(blaze_angle)
        )
        self._check_result(result, f"Get grating parameters for index {grating_idx}")
        
        return {
            'grooves': grooves.value,
            'min_wl': min_wl.value,
            'max_wl': max_wl.value,
            'blaze_angle': blaze_angle.value
        }
    
    def get_all_gratings(self) -> List[Dict[str, Any]]:
        """Получение информации о всех решётках"""
        count = self.get_grating_count()
        gratings = []
        
        for i in range(count):
            params = self.get_grating_parameters(i)
            params['index'] = i
            params['is_active'] = (self.get_active_grating() == i)
            gratings.append(params)
        
        return gratings
    
    # ==================== Управление щелями ====================
    
    def get_slit_count(self) -> int:
        """Получение количества щелей"""
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if self._slit_count is None:
            count = ctypes.c_int()
            result = self.dll.sls_GetSlitCount(self.current_instrument_idx, ctypes.byref(count))
            self._check_result(result, "Get slit count")
            self._slit_count = count.value
        
        return self._slit_count
    
    def get_slit_name(self, slit_idx: int) -> str:
        """
        Получение названия щели
        
        Args:
            slit_idx: Индекс щели
            
        Returns:
            Название щели
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        name_buffer = ctypes.create_string_buffer(256)
        result = self.dll.sls_GetSlitName(self.current_instrument_idx, slit_idx, name_buffer, 256)
        self._check_result(result, f"Get slit name for index {slit_idx}")
        
        return name_buffer.value.decode('utf-8', errors='ignore')
    
    def set_slit_width(self, slit_idx: int, width: float, reset_required: bool = False, async_mode: bool = False) -> bool:
        """
        Установка ширины щели
        
        Args:
            slit_idx: Индекс щели
            width: Ширина в микрометрах
            reset_required: Требуется ли сброс перед установкой
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_SetSlitWidthAsync(self.current_instrument_idx, slit_idx, ctypes.c_double(width), reset_required)
        else:
            result = self.dll.sls_SetSlitWidth(self.current_instrument_idx, slit_idx, ctypes.c_double(width), reset_required)
        
        self._check_result(result, f"Set slit {slit_idx} width to {width} um")
        return True
    
    def get_slit_width(self, slit_idx: int) -> float:
        """
        Получение ширины щели
        
        Args:
            slit_idx: Индекс щели
            
        Returns:
            Ширина в микрометрах
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        width = ctypes.c_double()
        result = self.dll.sls_GetSlitWidth(self.current_instrument_idx, slit_idx, ctypes.byref(width))
        self._check_result(result, f"Get slit {slit_idx} width")
        
        return width.value
    
    # ==================== Управление затворами ====================
    
    def get_shutter_count(self) -> int:
        """Получение количества затворов"""
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if self._shutter_count is None:
            count = ctypes.c_int()
            result = self.dll.sls_GetShutterCount(self.current_instrument_idx, ctypes.byref(count))
            self._check_result(result, "Get shutter count")
            self._shutter_count = count.value
        
        return self._shutter_count
    
    def get_shutter_name(self, shutter_idx: int) -> str:
        """
        Получение названия затвора
        
        Args:
            shutter_idx: Индекс затвора
            
        Returns:
            Название затвора
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        name_buffer = ctypes.create_string_buffer(256)
        result = self.dll.sls_GetShutterName(self.current_instrument_idx, shutter_idx, name_buffer, 256)
        self._check_result(result, f"Get shutter name for index {shutter_idx}")
        
        return name_buffer.value.decode('utf-8', errors='ignore')
    
    def shutter_open(self, shutter_idx: int = 0, async_mode: bool = False) -> bool:
        """
        Открытие затвора
        
        Args:
            shutter_idx: Индекс затвора
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_ShutterOpenAsync(self.current_instrument_idx, shutter_idx)
        else:
            result = self.dll.sls_ShutterOpen(self.current_instrument_idx, shutter_idx)
        
        self._check_result(result, f"Open shutter {shutter_idx}")
        return True
    
    def shutter_close(self, shutter_idx: int = 0, async_mode: bool = False) -> bool:
        """
        Закрытие затвора
        
        Args:
            shutter_idx: Индекс затвора
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_ShutterCloseAsync(self.current_instrument_idx, shutter_idx)
        else:
            result = self.dll.sls_ShutterClose(self.current_instrument_idx, shutter_idx)
        
        self._check_result(result, f"Close shutter {shutter_idx}")
        return True
    
    def get_shutter_state(self, shutter_idx: int = 0) -> int:
        """
        Получение состояния затвора
        
        Args:
            shutter_idx: Индекс затвора
            
        Returns:
            ShutterState: 0-UNKNOWN, 1-OPEN, 2-CLOSE
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        state = ctypes.c_int()
        result = self.dll.sls_GetShutterState(self.current_instrument_idx, shutter_idx, ctypes.byref(state))
        self._check_result(result, f"Get shutter {shutter_idx} state")
        
        return state.value
    
    def is_shutter_open(self, shutter_idx: int = 0) -> bool:
        """Проверка открыт ли затвор"""
        return self.get_shutter_state(shutter_idx) == ShutterState.OPEN
    
    # ==================== Управление фильтрами ====================
    
    def get_filter_count(self) -> int:
        """Получение количества фильтров"""
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if self._filter_count is None:
            count = ctypes.c_int()
            result = self.dll.sls_GetFilterCount(self.current_instrument_idx, ctypes.byref(count))
            self._check_result(result, "Get filter count")
            self._filter_count = count.value
        
        return self._filter_count
    
    def get_filter_name(self, filter_idx: int) -> str:
        """
        Получение названия фильтра
        
        Args:
            filter_idx: Индекс фильтра
            
        Returns:
            Название фильтра
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        name_buffer = ctypes.create_string_buffer(256)
        result = self.dll.sls_GetFilterName(self.current_instrument_idx, filter_idx, name_buffer, 256)
        self._check_result(result, f"Get filter name for index {filter_idx}")
        
        return name_buffer.value.decode('utf-8', errors='ignore')
    
    def get_filter_state_count(self, filter_idx: int) -> int:
        """
        Получение количества состояний фильтра
        
        Args:
            filter_idx: Индекс фильтра
            
        Returns:
            Количество состояний
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        count = ctypes.c_int()
        result = self.dll.sls_GetFilterStateCount(self.current_instrument_idx, filter_idx, ctypes.byref(count))
        self._check_result(result, f"Get filter state count for index {filter_idx}")
        
        return count.value
    
    def get_filter_state(self, filter_idx: int) -> int:
        """
        Получение текущего состояния фильтра
        
        Args:
            filter_idx: Индекс фильтра
            
        Returns:
            Индекс текущего состояния
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        state_idx = ctypes.c_int()
        result = self.dll.sls_GetFilterStateIdx(self.current_instrument_idx, filter_idx, ctypes.byref(state_idx))
        self._check_result(result, f"Get filter {filter_idx} state")
        
        return state_idx.value
    
    def set_filter_state(self, filter_idx: int, state_idx: int, async_mode: bool = False) -> bool:
        """
        Установка состояния фильтра
        
        Args:
            filter_idx: Индекс фильтра
            state_idx: Индекс состояния
            async_mode: Асинхронный режим
            
        Returns:
            True если успешно
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        if async_mode:
            result = self.dll.sls_SetFilterStateIdxAsync(self.current_instrument_idx, filter_idx, state_idx)
        else:
            result = self.dll.sls_SetFilterStateIdx(self.current_instrument_idx, filter_idx, state_idx)
        
        self._check_result(result, f"Set filter {filter_idx} state to {state_idx}")
        return True
    
    # ==================== Калибровка ====================
    
    def get_wavelength_at_pixel(self, central_wl: float, central_pixel: int, 
                                 pixel_pitch: float, pixel_num: int) -> float:
        """
        Получение длины волны для указанного пикселя
        
        Args:
            central_wl: Длина волны на центральном пикселе
            central_pixel: Номер центрального пикселя
            pixel_pitch: Размер пикселя в микрометрах
            pixel_num: Номер пикселя для расчёта
            
        Returns:
            Длина волны для указанного пикселя
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        wl = ctypes.c_double()
        result = self.dll.sls_GetPixelClbr(
            self.current_instrument_idx,
            ctypes.c_double(central_wl),
            central_pixel,
            ctypes.c_double(pixel_pitch),
            pixel_num,
            ctypes.byref(wl)
        )
        self._check_result(result, "Get wavelength at pixel")
        
        return wl.value
    
    def get_calibration_array(self, central_wl: float, central_pixel: int,
                               pixel_pitch: float, pixel_count: int) -> List[float]:
        """
        Получение массива калибровки для всех пикселей
        
        Args:
            central_wl: Длина волны на центральном пикселе
            central_pixel: Номер центрального пикселя
            pixel_pitch: Размер пикселя в микрометрах
            pixel_count: Количество пикселей
            
        Returns:
            Список длин волн для каждого пикселя
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        calibration_array = (ctypes.c_double * pixel_count)()
        result = self.dll.sls_GetCalibration(
            self.current_instrument_idx,
            ctypes.c_double(central_wl),
            central_pixel,
            ctypes.c_double(pixel_pitch),
            pixel_count,
            calibration_array
        )
        self._check_result(result, "Get calibration array")
        
        return [calibration_array[i] for i in range(pixel_count)]
    
    # ==================== Информационные методы ====================
    
    def get_instrument_name(self) -> str:
        """Получение имени инструмента"""
        return self.instrument_name or "Unknown"
    
    def get_instrument_serial(self, instrument_idx: int = 0) -> str:
        """
        Получение серийного номера инструмента
        
        Args:
            instrument_idx: Индекс инструмента
            
        Returns:
            Серийный номер
        """
        if not self.is_connected():
            raise MonochromatorError("Not connected")
        
        serial_buffer = ctypes.create_string_buffer(256)
        result = self.dll.sls_GetInstrumentSerial(instrument_idx, serial_buffer, 256)
        self._check_result(result, "Get instrument serial")
        
        return serial_buffer.value.decode('utf-8', errors='ignore')
    
    def get_info(self) -> Dict[str, Any]:
        """
        Получение полной информации о монохроматоре
        
        Returns:
            Словарь с информацией
        """
        info = {
            'connected': self.is_connected(),
            'instrument_name': self.get_instrument_name(),
            'instrument_count': self.instrument_count,
            'current_wavelength': None,
            'status': None,
            'active_grating': None,
            'grating_count': None,
            'slit_count': None,
            'shutter_count': None,
            'filter_count': None,
        }
        
        if self.is_connected():
            try:
                info['current_wavelength'] = self.get_wavelength()
                info['status'] = self.get_status()
                info['active_grating'] = self.get_active_grating()
                info['grating_count'] = self.get_grating_count()
                info['slit_count'] = self.get_slit_count()
                info['shutter_count'] = self.get_shutter_count()
                info['filter_count'] = self.get_filter_count()
            except MonochromatorError:
                pass
        
        return info
