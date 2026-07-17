# IoTLisaProject

Sistema de monitoreo IoT para Raspberry Pi con lectura de sensores y envio de datos por MQTT hacia Node-RED.

## Sensores incluidos

- sensores analogicos ya existentes del proyecto
- `DS18B20`
- `SEN0707` por `RS485 Modbus RTU`
- `SEN0710` por `RS485 Modbus RTU`

## Documentacion principal

- `MANUAL_USUARIO.md`: instalacion, uso diario, MQTT, servicio y Node-RED
- `MANUAL_DESARROLLADOR.md`: arquitectura del proyecto y guia para mantener o extender el codigo
- `MANUAL_SENSORES_RS485.md`: uso, limpieza, cuidado y buenas practicas para `SEN0707` y `SEN0710`

## Archivos clave

- `iot_sensor_system.py`: sistema principal
- `diagnostic.py`: diagnostico general
- `iot_service_manager.sh`: instalacion y control del servicio
- `rs485_ec_sensor.py`: prueba directa del sensor `SEN0707`
- `rs485_turbidity_sensor.py`: prueba directa del sensor `SEN0710`
- `rs485_modbus_config.py`: lectura y cambio de direccion/baudrate Modbus

## Configuracion RS485 recomendada

- `SEN0707` -> `slave 1`
- `SEN0710` -> `slave 2`
- ambos a `4800 baud`

## Inicio rapido

### Diagnostico

```bash
python3 diagnostic.py
```

### Sistema principal

```bash
python3 iot_sensor_system.py --interval 60 --ec-port /dev/ttyUSB0 --turbidity-port /dev/ttyUSB0
```

### Servicio

```bash
sudo ./iot_service_manager.sh install
sudo ./iot_service_manager.sh start
```

## Node-RED

El sistema publica en el topic:

```text
iot_uleam/uleam
```

Para detalles de dashboard y configuracion MQTT, revisar `MANUAL_USUARIO.md`.
