#!/usr/bin/env python3
"""
Sistema de monitoreo IoT con sensores
Versión mejorada con manejo de errores y configuración flexible
"""

import sys
import time
import glob
import json
import random
import logging
import argparse
from datetime import datetime
from typing import Optional, Dict, Any
import calendar

# Importar librería MQTT
from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

# Importar librería de la placa DFRobot
from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board

# === Configuración de logging ===
import os

# Determinar la ruta del archivo de log basado en permisos
def get_log_file_path():
    """Obtiene la ruta del archivo de log según permisos disponibles"""
    # Intentar /var/log primero (si se ejecuta como root/servicio)
    var_log_path = '/var/log/iot_sensor_system.log'
    try:
        # Intentar crear/abrir el archivo
        with open(var_log_path, 'a') as f:
            pass
        return var_log_path
    except PermissionError:
        # Si no hay permisos, usar directorio home del usuario
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, 'iot_logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'iot_sensor_system.log')

log_file = get_log_file_path()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"📝 Archivo de log: {log_file}")

# === Configuración MQTT ===
BROKER = '10.150.253.2'
PORT = 1883
USERNAME = 'mqtt-uleam'
PASSWORD = 'Mqtt-Uleam2025$'
USE_MQTT_V5 = False
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

# === Datos del dispositivo ===
DEVICE_SERIAL = "ULEAMCENTRAL02"
LOCATION_SLUG = "uleam"
TOPIC_DATA = f"iot_uleam/{LOCATION_SLUG}"

# === Configuración de sensores ===
VREF = 3.3  # Voltaje de referencia
DEFAULT_SAMPLE_INTERVAL = 3600  # 1 hora por defecto
MAX_RETRIES = 3  # Reintentos para lecturas fallidas
SENSOR_TIMEOUT = 5  # Timeout para lecturas en segundos


class SensorError(Exception):
    """Excepción personalizada para errores de sensores"""
    pass


class MQTTPublisher:
    """Cliente MQTT con reconexión automática y manejo de errores"""
    
    def __init__(self):
        self.client = MQTTClient(
            client_id=CLIENT_ID,
            protocol=5 if USE_MQTT_V5 else 4
        )
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"✅ Conectado exitosamente al broker MQTT como '{CLIENT_ID}'")
            self.connected = True
        else:
            logger.error(f"❌ Error al conectar MQTT: {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        if rc != 0:
            logger.warning("⚠️ Desconexión inesperada de MQTT. Reconectando...")
        else:
            logger.info("🔌 Desconectado del broker MQTT")

    def on_publish(self, client, userdata, mid):
        logger.debug(f"📤 Datos enviados al servidor MQTT (ID: {mid})")

    def connect(self):
        try:
            logger.info(f"🔌 Conectando a broker MQTT {BROKER}:{PORT}...")
            if USE_MQTT_V5:
                properties = Properties(PacketTypes.CONNECT)
                properties.SessionExpiryInterval = 3600
                self.client.connect(BROKER, PORT, keepalive=60, properties=properties)
            else:
                self.client.connect(BROKER, PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"❌ Error al conectar MQTT: {e}")
            raise

    def build_message(self, sensor_data: Dict[str, Any]) -> str:
        """Construye el mensaje JSON con datos de los sensores"""
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M:%S")

        message = {
            "Sensor": DEVICE_SERIAL,
            "temperatura": sensor_data.get('temperatura'),
            "ph": sensor_data.get('ph'),
            "oxigeno_disuelto": sensor_data.get('oxigeno_disuelto'),
            "potenciometro_1": sensor_data.get('potenciometro_1'),
            "potenciometro_2": sensor_data.get('potenciometro_2'),
            "timestamp": calendar.timegm(time.gmtime()),
            "dateTime": date_time,
            "sensor_status": sensor_data.get('sensor_status', {})
        }
        return json.dumps(message)

    def publish(self, topic: str, message: str) -> bool:
        """Publica un mensaje en el topic especificado"""
        if not self.connected:
            logger.warning("⚠️ No conectado a MQTT, saltando envío...")
            return False
        try:
            result = self.client.publish(topic, payload=message, qos=1)
            if result.rc != 0:
                logger.error(f"❌ Error al publicar en {topic}: {result.rc}")
                return False
            return True
        except Exception as e:
            logger.error(f"❌ Error al publicar: {e}")
            return False

    def disconnect(self):
        """Desconecta el cliente MQTT"""
        self.client.disconnect()
        self.client.loop_stop()


class SensorManager:
    """Gestor de sensores con manejo de errores y reintentos"""
    
    def __init__(self, board: Board):
        self.board = board
        self.sensor_status = {
            'board': False,
            'temperature': False,
            'ph': False,
            'dissolved_oxygen': False,
            'potentiometer_1': False,
            'potentiometer_2': False
        }
        self.ds18b20_device = None
        
    def initialize_board(self) -> bool:
        """Inicializa la placa DFRobot"""
        try:
            self.board.detecte()
            retry_count = 0
            while self.board.begin() != self.board.STA_OK and retry_count < MAX_RETRIES:
                logger.warning(f"Fallo al iniciar la placa, reintentando... ({retry_count + 1}/{MAX_RETRIES})")
                time.sleep(2)
                retry_count += 1
            
            if self.board.begin() == self.board.STA_OK:
                logger.info("✅ Placa iniciada correctamente")
                self.board.set_adc_enable()
                self.sensor_status['board'] = True
                return True
            else:
                logger.error("❌ No se pudo inicializar la placa después de varios intentos")
                return False
        except Exception as e:
            logger.error(f"❌ Error al inicializar la placa: {e}")
            return False

    def detect_ds18b20(self) -> bool:
        """Detecta el sensor de temperatura DS18B20"""
        try:
            base_dir = '/sys/bus/w1/devices/'
            logger.info("🔍 Buscando sensor DS18B20...")
            dispositivos = glob.glob(base_dir + '28*')
            
            if not dispositivos:
                logger.warning("⚠️ No se detectó ningún sensor DS18B20.")
                self.sensor_status['temperature'] = False
                return False
            
            self.ds18b20_device = dispositivos[0] + '/w1_slave'
            logger.info(f"✅ Sensor detectado: {dispositivos[0]}")
            self.sensor_status['temperature'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Error al detectar DS18B20: {e}")
            self.sensor_status['temperature'] = False
            return False

    def read_temperature(self) -> Optional[float]:
        """Lee la temperatura del sensor DS18B20"""
        if not self.ds18b20_device or not self.sensor_status['temperature']:
            return None
        
        try:
            with open(self.ds18b20_device, 'r') as f:
                lines = f.readlines()
            
            # Verificar que la lectura es válida
            retry_count = 0
            while lines[0].strip()[-3:] != 'YES' and retry_count < MAX_RETRIES:
                logger.debug("⏳ Esperando datos válidos del sensor de temperatura...")
                time.sleep(0.5)
                with open(self.ds18b20_device, 'r') as f:
                    lines = f.readlines()
                retry_count += 1
            
            if lines[0].strip()[-3:] != 'YES':
                raise SensorError("No se obtuvieron datos válidos del sensor de temperatura")
            
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return round(temp_c, 2)
            else:
                raise SensorError("No se encontró el valor de temperatura en la lectura")
                
        except Exception as e:
            logger.error(f"❌ Error al leer temperatura: {e}")
            self.sensor_status['temperature'] = False
            return None

    def read_adc_voltage(self, channel) -> Optional[float]:
        """Lee el voltaje de un canal ADC específico"""
        try:
            valor = self.board.get_adc_value(channel)
            voltaje = (valor / 4095.0) * VREF
            return round(voltaje, 2)
        except Exception as e:
            logger.error(f"❌ Error al leer canal ADC: {e}")
            return None

    def read_ph(self) -> Optional[float]:
        """Lee el sensor de pH conectado al canal A2"""
        try:
            voltaje_ph = self.read_adc_voltage(self.board.A2)
            if voltaje_ph is None:
                self.sensor_status['ph'] = False
                return None
            
            # Fórmula de conversión de voltaje a pH
            ph = 7 + ((2.5 - voltaje_ph) / 0.18)
            self.sensor_status['ph'] = True
            return round(ph, 2)
        except Exception as e:
            logger.error(f"❌ Error al leer pH: {e}")
            self.sensor_status['ph'] = False
            return None

    def read_dissolved_oxygen(self) -> Optional[float]:
        """Lee el sensor de oxígeno disuelto conectado al canal A3"""
        try:
            voltaje_do = self.read_adc_voltage(self.board.A3)
            if voltaje_do is None:
                self.sensor_status['dissolved_oxygen'] = False
                return None
            
            # Fórmula de conversión de voltaje a mg/L
            mg_L = (voltaje_do / 3.0) * 20.0
            self.sensor_status['dissolved_oxygen'] = True
            return round(mg_L, 2)
        except Exception as e:
            logger.error(f"❌ Error al leer oxígeno disuelto: {e}")
            self.sensor_status['dissolved_oxygen'] = False
            return None

    def read_all_sensors(self) -> Dict[str, Any]:
        """Lee todos los sensores de forma sincronizada"""
        sensor_data = {
            'temperatura': None,
            'ph': None,
            'oxigeno_disuelto': None,
            'potenciometro_1': None,
            'potenciometro_2': None,
            'sensor_status': self.sensor_status.copy()
        }
        
        # Leer potenciómetros
        voltaje_a0 = self.read_adc_voltage(self.board.A0)
        voltaje_a1 = self.read_adc_voltage(self.board.A1)
        
        if voltaje_a0 is not None:
            sensor_data['potenciometro_1'] = voltaje_a0
            self.sensor_status['potentiometer_1'] = True
        else:
            self.sensor_status['potentiometer_1'] = False
            
        if voltaje_a1 is not None:
            sensor_data['potenciometro_2'] = voltaje_a1
            self.sensor_status['potentiometer_2'] = True
        else:
            self.sensor_status['potentiometer_2'] = False
        
        # Leer pH
        ph = self.read_ph()
        if ph is not None:
            sensor_data['ph'] = ph
        
        # Leer oxígeno disuelto
        oxigeno = self.read_dissolved_oxygen()
        if oxigeno is not None:
            sensor_data['oxigeno_disuelto'] = oxigeno
        
        # Leer temperatura
        temp = self.read_temperature()
        if temp is not None:
            sensor_data['temperatura'] = temp
        
        return sensor_data

    def print_sensor_readings(self, sensor_data: Dict[str, Any]):
        """Imprime las lecturas de los sensores"""
        logger.info("=" * 60)
        logger.info("📊 LECTURAS DE SENSORES")
        logger.info("=" * 60)
        
        if sensor_data['potenciometro_1'] is not None:
            logger.info(f"🎛 Potenciómetro 1 (A0): {sensor_data['potenciometro_1']:.2f} V")
        else:
            logger.warning("⚠️ Potenciómetro 1: Error de lectura")
            
        if sensor_data['potenciometro_2'] is not None:
            logger.info(f"🎛 Potenciómetro 2 (A1): {sensor_data['potenciometro_2']:.2f} V")
        else:
            logger.warning("⚠️ Potenciómetro 2: Error de lectura")
            
        if sensor_data['ph'] is not None:
            logger.info(f"🧪 Sensor pH (A2): pH estimado {sensor_data['ph']:.2f}")
        else:
            logger.warning("⚠️ Sensor pH: Error de lectura")
            
        if sensor_data['oxigeno_disuelto'] is not None:
            logger.info(f"🌊 Oxígeno disuelto (A3): {sensor_data['oxigeno_disuelto']:.2f} mg/L")
        else:
            logger.warning("⚠️ Sensor de oxígeno disuelto: Error de lectura")
            
        if sensor_data['temperatura'] is not None:
            logger.info(f"🌡 Temperatura: {sensor_data['temperatura']} °C")
        else:
            logger.warning("⚠️ Sensor de temperatura: Error de lectura")
        
        logger.info("=" * 60)


def main(sample_interval: int = DEFAULT_SAMPLE_INTERVAL):
    """Función principal del sistema"""
    logger.info("🚀 Iniciando sistema de monitoreo IoT")
    logger.info(f"⏱ Intervalo de muestreo: {sample_interval} segundos")
    
    # Inicializar placa
    try:
        board = Board(1, 0x10)
    except Exception as e:
        logger.error(f"❌ Error al crear objeto Board: {e}")
        sys.exit(1)
    
    # Inicializar gestor de sensores
    sensor_manager = SensorManager(board)
    
    if not sensor_manager.initialize_board():
        logger.error("❌ No se pudo inicializar la placa. Terminando programa.")
        sys.exit(1)
    
    # Detectar sensor de temperatura
    sensor_manager.detect_ds18b20()
    
    # Inicializar cliente MQTT
    mqtt_client = MQTTPublisher()
    try:
        mqtt_client.connect()
        time.sleep(2)  # Esperar establecimiento de conexión
    except Exception as e:
        logger.error(f"❌ Error al conectar MQTT: {e}")
        logger.warning("⚠️ Continuando sin conexión MQTT...")
    
    # Bucle principal
    try:
        while True:
            start_time = time.time()
            
            # Leer todos los sensores de forma sincronizada
            sensor_data = sensor_manager.read_all_sensors()
            
            # Mostrar lecturas
            sensor_manager.print_sensor_readings(sensor_data)
            
            # Enviar datos por MQTT si hay al menos una lectura válida
            if any(v is not None for k, v in sensor_data.items() if k != 'sensor_status'):
                mqtt_message = mqtt_client.build_message(sensor_data)
                logger.info(f"📦 Enviando datos: {mqtt_message}")
                mqtt_client.publish(TOPIC_DATA, mqtt_message)
            else:
                logger.warning("⚠️ No hay datos válidos para enviar")
            
            # Calcular tiempo de espera para el próximo muestreo
            elapsed_time = time.time() - start_time
            sleep_time = max(0, sample_interval - elapsed_time)
            
            if sleep_time > 0:
                logger.info(f"😴 Esperando {sleep_time:.1f} segundos hasta el próximo muestreo...")
                time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        logger.info("🛑 Lectura finalizada por el usuario.")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
    finally:
        # Desconectar MQTT al finalizar
        mqtt_client.disconnect()
        logger.info("👋 Programa finalizado correctamente.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sistema de monitoreo IoT con sensores')
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=DEFAULT_SAMPLE_INTERVAL,
        help=f'Intervalo de muestreo en segundos (por defecto: {DEFAULT_SAMPLE_INTERVAL})'
    )
    
    args = parser.parse_args()
    
    # Validar intervalo
    if args.interval < 1:
        logger.error("❌ El intervalo debe ser mayor o igual a 1 segundo")
        sys.exit(1)
    
    main(sample_interval=args.interval)
