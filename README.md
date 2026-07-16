# Sistema de Monitoreo IoT con Sensores - Raspberry Pi

Sistema de monitoreo para Raspberry Pi con envio de datos por MQTT.

## Sensores integrados

| Sensor | Interfaz | Medicion |
|--------|----------|----------|
| Potenciometro 1 | A0 | Voltaje |
| Potenciometro 2 | A1 | Voltaje |
| Sensor pH | A2 | pH |
| Oxigeno disuelto | A3 | mg/L |
| DS18B20 | 1-Wire | Temperatura |
| DFRobot SEN0707 | RS485 Modbus RTU | EC, salinidad, TDS, temperatura |

## Archivos principales

- `iot_sensor_system.py`: proceso principal y publicacion MQTT
- `rs485_ec_sensor.py`: lector y prueba del sensor `SEN0707`
- `diagnostic.py`: diagnostico de I2C, 1-Wire, RS485 y MQTT
- `iot_service_manager.sh`: instalacion y control del servicio
- `iot-sensor-system.service`: unidad `systemd`

## Requisitos

### Hardware

- Raspberry Pi
- DFRobot Expansion Board `0x10`
- Sensor `DS18B20`
- Sensor de pH en `A2`
- Sensor de oxigeno disuelto en `A3`
- Sensor `SEN0707` con alimentacion `10-30V`
- Adaptador `USB-RS485`

### Software

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
pip3 install paho-mqtt minimalmodbus pyserial DFRobot-RaspberryPi-Expansion-Board
```

Habilitar en la Raspberry Pi:

- `I2C`
- `1-Wire`

## Uso del sensor EC RS485

El `SEN0707` usa estos parametros por defecto:

- protocolo: `Modbus RTU`
- direccion: `1`
- baudrate: `4800`
- formato serie: `8N1`

Cableado del sensor:

- `Brown`: `VCC 10-30V`
- `Black`: `GND`
- `Yellow`: `485-A`
- `Blue`: `485-B`

Prueba directa del sensor:

```bash
python3 rs485_ec_sensor.py --port /dev/ttyUSB0 --device-info --count 1
python3 rs485_ec_sensor.py --port /dev/ttyUSB0 --json --count 5 --interval 2
```

## Ejecutar manualmente el sistema completo

```bash
python3 iot_sensor_system.py --interval 60 --ec-port /dev/ttyUSB0
```

Si no pasas `--ec-port`, el sistema intenta detectar automaticamente un puerto `USB` o `ACM`.

## Instalar como servicio

```bash
chmod +x iot_service_manager.sh iot_sensor_system.py rs485_ec_sensor.py diagnostic.py
sudo ./iot_service_manager.sh install
sudo ./iot_service_manager.sh start
sudo ./iot_service_manager.sh status
```

## Mensaje MQTT

Ejemplo de payload:

```json
{
  "Sensor": "ULEAMCENTRAL02",
  "temperatura": 25.4,
  "ph": 7.12,
  "oxigeno_disuelto": 8.3,
  "potenciometro_1": 1.23,
  "potenciometro_2": 2.34,
  "ec_us_cm": 1216,
  "ec_temperature_c": 25.2,
  "salinity_ppm": 608,
  "tds_ppm": 668,
  "timestamp": 1735603200,
  "dateTime": "30/10/2025 14:30:00",
  "sensor_status": {
    "board": true,
    "temperature": true,
    "ph": true,
    "dissolved_oxygen": true,
    "potentiometer_1": true,
    "potentiometer_2": true,
    "ec_sensor": true
  }
}
```

## Diagnostico

```bash
python3 diagnostic.py
```

El diagnostico prueba:

- bus `I2C`
- placa `DFRobot`
- entradas `A0-A3`
- `pH`
- oxigeno disuelto
- `DS18B20`
- sensor `SEN0707`
- conectividad `MQTT`

## Problemas comunes

### El sensor EC responde pero marca `0`

- prueba con el sensor realmente sumergido
- elimina burbujas en la punta
- usa una muestra conductiva, no solo humedad en la tapa
- confirma que `A` y `B` no esten invertidos

### No hay comunicacion RS485

- revisa `/dev/ttyUSB0` o `/dev/ttyACM0`
- confirma `slave=1`
- confirma `baudrate=4800`
- verifica alimentacion estable de `12V`

### El servicio no inicia

```bash
sudo journalctl -u iot-sensor-system -n 100
sudo systemctl status iot-sensor-system
```
