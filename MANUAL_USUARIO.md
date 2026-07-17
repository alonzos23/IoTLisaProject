# Manual de Usuario

## Objetivo

Este sistema permite leer sensores conectados a una Raspberry Pi y enviar los datos por MQTT para visualizarlos en Node-RED.

Actualmente el sistema puede trabajar con:

- sensores analogicos ya existentes del proyecto
- sensor `DS18B20`
- sensor RS485 de conductividad `SEN0707`
- sensor RS485 de turbidez `SEN0710`

## Archivos importantes para el usuario

- `iot_sensor_system.py`: programa principal
- `diagnostic.py`: diagnostico rapido del sistema
- `iot_service_manager.sh`: instalar, iniciar, detener y revisar el servicio
- `rs485_ec_sensor.py`: prueba directa del sensor `SEN0707`
- `rs485_turbidity_sensor.py`: prueba directa del sensor `SEN0710`
- `rs485_modbus_config.py`: cambiar direccion o baudrate de sensores RS485

## Requisitos basicos

- Raspberry Pi encendida y configurada
- broker MQTT accesible
- Node-RED instalado si se quiere dashboard
- sensores bien alimentados y conectados

## Sensores RS485 nuevos

### Conductividad y salinidad

- modelo: `SEN0707`
- direccion recomendada: `1`
- baudrate recomendado: `4800`

### Turbidez

- modelo: `SEN0710`
- direccion recomendada: `2`
- baudrate recomendado: `4800`

## Conexion RS485 recomendada

Si ambos sensores RS485 van al mismo adaptador `USB-RS485`:

- `A` del sensor EC con `A` del sensor de turbidez y al `A` del adaptador
- `B` del sensor EC con `B` del sensor de turbidez y al `B` del adaptador
- `GND` comun
- cada sensor con su alimentacion correcta

Importante:

- no dejar ambos sensores con la misma direccion Modbus
- configuracion recomendada:
  - `SEN0707 = slave 1`
  - `SEN0710 = slave 2`

## Comandos utiles

### Probar el sensor EC

```bash
python3 rs485_ec_sensor.py --port /dev/ttyUSB0 --address 1 --json --count 5 --interval 2
```

### Probar el sensor de turbidez

```bash
python3 rs485_turbidity_sensor.py --port /dev/ttyUSB0 --address 2 --json --count 5 --interval 2
```

### Cambiar direccion Modbus

Ejemplo: cambiar el sensor de turbidez de `1` a `2`

```bash
python3 rs485_modbus_config.py --port /dev/ttyUSB0 --current-address 1 --new-address 2
```

### Ejecutar diagnostico general

```bash
python3 diagnostic.py
```

### Ejecutar el sistema principal manualmente

```bash
python3 iot_sensor_system.py --interval 60 --ec-port /dev/ttyUSB0 --turbidity-port /dev/ttyUSB0
```

## Instalar como servicio

```bash
chmod +x iot_service_manager.sh iot_sensor_system.py diagnostic.py rs485_ec_sensor.py rs485_turbidity_sensor.py rs485_modbus_config.py
sudo ./iot_service_manager.sh install
sudo ./iot_service_manager.sh start
```

## Revisar estado del servicio

```bash
sudo ./iot_service_manager.sh status
sudo ./iot_service_manager.sh logs
```

## Datos enviados por MQTT

El sistema publica en el topic:

```text
iot_uleam/uleam
```

Ejemplo de payload:

```json
{
  "Sensor": "ULEAMCENTRAL02",
  "temperatura": null,
  "ph": 12.89,
  "oxigeno_disuelto": 0.0,
  "potenciometro_1": 1.07,
  "potenciometro_2": 1.53,
  "ec_us_cm": null,
  "ec_temperature_c": null,
  "salinity_ppm": null,
  "tds_ppm": null,
  "turbidity_ntu": 35.4,
  "turbidity_temperature_c": 26.4,
  "timestamp": 1784311196,
  "dateTime": "17/07/2026 12:59:56",
  "sensor_status": {
    "board": true,
    "temperature": false,
    "ph": true,
    "dissolved_oxygen": true,
    "potentiometer_1": true,
    "potentiometer_2": true,
    "ec_sensor": false,
    "turbidity_sensor": true
  }
}
```

## Uso con Node-RED

En Node-RED se debe usar:

- broker MQTT correcto
- topic `iot_uleam/uleam`
- un nodo `json` o salida parseada

Si el dashboard no muestra un sensor nuevo:

1. revisar el payload en el nodo `debug`
2. revisar que el nodo `function` tenga suficientes salidas
3. revisar que el dashboard tenga los gauges conectados

## Problemas comunes

### El sensor equivocado aparece en el diagnostico

Ocurre cuando ambos sensores RS485 siguen en la misma direccion. Se debe corregir la direccion Modbus.

### El sensor RS485 no responde

Revisar:

- puerto correcto
- direccion correcta
- baudrate correcto
- cableado `A/B`
- alimentacion externa

### El dashboard no muestra turbidez

Revisar que el payload MQTT tenga:

- `turbidity_ntu`
- `turbidity_temperature_c`
- `sensor_status.turbidity_sensor`

## Recomendacion de uso diario

1. verificar conexiones
2. ejecutar una prueba corta del sensor a usar
3. ejecutar `diagnostic.py` si hay dudas
4. iniciar el sistema principal
5. revisar datos en Node-RED
