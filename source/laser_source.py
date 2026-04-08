import serial
import time


class LaserSource:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.port_name = None


    def connect(self, port: str, baudrate: int = 115200, timeout_seconds: int = 1) -> bool:
        connection_status = False

        try:
            self.connection = serial.Serial(port, baudrate, timeout=timeout_seconds)
            self.port_name = port
            self.is_connected = True
            connection_status = True
        except Exception as error:
            connection_status = False

        return connection_status


    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

        self.is_connected = False


    def set_wavelength(self, wavelength_nanometers: float) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"WAVE {wavelength_nanometers}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_wavelength(self) -> float:
        wavelength_value = 0.0

        if self.is_connected:
            self.connection.write("WAVE?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                wavelength_value = float(response_string)
            except ValueError:
                wavelength_value = 0.0

        return wavelength_value


    def set_energy(self, energy_joules: float) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"ENER {energy_joules}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_energy(self) -> float:
        energy_value = 0.0

        if self.is_connected:
            self.connection.write("ENER?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                energy_value = float(response_string)
            except ValueError:
                energy_value = 0.0

        return energy_value


    def fire(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("FIRE\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_repetition_rate(self, rate_hertz: float) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"RATE {rate_hertz}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_repetition_rate(self) -> float:
        rate_value = 0.0

        if self.is_connected:
            self.connection.write("RATE?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                rate_value = float(response_string)
            except ValueError:
                rate_value = 0.0

        return rate_value


    def enable_output(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "OUT 1" if enable_status else "OUT 0"

        if self.is_connected:
            self.connection.write(f"{command_string}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_output_status(self) -> bool:
        output_status = False

        if self.is_connected:
            self.connection.write("OUT?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                output_status = True

        return output_status


    def set_qswitch_delay(self, delay_microseconds: float) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"QDEL {delay_microseconds}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_qswitch_delay(self) -> float:
        delay_value = 0.0

        if self.is_connected:
            self.connection.write("QDEL?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                delay_value = float(response_string)
            except ValueError:
                delay_value = 0.0

        return delay_value


    def set_qswitch_mode(self, mode: str) -> bool:
        operation_status = False
        valid_modes = ["FR", "INT", "EXT1", "EXT2", "SINGLE"]

        if mode.upper() in valid_modes and self.is_connected:
            self.connection.write(f"QSW {mode.upper()}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_qswitch_mode(self) -> str:
        mode_value = ""

        if self.is_connected:
            self.connection.write("QSW?\r\n".encode())
            time.sleep(0.05)
            mode_value = self.connection.readline().decode().strip()

        return mode_value


    def set_lamp_mode(self, mode: str) -> bool:
        operation_status = False
        valid_modes = ["INT", "EXT", "SINGLE"]

        if mode.upper() in valid_modes and self.is_connected:
            self.connection.write(f"LAMP {mode.upper()}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_lamp_mode(self) -> str:
        mode_value = ""

        if self.is_connected:
            self.connection.write("LAMP?\r\n".encode())
            time.sleep(0.05)
            mode_value = self.connection.readline().decode().strip()

        return mode_value


    def set_simmer_time(self, time_milliseconds: int) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"SIMMER {time_milliseconds}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_simmer_time(self) -> int:
        time_value = 0

        if self.is_connected:
            self.connection.write("SIMMER?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                time_value = int(response_string)
            except ValueError:
                time_value = 0

        return time_value


    def set_harmonic(self, harmonic_value) -> bool:
        operation_status = False
        valid_harmonics = [1064, 532, 355, "OPO"]

        if harmonic_value in valid_harmonics and self.is_connected:
            self.connection.write(f"HARM {harmonic_value}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_harmonic(self):
        harmonic_value = ""

        if self.is_connected:
            self.connection.write("HARM?\r\n".encode())
            time.sleep(0.05)
            harmonic_value = self.connection.readline().decode().strip()

            try:
                harmonic_value = int(harmonic_value)
            except ValueError:
                pass

        return harmonic_value


    def set_opo_wavelength(self, wavelength_nanometers: float) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write(f"OPO {wavelength_nanometers}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_opo_wavelength(self) -> float:
        wavelength_value = 0.0

        if self.is_connected:
            self.connection.write("OPO?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                wavelength_value = float(response_string)
            except ValueError:
                wavelength_value = 0.0

        return wavelength_value


    def set_shutter(self, open_status: bool) -> bool:
        operation_status = False
        command_value = 1 if open_status else 0

        if self.is_connected:
            self.connection.write(f"SHUTTER {command_value}\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_shutter(self) -> bool:
        shutter_status = False

        if self.is_connected:
            self.connection.write("SHUTTER?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                shutter_status = True

        return shutter_status


    def get_status(self) -> str:
        status_string = ""

        if self.is_connected:
            self.connection.write("STATUS?\r\n".encode())
            time.sleep(0.05)
            status_string = self.connection.readline().decode().strip()

        return status_string


    def get_temperature(self) -> float:
        temperature_value = 0.0

        if self.is_connected:
            self.connection.write("TEMP?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                temperature_value = float(response_string)
            except ValueError:
                temperature_value = 0.0

        return temperature_value


    def get_model(self) -> str:
        model_string = ""

        if self.is_connected:
            self.connection.write("MODEL?\r\n".encode())
            time.sleep(0.05)
            model_string = self.connection.readline().decode().strip()

        return model_string


    def get_serial_number(self) -> str:
        serial_number_string = ""

        if self.is_connected:
            self.connection.write("SN?\r\n".encode())
            time.sleep(0.05)
            serial_number_string = self.connection.readline().decode().strip()

        return serial_number_string


    def get_firmware_version(self) -> str:
        firmware_string = ""

        if self.is_connected:
            self.connection.write("FW?\r\n".encode())
            time.sleep(0.05)
            firmware_string = self.connection.readline().decode().strip()

        return firmware_string


    def get_lamp_count(self) -> int:
        lamp_count_value = 0

        if self.is_connected:
            self.connection.write("LAMPCOUNT?\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                lamp_count_value = int(response_string)
            except ValueError:
                lamp_count_value = 0

        return lamp_count_value


    def stop(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("STOP\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def standby(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("STANDBY\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def reset_device(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("RESET\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status
