# Sistema de Monitoreo IoT con Sensores - Raspberry Pi

Sistema mejorado para monitoreo de sensores ambientales con envío de datos via MQTT.

## 🚀 Características Principales

- ✅ **Manejo robusto de errores** para cada sensor
- ✅ **Frecuencia de muestreo configurable** (por defecto 3600 segundos / 1 hora)
- ✅ **Lecturas sincronizadas** de todos los sensores
- ✅ **Sistema de logging completo** con archivo de log y salida por consola
- ✅ **Reconexión automática** MQTT
- ✅ **Gestión como servicio systemd** con scripts de control
- ✅ **Estado de salud de sensores** incluido en cada mensaje
- ✅ **No se cuelga** si un sensor falla

## 📋 Sensores Soportados

| Sensor | Canal | Medición |
|--------|-------|----------|
| Sensor pH | A2 | pH (0-14) |
| Oxígeno Disuelto | A3 | mg/L |
| DS18B20 | 1-Wire | Temperatura (°C) |

## 🔧 Requisitos Previos

### Hardware
- Raspberry Pi (3/4/5)
- DFRobot Expansion Board (dirección I2C: 0x10)
- Sensores conectados según la tabla anterior

### Software
```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y python3 python3-pip

# Instalar librerías Python
pip3 install paho-mqtt
pip3 install DFRobot-RaspberryPi-Expansion-Board

# Habilitar I2C
sudo raspi-config
# Navegar a: Interface Options > I2C > Enable

# Habilitar 1-Wire para DS18B20
sudo raspi-config
# Navegar a: Interface Options > 1-Wire > Enable

# Reiniciar
sudo reboot
```

## 📦 Instalación del Sistema

### 1. Descargar los archivos

Coloca los siguientes archivos en el mismo directorio:
- `iot_sensor_system.py` - Script principal
- `iot-sensor-system.service` - Archivo de servicio systemd
- `iot_service_manager.sh` - Script de gestión

### 2. Dar permisos de ejecución

```bash
chmod +x iot_service_manager.sh
chmod +x iot_sensor_system.py
```

### 3. Instalar el servicio

```bash
sudo ./iot_service_manager.sh install
```

Esto hará:
- Crear el directorio `/home/pi/iot_sensors`
- Copiar el script Python al directorio
- Instalar el servicio systemd
- Crear el archivo de log

## 🎮 Uso del Sistema

### Comandos Básicos

```bash
# Ver ayuda
./iot_service_manager.sh help

# Iniciar el servicio
sudo ./iot_service_manager.sh start

# Detener el servicio
sudo ./iot_service_manager.sh stop

# Reiniciar el servicio
sudo ./iot_service_manager.sh restart

# Ver estado del servicio
sudo ./iot_service_manager.sh status

# Ver logs
sudo ./iot_service_manager.sh logs
```

### Habilitar Inicio Automático

```bash
# Habilitar para que inicie al arrancar
sudo ./iot_service_manager.sh enable

# Deshabilitar inicio automático
sudo ./iot_service_manager.sh disable
```

### Ver Logs en Tiempo Real

```bash
# Opción 1: Logs del sistema (systemd)
sudo journalctl -u iot-sensor-system -f

# Opción 2: Archivo de log
tail -f /var/log/iot_sensor_system.log
```

## ⚙️ Configuración

### Cambiar la Frecuencia de Muestreo

Edita el archivo de servicio:
```bash
sudo nano /etc/systemd/system/iot-sensor-system.service
```

Modifica la línea `ExecStart`:
```ini
# Ejemplo: muestrear cada 10 minutos (600 segundos)
ExecStart=/usr/bin/python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 600

# Ejemplo: muestrear cada 5 minutos (300 segundos)
ExecStart=/usr/bin/python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 300

# Ejemplo: muestrear cada hora (3600 segundos) - VALOR POR DEFECTO
ExecStart=/usr/bin/python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 3600
```

Después de modificar:
```bash
sudo systemctl daemon-reload
sudo ./iot_service_manager.sh restart
```

### Ejecutar Manualmente (sin servicio)

```bash
# Con intervalo por defecto (3600 segundos)
python3 iot_sensor_system.py

# Con intervalo personalizado (ejemplo: 60 segundos)
python3 iot_sensor_system.py --interval 60
```

### Modificar Configuración MQTT

Edita el archivo `iot_sensor_system.py`:
```python
# === Configuración MQTT ===
BROKER = '10.150.253.2'        # IP del broker
PORT = 1883                     # Puerto MQTT
USERNAME = 'mqtt-uleam'         # Usuario
PASSWORD = 'Mqtt-Uleam2025$'    # Contraseña
```

## 📊 Formato de Datos

### Mensaje JSON Enviado

```json
{
  "Sensor": "ULEAMCENTRAL02",
  "temperatura": 25.5,
  "ph": 7.2,
  "oxigeno_disuelto": 8.5,
  "timestamp": 1735603200,
  "dateTime": "30/10/2025 14:30:00",
  "sensor_status": {
    "board": true,
    "temperature": true,
    "ph": true,
    "dissolved_oxygen": true,
    "potentiometer_1": true,
    "potentiometer_2": true
  }
}
```

### Valores `null` en Caso de Error

Si un sensor falla, su valor será `null` y su estado será `false`:
```json
{
  "temperatura": null,
  "sensor_status": {
    "temperature": false
  }
}
```

## 🔍 Diagnóstico y Solución de Problemas

### El servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u iot-sensor-system -n 100

# Verificar el estado
sudo systemctl status iot-sensor-system

# Probar ejecución manual
python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 10
```

### Sensor no detectado

```bash
# Verificar I2C
sudo i2cdetect -y 1

# Verificar 1-Wire (DS18B20)
ls /sys/bus/w1/devices/

# Ver logs del sistema
sudo ./iot_service_manager.sh logs
```

### Error de permisos

```bash
# Asegurarse de que el usuario 'pi' tenga permisos
sudo chown -R pi:pi /home/pi/iot_sensors
sudo chmod +x /home/pi/iot_sensors/iot_sensor_system.py
```

### Problemas con MQTT

```bash
# Probar conexión al broker
ping 10.150.253.2

# Ver logs específicos de MQTT
sudo journalctl -u iot-sensor-system | grep MQTT
```

## 🛡️ Manejo de Errores

El sistema incluye:

1. **Reintentos automáticos** (hasta 3 intentos) para lecturas fallidas
2. **Timeout de 5 segundos** para operaciones de sensores
3. **Reconexión automática** MQTT si se pierde la conexión
4. **Continúa operando** aunque algunos sensores fallen
5. **Logs detallados** de todos los errores
6. **Estado de salud** reportado en cada mensaje

## 📁 Estructura de Archivos

```
/home/pi/iot_sensors/
├── iot_sensor_system.py          # Script principal
└── [otros archivos de configuración]

/etc/systemd/system/
└── iot-sensor-system.service     # Definición del servicio

/var/log/
└── iot_sensor_system.log         # Archivo de log
```

## 🔄 Actualizar el Sistema

```bash
# 1. Detener el servicio
sudo ./iot_service_manager.sh stop

# 2. Reemplazar el archivo Python
sudo cp iot_sensor_system.py /home/pi/iot_sensors/

# 3. Recargar y reiniciar
sudo systemctl daemon-reload
sudo ./iot_service_manager.sh start
```

## 📝 Notas Importantes

- El intervalo mínimo de muestreo es **1 segundo**
- El intervalo por defecto es **3600 segundos (1 hora)**
- Los logs se guardan en `/var/log/iot_sensor_system.log`
- El servicio se ejecuta con el usuario `pi`
- Los datos se envían aunque algunos sensores fallen (los que funcionen)

## 🆘 Soporte

Para más información sobre los logs:
```bash
# Último arranque del sistema
sudo journalctl -b -u iot-sensor-system

# Últimas 24 horas
sudo journalctl --since "24 hours ago" -u iot-sensor-system

# Errores únicamente
sudo journalctl -u iot-sensor-system -p err
```

---

**Versión:** 1.0  
**Fecha:** Enero 2026
**Autoras:** Alonzo Merizaldes Stefany Michelle - Cedeño Rivera Joseline Malena
**Tutor:** Ing. Willian Zamora, PhD.
**Guia Tutor:** Ing. Mike Machuca Avalos, Mg.


**Versión:** 2.0 
**Fecha:** Por definir 
**Autor/Colaborador:** Victor Delgado
**Tutor:** Ing. Mike Machica Avalos, Mg**
**Guia tutor:** Ing. Willian Zamora, PhD**
**Mejoras Implementadas:** Sensores de Salinidad y Turbidez 
