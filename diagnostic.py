#!/usr/bin/env python3
"""Diagnostico del sistema IoT y de los sensores RS485 SEN0707 y SEN0710."""

import glob
import subprocess
import sys
import time

from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
from rs485_ec_sensor import (
    auto_detect_port,
    create_instrument,
    read_device_info as read_ec_device_info,
    read_measurements as read_ec_measurements,
)
from rs485_turbidity_sensor import (
    read_device_info as read_turbidity_device_info,
    read_measurements as read_turbidity_measurements,
)


VREF = 3.3
EC_SLAVE_ADDRESS = 1
EC_BAUDRATE = 4800
EC_TIMEOUT = 1.0

TURBIDITY_SLAVE_ADDRESS = 2
TURBIDITY_BAUDRATE = 4800
TURBIDITY_TIMEOUT = 1.0


def print_header(title):
    print('\n' + '=' * 70)
    print(f'  {title}')
    print('=' * 70)


def print_status(sensor_name, status, details=''):
    icon = 'OK' if status else 'FALLO'
    print(f'[{icon}] {sensor_name}')
    if details:
        print(f'  {details}')


def test_i2c():
    print_header('1. DISPOSITIVOS I2C DETECTADOS')
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True, check=False)
        print(result.stdout)
        found = '10' in result.stdout
        print_status('Placa DFRobot en 0x10', found, 'Revision del bus I2C 1')
        return found
    except Exception as e:
        print_status('i2cdetect', False, f'Error: {e}')
        return False


def test_board():
    print_header('2. PRUEBA DE PLACA DFROBOT')
    try:
        board = Board(1, 0x10)
        board.detecte()
        if board.begin() == board.STA_OK:
            board.set_adc_enable()
            print_status('Placa DFRobot', True, 'Bus I2C 1, direccion 0x10')
            return board
        print_status('Placa DFRobot', False, 'No se pudo inicializar')
        return None
    except Exception as e:
        print_status('Placa DFRobot', False, f'Error: {e}')
        return None


def test_analog_inputs(board):
    print_header('3. PRUEBA DE ENTRADAS ANALOGICAS')
    if board is None:
        print_status('Entradas analogicas', False, 'Placa no disponible')
        return

    try:
        for channel_name, channel in [('A0', board.A0), ('A1', board.A1), ('A2', board.A2), ('A3', board.A3)]:
            value = board.get_adc_value(channel)
            voltage = (value / 4095.0) * VREF
            print_status(channel_name, True, f'ADC={value}, Voltaje={voltage:.3f}V')
    except Exception as e:
        print_status('Entradas analogicas', False, f'Error: {e}')


def test_ph_sensor(board):
    print_header('4. PRUEBA DE SENSOR DE PH')
    if board is None:
        print_status('Sensor pH', False, 'Placa no disponible')
        return

    try:
        value = board.get_adc_value(board.A2)
        voltage = (value / 4095.0) * VREF
        ph = 7 + ((2.5 - voltage) / 0.18)
        print_status('Sensor pH A2', True, f'Voltaje={voltage:.3f}V, pH={ph:.2f}')
    except Exception as e:
        print_status('Sensor pH', False, f'Error: {e}')


def test_do_sensor(board):
    print_header('5. PRUEBA DE SENSOR DE OXIGENO DISUELTO')
    if board is None:
        print_status('Sensor O2', False, 'Placa no disponible')
        return

    try:
        value = board.get_adc_value(board.A3)
        voltage = (value / 4095.0) * VREF
        mg_l = (voltage / 3.0) * 20.0
        print_status('Sensor O2 A3', True, f'Voltaje={voltage:.3f}V, O2={mg_l:.2f} mg/L')
    except Exception as e:
        print_status('Sensor O2', False, f'Error: {e}')


def test_ds18b20():
    print_header('6. PRUEBA DE SENSOR DS18B20')
    try:
        devices = glob.glob('/sys/bus/w1/devices/28*')
        if not devices:
            print_status('Sensor DS18B20', False, 'No se detecto el dispositivo')
            return

        device_file = devices[0] + '/w1_slave'
        with open(device_file, 'r', encoding='utf-8') as handle:
            lines = handle.readlines()

        retry = 0
        while lines[0].strip()[-3:] != 'YES' and retry < 3:
            time.sleep(0.5)
            with open(device_file, 'r', encoding='utf-8') as handle:
                lines = handle.readlines()
            retry += 1

        equals_pos = lines[1].find('t=')
        if equals_pos == -1:
            print_status('Sensor DS18B20', False, 'No se encontro valor de temperatura')
            return

        temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
        print_status('Sensor DS18B20', True, f'Temperatura={temp_c:.2f}C')
    except Exception as e:
        print_status('Sensor DS18B20', False, f'Error: {e}')


def test_ec_sensor():
    print_header('7. PRUEBA DE SENSOR EC RS485 SEN0707')
    try:
        port = auto_detect_port()
        instrument = create_instrument(port, EC_SLAVE_ADDRESS, EC_BAUDRATE, EC_TIMEOUT)
        info = read_ec_device_info(instrument)
        data = read_ec_measurements(instrument)
        print_status('Puerto RS485', True, f'{port} (esperado slave {EC_SLAVE_ADDRESS})')
        print_status('Configuracion RS485', True, f"slave={info['slave_address']}, baudrate={info['baudrate']}")
        print_status(
            'Lectura SEN0707',
            True,
            (
                f"EC={data['ec_us_cm']} uS/cm, Temp={data['temperature_c']:.1f}C, "
                f"Salinidad={data['salinity_ppm']} ppm, TDS={data['tds_ppm']} ppm"
            ),
        )
    except Exception as e:
        print_status('Sensor EC RS485', False, f'Error: {e}')


def test_turbidity_sensor():
    print_header('8. PRUEBA DE SENSOR DE TURBIDEZ RS485 SEN0710')
    try:
        port = auto_detect_port()
        instrument = create_instrument(
            port,
            TURBIDITY_SLAVE_ADDRESS,
            TURBIDITY_BAUDRATE,
            TURBIDITY_TIMEOUT,
        )
        info = read_turbidity_device_info(instrument)
        data = read_turbidity_measurements(instrument)
        print_status('Puerto RS485', True, f'{port} (esperado slave {TURBIDITY_SLAVE_ADDRESS})')
        print_status('Configuracion RS485', True, f"slave={info['slave_address']}, baudrate={info['baudrate']}")
        print_status(
            'Lectura SEN0710',
            True,
            f"Turbidez={data['turbidity_ntu']:.1f} NTU, Temp={data['temperature_c']:.1f}C",
        )
    except Exception as e:
        print_status('Sensor de turbidez RS485', False, f'Error: {e}')


def test_mqtt_connection():
    print_header('9. PRUEBA DE CONEXION MQTT')
    try:
        import socket
        from paho.mqtt.client import Client as MQTTClient

        broker = '10.150.253.2'
        port = 1883

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((broker, port))
        sock.close()
        if result != 0:
            print_status('Conectividad MQTT', False, f'No se puede alcanzar {broker}:{port}')
            return

        connected = False

        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            connected = rc == 0

        client = MQTTClient('diagnostic-test')
        client.username_pw_set('mqtt-uleam', 'Mqtt-Uleam2025$')
        client.on_connect = on_connect
        client.connect(broker, port, keepalive=10)
        client.loop_start()
        time.sleep(2)
        client.disconnect()
        client.loop_stop()

        print_status('Autenticacion MQTT', connected, 'Credenciales del broker principal')
    except ImportError:
        print_status('paho-mqtt', False, 'No instalada. Ejecuta: pip3 install paho-mqtt')
    except Exception as e:
        print_status('Conexion MQTT', False, f'Error: {e}')


def main():
    print('\nDIAGNOSTICO DEL SISTEMA DE SENSORES IoT - ULEAM')
    test_i2c()
    board = test_board()
    test_analog_inputs(board)
    test_ph_sensor(board)
    test_do_sensor(board)
    test_ds18b20()
    test_ec_sensor()
    test_turbidity_sensor()
    test_mqtt_connection()
    print('\nDiagnostico completado')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nDiagnostico interrumpido por el usuario')
        sys.exit(0)
    except Exception as e:
        print(f'\nError inesperado durante el diagnostico: {e}')
        sys.exit(1)
