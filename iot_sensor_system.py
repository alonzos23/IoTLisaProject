#!/usr/bin/env python3
"""
Sistema de monitoreo IoT con sensores.
Incluye sensores analogicos, 1-Wire y RS485 (SEN0707).
"""

import argparse
import calendar
import glob
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
from rs485_ec_sensor import auto_detect_port, create_instrument, read_measurements


BROKER = '10.150.253.2'
PORT = 1883
USERNAME = 'mqtt-uleam'
PASSWORD = 'Mqtt-Uleam2025$'
USE_MQTT_V5 = False
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

DEVICE_SERIAL = 'ULEAMCENTRAL02'
LOCATION_SLUG = 'uleam'
TOPIC_DATA = f'iot_uleam/{LOCATION_SLUG}'

VREF = 3.3
DEFAULT_SAMPLE_INTERVAL = 3600
MAX_RETRIES = 3

EC_SLAVE_ADDRESS = 1
EC_BAUDRATE = 4800
EC_TIMEOUT = 1.0


def get_log_file_path() -> str:
    """Obtiene la ruta del archivo de log según permisos disponibles."""
    var_log_path = '/var/log/iot_sensor_system.log'
    try:
        with open(var_log_path, 'a', encoding='utf-8'):
            pass
        return var_log_path
    except PermissionError:
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, 'iot_logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'iot_sensor_system.log')


log_file = get_log_file_path()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)
logger.info(f'Archivo de log: {log_file}')


class SensorError(Exception):
    """Excepcion personalizada para errores de sensores."""


class MQTTPublisher:
    """Cliente MQTT con reconexion automatica."""

    def __init__(self):
        self.client = MQTTClient(
            client_id=CLIENT_ID,
            protocol=5 if USE_MQTT_V5 else 4,
        )
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"Conectado exitosamente al broker MQTT como '{CLIENT_ID}'")
            self.connected = True
        else:
            logger.error(f'Error al conectar MQTT: {rc}')
            self.connected = False

    def on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        if rc != 0:
            logger.warning('Desconexion inesperada de MQTT. Reconectando...')
        else:
            logger.info('Desconectado del broker MQTT')

    def on_publish(self, client, userdata, mid):
        logger.debug(f'Datos enviados al servidor MQTT (ID: {mid})')

    def connect(self):
        logger.info(f'Conectando a broker MQTT {BROKER}:{PORT}...')
        if USE_MQTT_V5:
            properties = Properties(PacketTypes.CONNECT)
            properties.SessionExpiryInterval = 3600
            self.client.connect(BROKER, PORT, keepalive=60, properties=properties)
        else:
            self.client.connect(BROKER, PORT, keepalive=60)
        self.client.loop_start()

    def build_message(self, sensor_data: Dict[str, Any]) -> str:
        now = datetime.now()
        message = {
            'Sensor': DEVICE_SERIAL,
            'temperatura': sensor_data.get('temperatura'),
            'ph': sensor_data.get('ph'),
            'oxigeno_disuelto': sensor_data.get('oxigeno_disuelto'),
            'potenciometro_1': sensor_data.get('potenciometro_1'),
            'potenciometro_2': sensor_data.get('potenciometro_2'),
            'ec_us_cm': sensor_data.get('ec_us_cm'),
            'ec_temperature_c': sensor_data.get('ec_temperature_c'),
            'salinity_ppm': sensor_data.get('salinity_ppm'),
            'tds_ppm': sensor_data.get('tds_ppm'),
            'timestamp': calendar.timegm(time.gmtime()),
            'dateTime': now.strftime('%d/%m/%Y %H:%M:%S'),
            'sensor_status': sensor_data.get('sensor_status', {}),
        }
        return json.dumps(message)

    def publish(self, topic: str, message: str) -> bool:
        if not self.connected:
            logger.warning('No conectado a MQTT, saltando envio...')
            return False
        try:
            result = self.client.publish(topic, payload=message, qos=1)
            if result.rc != 0:
                logger.error(f'Error al publicar en {topic}: {result.rc}')
                return False
            return True
        except Exception as e:
            logger.error(f'Error al publicar: {e}')
            return False

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()


class SensorManager:
    """Gestor de sensores del sistema."""

    def __init__(self, board: Board, ec_port: Optional[str] = None):
        self.board = board
        self.ec_port = ec_port
        self.ec_instrument = None
        self.ds18b20_device = None
        self.sensor_status = {
            'board': False,
            'temperature': False,
            'ph': False,
            'dissolved_oxygen': False,
            'potentiometer_1': False,
            'potentiometer_2': False,
            'ec_sensor': False,
        }

    def initialize_board(self) -> bool:
        try:
            self.board.detecte()
            retry_count = 0
            while self.board.begin() != self.board.STA_OK and retry_count < MAX_RETRIES:
                logger.warning(
                    f'Fallo al iniciar la placa, reintentando... ({retry_count + 1}/{MAX_RETRIES})'
                )
                time.sleep(2)
                retry_count += 1

            if self.board.begin() == self.board.STA_OK:
                logger.info('Placa iniciada correctamente')
                self.board.set_adc_enable()
                self.sensor_status['board'] = True
                return True

            logger.error('No se pudo inicializar la placa despues de varios intentos')
            return False
        except Exception as e:
            logger.error(f'Error al inicializar la placa: {e}')
            return False

    def detect_ds18b20(self) -> bool:
        try:
            base_dir = '/sys/bus/w1/devices/'
            logger.info('Buscando sensor DS18B20...')
            devices = glob.glob(base_dir + '28*')
            if not devices:
                logger.warning('No se detecto ningun sensor DS18B20.')
                self.sensor_status['temperature'] = False
                return False

            self.ds18b20_device = devices[0] + '/w1_slave'
            logger.info(f'Sensor detectado: {devices[0]}')
            self.sensor_status['temperature'] = True
            return True
        except Exception as e:
            logger.error(f'Error al detectar DS18B20: {e}')
            self.sensor_status['temperature'] = False
            return False

    def initialize_ec_sensor(self) -> bool:
        try:
            port = self.ec_port or auto_detect_port()
            instrument = create_instrument(port, EC_SLAVE_ADDRESS, EC_BAUDRATE, EC_TIMEOUT)
            read_measurements(instrument)
            self.ec_instrument = instrument
            self.ec_port = port
            self.sensor_status['ec_sensor'] = True
            logger.info(f'Sensor EC RS485 listo en {port}')
            return True
        except Exception as e:
            logger.warning(f'Sensor EC RS485 no disponible: {e}')
            self.ec_instrument = None
            self.sensor_status['ec_sensor'] = False
            return False

    def read_temperature(self) -> Optional[float]:
        if not self.ds18b20_device or not self.sensor_status['temperature']:
            return None

        try:
            with open(self.ds18b20_device, 'r', encoding='utf-8') as handle:
                lines = handle.readlines()

            retry_count = 0
            while lines[0].strip()[-3:] != 'YES' and retry_count < MAX_RETRIES:
                time.sleep(0.5)
                with open(self.ds18b20_device, 'r', encoding='utf-8') as handle:
                    lines = handle.readlines()
                retry_count += 1

            if lines[0].strip()[-3:] != 'YES':
                raise SensorError('No se obtuvieron datos validos del sensor de temperatura')

            equals_pos = lines[1].find('t=')
            if equals_pos == -1:
                raise SensorError('No se encontro el valor de temperatura en la lectura')

            temp_string = lines[1][equals_pos + 2:]
            return round(float(temp_string) / 1000.0, 2)
        except Exception as e:
            logger.error(f'Error al leer temperatura: {e}')
            self.sensor_status['temperature'] = False
            return None

    def read_adc_voltage(self, channel) -> Optional[float]:
        try:
            value = self.board.get_adc_value(channel)
            voltage = (value / 4095.0) * VREF
            return round(voltage, 2)
        except Exception as e:
            logger.error(f'Error al leer canal ADC: {e}')
            return None

    def read_ph(self) -> Optional[float]:
        try:
            voltage_ph = self.read_adc_voltage(self.board.A2)
            if voltage_ph is None:
                self.sensor_status['ph'] = False
                return None

            ph = 7 + ((2.5 - voltage_ph) / 0.18)
            self.sensor_status['ph'] = True
            return round(ph, 2)
        except Exception as e:
            logger.error(f'Error al leer pH: {e}')
            self.sensor_status['ph'] = False
            return None

    def read_dissolved_oxygen(self) -> Optional[float]:
        try:
            voltage_do = self.read_adc_voltage(self.board.A3)
            if voltage_do is None:
                self.sensor_status['dissolved_oxygen'] = False
                return None

            mg_l = (voltage_do / 3.0) * 20.0
            self.sensor_status['dissolved_oxygen'] = True
            return round(mg_l, 2)
        except Exception as e:
            logger.error(f'Error al leer oxigeno disuelto: {e}')
            self.sensor_status['dissolved_oxygen'] = False
            return None

    def read_ec_sensor(self) -> Dict[str, Optional[float]]:
        sensor_data = {
            'ec_us_cm': None,
            'ec_temperature_c': None,
            'salinity_ppm': None,
            'tds_ppm': None,
        }

        if not self.ec_instrument:
            self.sensor_status['ec_sensor'] = False
            return sensor_data

        try:
            data = read_measurements(self.ec_instrument)
            sensor_data['ec_us_cm'] = data['ec_us_cm']
            sensor_data['ec_temperature_c'] = data['temperature_c']
            sensor_data['salinity_ppm'] = data['salinity_ppm']
            sensor_data['tds_ppm'] = data['tds_ppm']
            self.sensor_status['ec_sensor'] = True
        except Exception as e:
            logger.error(f'Error al leer sensor EC RS485: {e}')
            self.sensor_status['ec_sensor'] = False

        return sensor_data

    def read_all_sensors(self) -> Dict[str, Any]:
        sensor_data = {
            'temperatura': None,
            'ph': None,
            'oxigeno_disuelto': None,
            'potenciometro_1': None,
            'potenciometro_2': None,
            'ec_us_cm': None,
            'ec_temperature_c': None,
            'salinity_ppm': None,
            'tds_ppm': None,
            'sensor_status': self.sensor_status.copy(),
        }

        voltage_a0 = self.read_adc_voltage(self.board.A0)
        voltage_a1 = self.read_adc_voltage(self.board.A1)

        if voltage_a0 is not None:
            sensor_data['potenciometro_1'] = voltage_a0
            self.sensor_status['potentiometer_1'] = True
        else:
            self.sensor_status['potentiometer_1'] = False

        if voltage_a1 is not None:
            sensor_data['potenciometro_2'] = voltage_a1
            self.sensor_status['potentiometer_2'] = True
        else:
            self.sensor_status['potentiometer_2'] = False

        ph = self.read_ph()
        if ph is not None:
            sensor_data['ph'] = ph

        oxygen = self.read_dissolved_oxygen()
        if oxygen is not None:
            sensor_data['oxigeno_disuelto'] = oxygen

        temperature = self.read_temperature()
        if temperature is not None:
            sensor_data['temperatura'] = temperature

        sensor_data.update(self.read_ec_sensor())
        sensor_data['sensor_status'] = self.sensor_status.copy()
        return sensor_data

    def print_sensor_readings(self, sensor_data: Dict[str, Any]):
        logger.info('=' * 60)
        logger.info('LECTURAS DE SENSORES')
        logger.info('=' * 60)

        if sensor_data['potenciometro_1'] is not None:
            logger.info(f"Potenciometro 1 (A0): {sensor_data['potenciometro_1']:.2f} V")
        else:
            logger.warning('Potenciometro 1: Error de lectura')

        if sensor_data['potenciometro_2'] is not None:
            logger.info(f"Potenciometro 2 (A1): {sensor_data['potenciometro_2']:.2f} V")
        else:
            logger.warning('Potenciometro 2: Error de lectura')

        if sensor_data['ph'] is not None:
            logger.info(f"Sensor pH (A2): pH estimado {sensor_data['ph']:.2f}")
        else:
            logger.warning('Sensor pH: Error de lectura')

        if sensor_data['oxigeno_disuelto'] is not None:
            logger.info(f"Oxigeno disuelto (A3): {sensor_data['oxigeno_disuelto']:.2f} mg/L")
        else:
            logger.warning('Sensor de oxigeno disuelto: Error de lectura')

        if sensor_data['temperatura'] is not None:
            logger.info(f"Temperatura DS18B20: {sensor_data['temperatura']:.2f} C")
        else:
            logger.warning('Sensor de temperatura DS18B20: Error de lectura')

        if sensor_data['ec_us_cm'] is not None:
            logger.info(
                'Sensor EC RS485: '
                f"EC={sensor_data['ec_us_cm']} uS/cm | "
                f"Salinidad={sensor_data['salinity_ppm']} ppm | "
                f"TDS={sensor_data['tds_ppm']} ppm | "
                f"Temp={sensor_data['ec_temperature_c']:.1f} C"
            )
        else:
            logger.warning('Sensor EC RS485: Error de lectura')

        logger.info('=' * 60)


def main(sample_interval: int = DEFAULT_SAMPLE_INTERVAL, ec_port: Optional[str] = None):
    logger.info('Iniciando sistema de monitoreo IoT')
    logger.info(f'Intervalo de muestreo: {sample_interval} segundos')

    try:
        board = Board(1, 0x10)
    except Exception as e:
        logger.error(f'Error al crear objeto Board: {e}')
        sys.exit(1)

    sensor_manager = SensorManager(board, ec_port=ec_port)
    if not sensor_manager.initialize_board():
        logger.error('No se pudo inicializar la placa. Terminando programa.')
        sys.exit(1)

    sensor_manager.detect_ds18b20()
    sensor_manager.initialize_ec_sensor()

    mqtt_client = MQTTPublisher()
    try:
        mqtt_client.connect()
        time.sleep(2)
    except Exception as e:
        logger.error(f'Error al conectar MQTT: {e}')
        logger.warning('Continuando sin conexion MQTT...')

    try:
        while True:
            start_time = time.time()
            sensor_data = sensor_manager.read_all_sensors()
            sensor_manager.print_sensor_readings(sensor_data)

            if any(value is not None for key, value in sensor_data.items() if key != 'sensor_status'):
                mqtt_message = mqtt_client.build_message(sensor_data)
                logger.info(f'Enviando datos: {mqtt_message}')
                mqtt_client.publish(TOPIC_DATA, mqtt_message)
            else:
                logger.warning('No hay datos validos para enviar')

            elapsed_time = time.time() - start_time
            sleep_time = max(0, sample_interval - elapsed_time)
            if sleep_time > 0:
                logger.info(f'Esperando {sleep_time:.1f} segundos hasta el proximo muestreo...')
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.info('Lectura finalizada por el usuario.')
    except Exception as e:
        logger.error(f'Error inesperado: {e}', exc_info=True)
    finally:
        mqtt_client.disconnect()
        logger.info('Programa finalizado correctamente.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sistema de monitoreo IoT con sensores')
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=DEFAULT_SAMPLE_INTERVAL,
        help=f'Intervalo de muestreo en segundos (por defecto: {DEFAULT_SAMPLE_INTERVAL})',
    )
    parser.add_argument(
        '--ec-port',
        help='Puerto serie del sensor EC RS485, por ejemplo /dev/ttyUSB0',
    )

    args = parser.parse_args()
    if args.interval < 1:
        logger.error('El intervalo debe ser mayor o igual a 1 segundo')
        sys.exit(1)

    main(sample_interval=args.interval, ec_port=args.ec_port)
