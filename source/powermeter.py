import serial
import time

from typing import Tuple


class Powermeter:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.port_name = None


    def connect(self, com_port: int, baudrate: int = 115200) -> bool:
        connection_status = False

        try:
            self.connection = serial.Serial(f'COM{com_port}', baudrate, timeout=1)
            self.port_name = com_port
            self.is_connected = True
            time.sleep(0.5)
            connection_status = True
        except Exception as error:
            connection_status = False

        return connection_status


    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

        self.is_connected = False


    def get_version(self) -> str:
        version_string = ""

        if self.is_connected:
            self.connection.write("*VER\r\n".encode())
            time.sleep(0.05)
            version_string = self.connection.readline().decode().strip()

        return version_string


    def get_status(self) -> str:
        status_string = ""

        if self.is_connected:
            self.connection.write("*STS\r\n".encode())
            time.sleep(0.05)
            status_string = self.connection.readline().decode().strip()

        return status_string


    def get_extended_status(self) -> str:
        extended_status_string = ""

        if self.is_connected:
            self.connection.write("*ST2\r\n".encode())
            time.sleep(0.05)
            extended_status_string = self.connection.readline().decode().strip()

        return extended_status_string


    def set_scale(self, scale_index: int) -> bool:
        operation_status = False

        if self.is_connected and 0 <= scale_index <= 41:
            command_string = f"*SCS{scale_index:02d}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_scale_up(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*SSU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_scale_down(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*SSD\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_current_scale_index(self) -> int:
        scale_index = 0

        if self.is_connected:
            self.connection.write("*GCR\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                scale_index = int(response_string)
            except ValueError:
                scale_index = 0

        return scale_index


    def set_autoscale(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*SAS1\r\n" if enable_status else "*SAS0\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_autoscale(self) -> bool:
        autoscale_status = False

        if self.is_connected:
            self.connection.write("*GAS\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                autoscale_status = True

        return autoscale_status


    def get_valid_scales(self) -> str:
        valid_scales_string = ""

        if self.is_connected:
            self.connection.write("*DVS\r\n".encode())
            time.sleep(0.05)
            valid_scales_string = self.connection.readline().decode().strip()

        return valid_scales_string


    def set_trigger_level(self, trigger_level_percent: float) -> bool:
        operation_status = False

        if self.is_connected and 0.1 <= trigger_level_percent <= 99.9:
            command_string = f"*STL{trigger_level_percent:04.1f}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_trigger_level(self) -> float:
        trigger_level = 0.0

        if self.is_connected:
            self.connection.write("*GTL\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if ':' in response_string:
                parts = response_string.split(':')

                if len(parts) > 1:
                    try:
                        trigger_level = float(parts[1].strip())
                    except ValueError:
                        trigger_level = 0.0

        return trigger_level


    def get_measure_mode(self) -> int:
        measure_mode = 0

        if self.is_connected:
            self.connection.write("*GMD\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if ':' in response_string:
                parts = response_string.split(':')

                if len(parts) > 1:
                    try:
                        measure_mode = int(parts[1].strip())
                    except ValueError:
                        measure_mode = 0

        return measure_mode


    def get_current_value(self) -> float:
        current_value = 0.0

        if self.is_connected:
            self.connection.write("*CVU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                current_value = float(response_string)
            except ValueError:
                current_value = 0.0

        return current_value


    def start_continuous_transmission(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*CAU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def start_continuous_with_frequency(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*CEU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_current_with_frequency(self) -> Tuple[float, float]:
        energy_value = 0.0
        frequency_value = 0.0

        if self.is_connected:
            self.connection.write("*CTU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()
            parts = response_string.split(',')

            if len(parts) >= 2:
                try:
                    energy_value = float(parts[0])
                    frequency_value = float(parts[1])
                except ValueError:
                    energy_value = 0.0
                    frequency_value = 0.0

        return energy_value, frequency_value


    def stop_continuous_transmission(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*CSU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def is_new_value_ready(self) -> bool:
        new_value_ready = False

        if self.is_connected:
            self.connection.write("*NVU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if "available" in response_string.lower() and "not" not in response_string.lower():
                new_value_ready = True

        return new_value_ready


    def get_laser_frequency(self) -> float:
        frequency_value = 0.0

        if self.is_connected:
            self.connection.write("*GRR\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            try:
                frequency_value = float(response_string)
            except ValueError:
                frequency_value = 0.0

        return frequency_value


    def set_binary_mode(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*SS11\r\n" if enable_status else "*SS10\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_binary_mode(self) -> bool:
        binary_mode_status = False

        if self.is_connected:
            self.connection.write("*GBM\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                binary_mode_status = True

        return binary_mode_status


    def set_wavelength_nanometers(self, wavelength_nanometers: int) -> bool:
        operation_status = False

        if self.is_connected:
            command_string = f"*PWC{wavelength_nanometers:05d}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_wavelength_microns(self, wavelength_microns: float) -> bool:
        operation_status = False

        if self.is_connected:
            command_string = f"*PWM{wavelength_microns:05.1f}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_wavelength(self) -> int:
        wavelength_value = 0

        if self.is_connected:
            self.connection.write("*GWL\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if ':' in response_string:
                parts = response_string.split(':')

                if len(parts) > 1:
                    try:
                        wavelength_value = int(parts[1].strip())
                    except ValueError:
                        wavelength_value = 0

        return wavelength_value


    def set_anticipation(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*ANT1\r\n" if enable_status else "*ANT0\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_anticipation(self) -> bool:
        anticipation_status = False

        if self.is_connected:
            self.connection.write("*GAN\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                anticipation_status = True

        return anticipation_status


    def set_noise_suppression(self, average_size: int) -> bool:
        operation_status = False

        if self.is_connected and 0 <= average_size <= 999:
            command_string = f"*AVG{average_size:03d}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_zero_offset(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*SOU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def clear_zero_offset(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*COU\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_zero_offset(self) -> bool:
        zero_offset_status = False

        if self.is_connected:
            self.connection.write("*GZO\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                zero_offset_status = True

        return zero_offset_status


    def set_diode_zero_offset(self) -> bool:
        operation_status = False

        if self.is_connected:
            self.connection.write("*SDZ\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_user_multiplier(self, multiplier: float) -> bool:
        operation_status = False

        if self.is_connected:
            command_string = f"*MUL{multiplier:.6e}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_user_multiplier(self) -> float:
        multiplier_value = 1.0

        if self.is_connected:
            self.connection.write("*GUM\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if ':' in response_string:
                parts = response_string.split(':')

                if len(parts) > 1:
                    try:
                        multiplier_value = float(parts[1].strip())
                    except ValueError:
                        multiplier_value = 1.0

        return multiplier_value


    def set_user_offset(self, offset: float) -> bool:
        operation_status = False

        if self.is_connected:
            command_string = f"*OFF{offset:.6e}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_user_offset(self) -> float:
        offset_value = 0.0

        if self.is_connected:
            self.connection.write("*GUO\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if ':' in response_string:
                parts = response_string.split(':')

                if len(parts) > 1:
                    try:
                        offset_value = float(parts[1].strip())
                    except ValueError:
                        offset_value = 0.0

        return offset_value


    def set_single_shot_energy_mode(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*SSE1\r\n" if enable_status else "*SSE0\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

            if operation_status:
                time.sleep(2)

        return operation_status


    def set_attenuator(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*ATT1\r\n" if enable_status else "*ATT0\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_attenuator(self) -> bool:
        attenuator_status = False

        if self.is_connected:
            self.connection.write("*GAT\r\n".encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string == "1":
                attenuator_status = True

        return attenuator_status


    def set_external_trigger(self, enable_status: bool) -> bool:
        operation_status = False
        command_string = "*ET1\r\n" if enable_status else "*ET0\r\n"

        if self.is_connected:
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def set_baud_rate(self, baud_rate_index: int) -> bool:
        operation_status = False
        baud_rates = {0: 9600, 1: 19200, 2: 38400, 3: 57600, 4: 115200}

        if self.is_connected and baud_rate_index in baud_rates:
            command_string = f"*BPS{baud_rate_index}\r\n"
            self.connection.write(command_string.encode())
            time.sleep(0.05)
            response_string = self.connection.readline().decode().strip()

            if response_string and "OK" in response_string.upper():
                operation_status = True

        return operation_status


    def get_power(self) -> float:
        power_value = self.get_current_value()

        return power_value


    def get_energy(self) -> float:
        energy_value = self.get_current_value()

        return energy_value


    def get_average_power(self, number_of_measurements: int = 10, delay_seconds: float = 0.1) -> float:
        total_value = 0.0

        for _ in range(number_of_measurements):
            total_value = total_value + self.get_power()
            time.sleep(delay_seconds)

        average_value = total_value / number_of_measurements

        return average_value


    def get_average_energy(self, number_of_measurements: int = 10, delay_seconds: float = 0.1) -> float:
        total_value = 0.0

        for _ in range(number_of_measurements):
            total_value = total_value + self.get_energy()
            time.sleep(delay_seconds)

        average_value = total_value / number_of_measurements

        return average_value
