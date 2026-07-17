# Manual para Desarrolladores

## Objetivo

Este documento describe la organizacion del proyecto y las reglas practicas para mantenerlo sin romper el soporte actual de sensores.

## Resumen de arquitectura

El proyecto esta centrado en `iot_sensor_system.py`, que:

- lee sensores analogicos y `DS18B20`
- lee sensores RS485 usando `minimalmodbus`
- construye un JSON unificado
- publica los datos por MQTT

## Archivos principales

- `iot_sensor_system.py`: bucle principal y payload MQTT
- `diagnostic.py`: pruebas individuales de hardware y conectividad
- `rs485_ec_sensor.py`: lector del `SEN0707`
- `rs485_turbidity_sensor.py`: lector del `SEN0710`
- `rs485_modbus_config.py`: herramienta para direccion y baudrate Modbus
- `iot_service_manager.sh`: instalacion y control del servicio
- `iot-sensor-system.service`: definicion de systemd

## Sensores soportados

### Ya existentes en el proyecto

- `A0`: `potenciometro_1`
- `A1`: `potenciometro_2`
- `A2`: `ph`
- `A3`: `oxigeno_disuelto`
- `DS18B20`: `temperatura`

### Agregados en esta etapa

- `SEN0707`
  - `ec_us_cm`
  - `ec_temperature_c`
  - `salinity_ppm`
  - `tds_ppm`
  - `sensor_status.ec_sensor`

- `SEN0710`
  - `turbidity_ntu`
  - `turbidity_temperature_c`
  - `sensor_status.turbidity_sensor`

## Convencion RS485 adoptada

Para compartir el mismo bus RS485:

- `SEN0707` usa `slave 1`
- `SEN0710` usa `slave 2`
- ambos usan `4800`, `8N1`

No cambiar estos defaults sin actualizar tambien:

- `iot_sensor_system.py`
- `diagnostic.py`
- `MANUAL_USUARIO.md`
- cualquier flujo de `Node-RED` que dependa del payload

## Flujo de datos

1. `SensorManager` inicializa placa, `DS18B20` y sensores RS485
2. `read_all_sensors()` junta todos los datos
3. `MQTTPublisher.build_message()` arma el payload
4. `publish()` envia al topic `iot_uleam/uleam`

## Reglas para modificar el sistema

### 1. No romper el payload existente

Si agregas sensores nuevos:

- conserva los campos actuales
- agrega los nuevos campos con nombres claros
- actualiza `sensor_status`

### 2. Mantener pruebas separadas por sensor RS485

Cada sensor RS485 debe tener:

- su lector dedicado
- su metodo de lectura propio
- su bloque de diagnostico propio

Esto evita interpretar mal registros de un sensor como si fueran de otro.

### 3. No asumir autodeteccion de modelo RS485

Los sensores pueden compartir:

- mismo puerto
- mismo baudrate
- mismo protocolo

Por eso la diferenciacion real se hace por direccion Modbus, no por deteccion automatica del modelo.

## Estructura interna relevante

### `iot_sensor_system.py`

- `MQTTPublisher`: conexion y publicacion MQTT
- `SensorManager.initialize_ec_sensor()`
- `SensorManager.initialize_turbidity_sensor()`
- `SensorManager.read_ec_sensor()`
- `SensorManager.read_turbidity_sensor()`
- `SensorManager.read_all_sensors()`

### `diagnostic.py`

Debe seguir reflejando la configuracion real del sistema. Si cambian direcciones o baudrate, actualizarlo.

## Comandos de desarrollo utiles

### Validar sintaxis

```bash
python -m py_compile iot_sensor_system.py diagnostic.py rs485_ec_sensor.py rs485_turbidity_sensor.py rs485_modbus_config.py
```

### Probar solo EC

```bash
python3 rs485_ec_sensor.py --port /dev/ttyUSB0 --address 1 --json --count 3
```

### Probar solo turbidez

```bash
python3 rs485_turbidity_sensor.py --port /dev/ttyUSB0 --address 2 --json --count 3
```

### Leer o cambiar configuracion Modbus

```bash
python3 rs485_modbus_config.py --port /dev/ttyUSB0 --current-address 1
python3 rs485_modbus_config.py --port /dev/ttyUSB0 --current-address 1 --new-address 2
```

### Ejecutar sistema completo

```bash
python3 iot_sensor_system.py --interval 60 --ec-port /dev/ttyUSB0 --turbidity-port /dev/ttyUSB0
```

## Cuidados al tocar Node-RED

Si se agregan nuevas claves al payload MQTT, revisar:

- nodo `function` de normalizacion
- cantidad de salidas del nodo `function`
- gauges, textos y charts conectados

Error comun:

- el codigo del `function` se actualiza, pero el numero de `outputs` no

## Procedimiento recomendado al agregar un nuevo sensor

1. confirmar protocolo y registros del fabricante
2. crear un script de prueba dedicado
3. validar lecturas reales en Raspberry Pi
4. integrar en `iot_sensor_system.py`
5. agregar estado en `sensor_status`
6. actualizar `diagnostic.py`
7. actualizar documentacion
8. actualizar `Node-RED` si el payload cambia

## Riesgos conocidos

- dos sensores RS485 con misma direccion en el mismo bus producen conflictos
- diagnosticos de un sensor pueden interpretar basura valida de otro si comparten direccion y protocolo
- si el servicio systemd no se reinstala o reinicia, Node-RED puede seguir recibiendo el payload viejo

## Recomendacion general

Mantener cada cambio pequeño y verificable. Primero prueba con script individual, luego integra al sistema principal, luego valida MQTT y finalmente dashboard.
