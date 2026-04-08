import numpy
import pyvisa
import time

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


class Oscilloscope:
    def __init__(self):
        self.instrument = None
        self.resource_manager = None
        self.is_connected = False
        self.timeout_milliseconds = 30000


    def connect(self, resource_string: str = None) -> bool:
        status = False

        try:
            self.resource_manager = pyvisa.ResourceManager('@py')

            if resource_string:
                self.instrument = self.resource_manager.open_resource(resource_string)
            else:
                available_resources = self.resource_manager.list_resources()

                for single_resource in available_resources:
                    if 'USB' in single_resource:
                        try:
                            temporary_instrument = self.resource_manager.open_resource(single_resource)
                            temporary_instrument.timeout = self.timeout_milliseconds
                            temporary_instrument.read_termination = '\n'
                            temporary_instrument.write_termination = '\n'
                            identification_string = temporary_instrument.query('*IDN?')

                            if 'AGILENT' in identification_string.upper() or 'KEYSIGHT' in identification_string.upper():
                                self.instrument = temporary_instrument

                                break

                            temporary_instrument.close()
                        except:
                            continue

            if self.instrument is not None:
                self.is_connected = True
                status = True
        except Exception as error:
            pass

        return status


    def disconnect(self):
        if self.instrument:
            self.instrument.close()

        if self.resource_manager:
            self.resource_manager.close()

        self.is_connected = False


    def set_timeout(self, milliseconds: int):
        self.timeout_milliseconds = milliseconds

        if self.instrument:
            self.instrument.timeout = milliseconds


    def identification(self) -> str:
        identification_string = self.instrument.query('*IDN?')

        return identification_string


    def reset(self):
        self.instrument.write('*RST')
        time.sleep(1)


    def self_test(self) -> bool:
        test_result = self.instrument.query('*TST?') == '0'

        return test_result


    def clear_status(self):
        self.instrument.write('*CLS')


    def get_error(self) -> str:
        error_message = self.instrument.query(':SYSTem:ERRor?')

        return error_message


    def wait_for_operation_complete(self):
        self.instrument.query('*OPC?')


    def set_channel_display(self, channel_number: int, enable_status: bool):
        self.instrument.write(f':CHANnel{channel_number}:DISPlay {1 if enable_status else 0}')


    def get_channel_display(self, channel_number: int) -> bool:
        display_status = self.instrument.query(f':CHANnel{channel_number}:DISPlay?') == '1'

        return display_status


    def set_channel_scale(self, channel_number: int, scale_volts: float):
        self.instrument.write(f':CHANnel{channel_number}:SCALe {scale_volts}')


    def get_channel_scale(self, channel_number: int) -> float:
        scale_value = float(self.instrument.query(f':CHANnel{channel_number}:SCALe?'))

        return scale_value


    def set_channel_offset(self, channel_number: int, offset_volts: float):
        self.instrument.write(f':CHANnel{channel_number}:OFFSet {offset_volts}')


    def get_channel_offset(self, channel_number: int) -> float:
        offset_value = float(self.instrument.query(f':CHANnel{channel_number}:OFFSet?'))

        return offset_value


    def set_channel_coupling(self, channel_number: int, coupling_type: str):
        self.instrument.write(f':CHANnel{channel_number}:COUPling {coupling_type}')


    def get_channel_coupling(self, channel_number: int) -> str:
        coupling_value = self.instrument.query(f':CHANnel{channel_number}:COUPling?').strip()

        return coupling_value


    def set_channel_impedance(self, channel_number: int, impedance_ohms: float):
        self.instrument.write(f':CHANnel{channel_number}:IMPedance {impedance_ohms}')


    def get_channel_impedance(self, channel_number: int) -> float:
        impedance_value = float(self.instrument.query(f':CHANnel{channel_number}:IMPedance?'))

        return impedance_value


    def set_channel_probe(self, channel_number: int, attenuation_factor: float):
        self.instrument.write(f':CHANnel{channel_number}:PROBe {attenuation_factor}')


    def get_channel_probe(self, channel_number: int) -> float:
        attenuation_value = float(self.instrument.query(f':CHANnel{channel_number}:PROBe?'))

        return attenuation_value


    def set_channel_invert(self, channel_number: int, invert_status: bool):
        self.instrument.write(f':CHANnel{channel_number}:INVert {1 if invert_status else 0}')


    def get_channel_invert(self, channel_number: int) -> bool:
        invert_status = self.instrument.query(f':CHANnel{channel_number}:INVert?') == '1'

        return invert_status


    def set_channel_bandwidth(self, channel_number: int, bandwidth_limit: str):
        self.instrument.write(f':CHANnel{channel_number}:BANDwidth {bandwidth_limit}')


    def get_channel_bandwidth(self, channel_number: int) -> str:
        bandwidth_value = self.instrument.query(f':CHANnel{channel_number}:BANDwidth?').strip()

        return bandwidth_value


    def set_channel_label(self, channel_number: int, label_text: str):
        self.instrument.write(f':CHANnel{channel_number}:LABel "{label_text}"')


    def get_channel_label(self, channel_number: int) -> str:
        label_value = self.instrument.query(f':CHANnel{channel_number}:LABel?').strip().strip('"')

        return label_value


    def auto_scale(self):
        self.instrument.write(':AUToscale')


    def set_timebase_scale(self, seconds_per_division: float):
        self.instrument.write(f':TIMebase:SCALe {seconds_per_division}')


    def get_timebase_scale(self) -> float:
        scale_value = float(self.instrument.query(':TIMebase:SCALe?'))

        return scale_value


    def set_timebase_delay(self, delay_seconds: float):
        self.instrument.write(f':TIMebase:DELay {delay_seconds}')


    def get_timebase_delay(self) -> float:
        delay_value = float(self.instrument.query(':TIMebase:DELay?'))

        return delay_value


    def set_timebase_reference(self, reference_position: str):
        self.instrument.write(f':TIMebase:REFerence {reference_position}')


    def get_timebase_reference(self) -> str:
        reference_value = self.instrument.query(':TIMebase:REFerence?').strip()

        return reference_value


    def set_timebase_mode(self, mode_type: str):
        self.instrument.write(f':TIMebase:MODE {mode_type}')


    def get_timebase_mode(self) -> str:
        mode_value = self.instrument.query(':TIMebase:MODE?').strip()

        return mode_value


    def run_acquisition(self):
        self.instrument.write(':RUN')


    def stop_acquisition(self):
        self.instrument.write(':STOP')


    def single_acquisition(self):
        self.instrument.write(':SINGle')


    def force_trigger(self):
        self.instrument.write(':TRIGger:FORCe')


    def set_trigger_source(self, source_channel: str):
        self.instrument.write(f':TRIGger:SOURce {source_channel}')


    def get_trigger_source(self) -> str:
        source_value = self.instrument.query(':TRIGger:SOURce?').strip()

        return source_value


    def set_trigger_level(self, level_volts: float):
        self.instrument.write(f':TRIGger:LEVel {level_volts}')


    def get_trigger_level(self) -> float:
        level_value = float(self.instrument.query(':TRIGger:LEVel?'))

        return level_value


    def set_trigger_slope(self, slope_direction: str):
        self.instrument.write(f':TRIGger:SLOPe {slope_direction}')


    def get_trigger_slope(self) -> str:
        slope_value = self.instrument.query(':TRIGger:SLOPe?').strip()

        return slope_value


    def set_trigger_mode(self, mode_type: str):
        self.instrument.write(f':TRIGger:MODE {mode_type}')


    def get_trigger_mode(self) -> str:
        mode_value = self.instrument.query(':TRIGger:MODE?').strip()

        return mode_value


    def set_trigger_coupling(self, coupling_type: str):
        self.instrument.write(f':TRIGger:COUPling {coupling_type}')


    def get_trigger_coupling(self) -> str:
        coupling_value = self.instrument.query(':TRIGger:COUPling?').strip()

        return coupling_value


    def set_trigger_holdoff(self, holdoff_seconds: float):
        self.instrument.write(f':TRIGger:HOLDoff {holdoff_seconds}')


    def get_trigger_holdoff(self) -> float:
        holdoff_value = float(self.instrument.query(':TRIGger:HOLDoff?'))

        return holdoff_value


    def set_acquire_type(self, acquisition_type: str):
        self.instrument.write(f':ACQuire:TYPE {acquisition_type}')


    def get_acquire_type(self) -> str:
        type_value = self.instrument.query(':ACQuire:TYPE?').strip()

        return type_value


    def set_acquire_type_normal(self):
        self.set_acquire_type('NORMal')


    def set_acquire_type_average(self):
        self.set_acquire_type('AVERage')


    def set_acquire_type_peak(self):
        self.set_acquire_type('PEAK')


    def set_acquire_type_high_resolution(self):
        self.set_acquire_type('HRESolution')


    def set_average_count(self, number_of_averages: int):
        self.instrument.write(f':ACQuire:COUNt {number_of_averages}')


    def get_average_count(self) -> int:
        count_value = int(self.instrument.query(':ACQuire:COUNt?'))

        return count_value


    def set_acquire_complete(self, completion_percent: int = 100):
        self.instrument.write(f':ACQuire:COMPlete {completion_percent}')


    def get_acquire_complete(self) -> int:
        percent_value = int(self.instrument.query(':ACQuire:COMPlete?'))

        return percent_value


    def measure(self, parameter_name: str, channel_number: int = 1, timeout_milliseconds: int = 5000) -> Optional[float]:
        result_value = None

        valid_parameters = [
            'VPP',
            'VMAX',
            'VMIN',
            'VRMS',
            'FREQuency',
            'PERiod',
            'RISetime',
            'FALLtime',
            'PWIDth',
            'NWIDth',
            'DUTYcycle',
            'MEAN',
            'RMS',
            'OVERS',
            'PREShoot',
            'DELay',
            'PHASe'
        ]

        if parameter_name.upper() in valid_parameters:
            try:
                old_timeout = self.instrument.timeout
                self.instrument.timeout = timeout_milliseconds
                self.instrument.write(f':MEASure:{parameter_name}? CHAN{channel_number}')
                time.sleep(0.3)
                measurement_result = self.instrument.query(':MEASure:RESult?')
                self.instrument.timeout = old_timeout
                result_value = float(measurement_result) if measurement_result else None
            except:
                result_value = None

        return result_value


    def measure_peak_to_peak(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('VPP', channel_number)

        return result_value


    def measure_maximum(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('VMAX', channel_number)

        return result_value


    def measure_minimum(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('VMIN', channel_number)

        return result_value


    def measure_rms(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('VRMS', channel_number)

        return result_value


    def measure_frequency(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('FREQuency', channel_number)

        return result_value


    def measure_period(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('PERiod', channel_number)

        return result_value


    def measure_rise_time(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('RISetime', channel_number)

        return result_value


    def measure_fall_time(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('FALLtime', channel_number)

        return result_value


    def measure_positive_width(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('PWIDth', channel_number)

        return result_value


    def measure_negative_width(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('NWIDth', channel_number)

        return result_value


    def measure_duty_cycle(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('DUTYcycle', channel_number)

        return result_value


    def measure_mean(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('MEAN', channel_number)

        return result_value


    def measure_rms_ac(self, channel_number: int = 1) -> Optional[float]:
        result_value = self.measure('RMS', channel_number)

        return result_value


    def measure_phase(self, source_one: str = 'CHAN1', source_two: str = 'CHAN2') -> Optional[float]:
        result_value = None

        try:
            self.instrument.write(f':MEASure:PHASe? {source_one},{source_two}')
            time.sleep(0.3)
            phase_result = self.instrument.query(':MEASure:RESult?')
            result_value = float(phase_result) if phase_result else None
        except:
            result_value = None

        return result_value


    def measure_delay(self, source_one: str = 'CHAN1', source_two: str = 'CHAN2') -> Optional[float]:
        result_value = None

        try:
            self.instrument.write(f':MEASure:DELay? {source_one},{source_two}')
            time.sleep(0.3)
            delay_result = self.instrument.query(':MEASure:RESult?')
            result_value = float(delay_result) if delay_result else None
        except:
            result_value = None

        return result_value


    def set_cursor_mode(self, cursor_mode: str):
        self.instrument.write(f':CURSor:MODE {cursor_mode}')


    def get_cursor_mode(self) -> str:
        mode_value = self.instrument.query(':CURSor:MODE?').strip()

        return mode_value


    def set_cursor_position(self, cursor_name: str, position_value: float):
        self.instrument.write(f':CURSor:{cursor_name} {position_value}')


    def get_cursor_position(self, cursor_name: str) -> float:
        position_value = float(self.instrument.query(f':CURSor:{cursor_name}?'))

        return position_value


    def get_cursor_delta(self) -> Dict[str, float]:
        delta_x = float(self.instrument.query(':CURSor:XDELta?'))
        delta_y = float(self.instrument.query(':CURSor:YDELta?'))
        inverse_delta_x = float(self.instrument.query(':CURSor:INVXDELta?'))

        delta_values = {
            'delta_x': delta_x,
            'delta_y': delta_y,
            'inverse_delta_x': inverse_delta_x
        }

        return delta_values


    def set_math_function(self, math_function: str):
        self.instrument.write(f':MATH:FUNCtion {math_function}')


    def get_math_function(self) -> str:
        function_value = self.instrument.query(':MATH:FUNCtion?').strip()

        return function_value


    def set_math_source(self, source_one: str, source_two: str = None):
        self.instrument.write(f':MATH:SOURce1 {source_one}')

        if source_two:
            self.instrument.write(f':MATH:SOURce2 {source_two}')


    def set_math_scale(self, scale_value: float):
        self.instrument.write(f':MATH:SCALe {scale_value}')


    def get_math_scale(self) -> float:
        scale_value = float(self.instrument.query(':MATH:SCALe?'))

        return scale_value


    def set_math_offset(self, offset_value: float):
        self.instrument.write(f':MATH:OFFSet {offset_value}')


    def get_math_offset(self) -> float:
        offset_value = float(self.instrument.query(':MATH:OFFSet?'))

        return offset_value


    def set_math_fft_window(self, window_type: str):
        self.instrument.write(f':MATH:FFT:WINDow {window_type}')


    def acquire_waveform(self, channel_number: int = 1, points_count: int = 2000, binary_format: bool = False) -> Tuple[List[float], List[float]]:
        result_value = ([], [])

        if self.is_connected:
            try:
                self.instrument.write(f':CHANnel{channel_number}:DISPlay 1')
                time.sleep(0.05)

                self.instrument.write(f':WAVeform:SOURce CHAN{channel_number}')

                if binary_format:
                    self.instrument.write(':WAVeform:FORMat WORD')
                    self.instrument.write(':WAVeform:BYTeorder LSBFirst')
                    data_type = 'h'
                else:
                    self.instrument.write(':WAVeform:FORMat ASCII')
                    data_type = None

                self.instrument.write(f':WAVeform:POINts {points_count}')
                self.instrument.write(f':DIGitize CHAN{channel_number}')
                time.sleep(0.3)

                x_increment = float(self.instrument.query(':WAVeform:XINCrement?'))
                x_origin = float(self.instrument.query(':WAVeform:XORigin?'))
                y_increment = float(self.instrument.query(':WAVeform:YINCrement?'))
                y_origin = float(self.instrument.query(':WAVeform:YORigin?'))

                if binary_format:
                    binary_data = self.instrument.query_binary_values(':WAVeform:DATA?', datatype=data_type)
                    voltage_values = [(value - y_origin) * y_increment for value in binary_data]
                else:
                    ascii_data = self.instrument.query(':WAVeform:DATA?')

                    if ascii_data.startswith('#'):
                        header_length = int(ascii_data[1])
                        ascii_data = ascii_data[2 + header_length:]

                    voltage_values = [float(value) for value in ascii_data.strip().split(',')]

                time_axis = [x_origin + x_increment * index for index in range(len(voltage_values))]
                result_value = (time_axis, voltage_values)

            except Exception as error:
                result_value = ([], [])

        return result_value


    def acquire_waveform_binary(self, channel_number: int = 1, points_count: int = 2000) -> Tuple[List[float], List[float]]:
        time_axis, voltage_values = self.acquire_waveform(channel_number, points_count, binary_format=True)
        result_value = (time_axis, voltage_values)

        return result_value


    def get_waveform_preamble(self) -> Dict[str, Any]:
        preamble_data = self.instrument.query(':WAVeform:PREamble?').split(',')

        preamble_parameters = {
            'format_code': int(preamble_data[0]),
            'acquisition_type': int(preamble_data[1]),
            'points_count': int(preamble_data[2]),
            'average_count': int(preamble_data[3]),
            'x_increment': float(preamble_data[4]),
            'x_origin': float(preamble_data[5]),
            'x_reference': float(preamble_data[6]),
            'y_increment': float(preamble_data[7]),
            'y_origin': float(preamble_data[8]),
            'y_reference': float(preamble_data[9])
        }

        return preamble_parameters


    def set_segment_count(self, segment_quantity: int):
        self.instrument.write(f':ACQuire:SEGMent:COUNt {segment_quantity}')


    def get_segment_count(self) -> int:
        segment_quantity = int(self.instrument.query(':ACQuire:SEGMent:COUNt?'))

        return segment_quantity


    def set_segment_index(self, segment_index_number: int):
        self.instrument.write(f':ACQuire:SEGMent:INDex {segment_index_number}')


    def get_segment(self, segment_index_number: int, channel_number: int = 1) -> Tuple[List[float], List[float]]:
        self.set_segment_index(segment_index_number)
        time_axis, voltage_values = self.acquire_waveform(channel_number)
        result_value = (time_axis, voltage_values)

        return result_value


    def load_mask(self, file_name: str):
        self.instrument.write(f':MASK:LOAD "{file_name}"')


    def check_mask(self) -> bool:
        mask_status = self.instrument.query(':MASK:FAIL?') == '1'

        return mask_status


    def get_mask_fail_count(self) -> int:
        fail_count = int(self.instrument.query(':MASK:COUNt?'))

        return fail_count


    def clear_mask_fail_count(self):
        self.instrument.write(':MASK:CLEar')


    def save_screenshot(self, file_name: str = None) -> str:
        self.instrument.write(':DISPlay:DATA? PNG')
        image_data = self.instrument.read_raw()

        if file_name is None:
            file_name = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"

        with open(file_name, 'wb') as file_handle:
            if image_data.startswith(b'#'):
                header_length = int(chr(image_data[1]))
                image_data = image_data[2 + header_length:]

            file_handle.write(image_data)

        return file_name


    def save_setup(self, memory_location: str = '1'):
        self.instrument.write(f':SAVE:SETup {memory_location}')


    def recall_setup(self, memory_location: str = '1'):
        self.instrument.write(f':RECall:SETup {memory_location}')


    def export_waveform_to_csv(self, file_name: str, channel_number: int = 1):
        self.instrument.write(f':EXPort:WAVeform:SOURce CHAN{channel_number}')
        self.instrument.write(f':EXPort:WAVeform:STARt "{file_name}"')


    def get_ip_address(self) -> str:
        ip_address = self.instrument.query(':SYSTem:COMMunicate:LAN:IPADdress?').strip()

        return ip_address


    def set_ip_address(self, ip_address: str):
        self.instrument.write(f':SYSTem:COMMunicate:LAN:IPADdress "{ip_address}"')


    def get_mac_address(self) -> str:
        mac_address = self.instrument.query(':SYSTem:COMMunicate:LAN:MAC?').strip()

        return mac_address


    def get_all_settings(self) -> Dict[str, Any]:
        all_settings = {
            'identification': self.identification(),
            'timebase_scale': self.get_timebase_scale(),
            'timebase_delay': self.get_timebase_delay(),
            'timebase_mode': self.get_timebase_mode(),
            'acquire_type': self.get_acquire_type(),
            'average_count': self.get_average_count(),
            'trigger_source': self.get_trigger_source(),
            'trigger_level': self.get_trigger_level(),
            'trigger_slope': self.get_trigger_slope(),
        }

        for channel_index in range(1, 5):
            all_settings[f'channel_{channel_index}_display'] = self.get_channel_display(channel_index)
            all_settings[f'channel_{channel_index}_scale'] = self.get_channel_scale(channel_index)
            all_settings[f'channel_{channel_index}_offset'] = self.get_channel_offset(channel_index)
            all_settings[f'channel_{channel_index}_coupling'] = self.get_channel_coupling(channel_index)

        return all_settings


    def get_signal_statistics(self, channel_number: int = 1) -> Dict[str, float]:
        statistics = {}
        _, voltage_values = self.acquire_waveform(channel_number)

        if voltage_values:
            statistics = {
                'points_count': len(voltage_values),
                'maximum_voltage': max(voltage_values),
                'minimum_voltage': min(voltage_values),
                'peak_to_peak_voltage': max(voltage_values) - min(voltage_values),
                'average_voltage': sum(voltage_values) / len(voltage_values),
                'standard_deviation': float(numpy.std(voltage_values)) if len(voltage_values) > 1 else 0
            }

        return statistics


    def get_device_information(self) -> Dict[str, str]:
        device_info = {
            'manufacturer': self.instrument.query(':SYSTem:INFo:MANufacturer?').strip(),
            'model_number': self.instrument.query(':SYSTem:INFo:MODeL?').strip(),
            'serial_number': self.instrument.query(':SYSTem:INFo:SERial?').strip(),
            'firmware_version': self.instrument.query(':SYSTem:INFo:Firmware?').strip()
        }

        return device_info
