# 💡 EJEMPLOS PRÁCTICOS DE USO

## 📝 ESCENARIOS COMUNES

### Escenario 1: Primera Instalación

```bash
# 1. Conectarse al Raspberry Pi
ssh pi@192.168.1.100

# 2. Crear directorio de trabajo
mkdir -p ~/iot_project
cd ~/iot_project

# 3. Copiar los archivos al Raspberry Pi
# (desde tu computadora)
scp iot_sensor_system.py pi@192.168.1.100:~/iot_project/
scp iot-sensor-system.service pi@192.168.1.100:~/iot_project/
scp iot_service_manager.sh pi@192.168.1.100:~/iot_project/
scp diagnostic.py pi@192.168.1.100:~/iot_project/

# 4. Volver al SSH del Raspberry Pi
cd ~/iot_project

# 5. Dar permisos
chmod +x iot_service_manager.sh
chmod +x iot_sensor_system.py
chmod +x diagnostic.py

# 6. Ejecutar diagnóstico
python3 diagnostic.py

# 7. Si todo está OK, instalar servicio
sudo ./iot_service_manager.sh install

# 8. Iniciar servicio
sudo ./iot_service_manager.sh start

# 9. Verificar que funciona
sudo ./iot_service_manager.sh status

# 10. Habilitar inicio automático
sudo ./iot_service_manager.sh enable
```

---

### Escenario 2: Prueba con Muestreo Rápido

**Caso:** Quieres probar que todo funciona sin esperar 1 hora

```bash
# Ejecutar manualmente con muestreo cada 10 segundos
python3 iot_sensor_system.py --interval 10

# Ver las lecturas en tiempo real
# Presiona Ctrl+C para detener
```

**Salida esperada:**
```
🚀 Iniciando sistema de monitoreo IoT
⏱ Intervalo de muestreo: 10 segundos
✅ Placa iniciada correctamente
🔍 Buscando sensor DS18B20...
✅ Sensor detectado: /sys/bus/w1/devices/28-xxxxxxxxxxxx
🔌 Conectando a broker MQTT 10.150.253.2:1883...
✅ Conectado exitosamente al broker MQTT

============================================================
📊 LECTURAS DE SENSORES
============================================================
🎛 Potenciómetro 1 (A0): 1.65 V
🎛 Potenciómetro 2 (A1): 2.10 V
🧪 Sensor pH (A2): pH estimado 7.20
🌊 Oxígeno disuelto (A3): 8.50 mg/L
🌡 Temperatura: 25.5 °C
============================================================

📦 Enviando datos: {"Sensor": "ULEAMCENTRAL02", ...}
📤 Datos enviados al servidor MQTT (ID: 1)
😴 Esperando 9.8 segundos hasta el próximo muestreo...
```

---

### Escenario 3: Cambiar Frecuencia del Servicio

**Caso:** Quieres que el servicio muestree cada 5 minutos (300 segundos)

```bash
# 1. Detener el servicio
sudo ./iot_service_manager.sh stop

# 2. Editar el archivo de servicio
sudo nano /etc/systemd/system/iot-sensor-system.service

# 3. Modificar la línea ExecStart:
# De:
ExecStart=/usr/bin/python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 3600

# A:
ExecStart=/usr/bin/python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 300

# 4. Guardar (Ctrl+O, Enter, Ctrl+X)

# 5. Recargar configuración
sudo systemctl daemon-reload

# 6. Iniciar servicio
sudo ./iot_service_manager.sh start

# 7. Verificar
sudo ./iot_service_manager.sh status
```

---

### Escenario 4: Ver Logs en Tiempo Real

**Caso:** Quieres ver qué está haciendo el sistema ahora mismo

```bash
# Opción 1: Logs del sistema (recomendado)
sudo journalctl -u iot-sensor-system -f

# Opción 2: Archivo de log
tail -f /var/log/iot_sensor_system.log

# Opción 3: Últimas 100 líneas
sudo journalctl -u iot-sensor-system -n 100

# Opción 4: Solo errores
sudo journalctl -u iot-sensor-system -p err
```

---

### Escenario 5: Un Sensor Dejó de Funcionar

**Caso:** El sensor de temperatura no está reportando datos

```bash
# 1. Ver los logs para identificar el problema
sudo ./iot_service_manager.sh logs

# Buscar líneas como:
# ⚠️ Sensor de temperatura: Error de lectura
# ❌ Error al leer temperatura: [Errno 2] No such file or directory

# 2. Ejecutar diagnóstico
python3 diagnostic.py

# 3. Verificar específicamente el DS18B20
ls /sys/bus/w1/devices/

# Si no aparece:
# - Verificar conexión física
# - Verificar resistencia pull-up (4.7kΩ)
# - Verificar que 1-Wire está habilitado:
sudo raspi-config
# Interface Options > 1-Wire > Enable

# 4. Reiniciar
sudo reboot

# 5. Después del reinicio, verificar de nuevo
python3 diagnostic.py
```

**Importante:** El sistema **seguirá funcionando** con los otros sensores aunque uno falle.

---

### Escenario 6: Verificar Datos en el Broker MQTT

**Caso:** Quieres confirmar que los datos están llegando al servidor

```bash
# Instalar mosquitto clients (si no está instalado)
sudo apt-get install mosquitto-clients

# Suscribirse al topic y ver mensajes en tiempo real
mosquitto_sub -h 10.150.253.2 -p 1883 \
  -u mqtt-uleam -P 'Mqtt-Uleam2025$' \
  -t 'iot_uleam/uleam' -v

# Salida esperada:
# iot_uleam/uleam {"Sensor":"ULEAMCENTRAL02","temperatura":25.5,...}
```

---

### Escenario 7: Actualizar el Código

**Caso:** Has hecho cambios en `iot_sensor_system.py`

```bash
# 1. Detener el servicio
sudo ./iot_service_manager.sh stop

# 2. Hacer backup del código actual
cp /home/pi/iot_sensors/iot_sensor_system.py \
   /home/pi/iot_sensors/iot_sensor_system.py.backup

# 3. Copiar la nueva versión
sudo cp iot_sensor_system.py /home/pi/iot_sensors/

# 4. Dar permisos
sudo chmod +x /home/pi/iot_sensors/iot_sensor_system.py
sudo chown pi:pi /home/pi/iot_sensors/iot_sensor_system.py

# 5. Probar manualmente primero
python3 /home/pi/iot_sensors/iot_sensor_system.py --interval 10

# 6. Si funciona, iniciar el servicio
sudo ./iot_service_manager.sh start

# 7. Verificar logs
sudo ./iot_service_manager.sh logs
```

---

### Escenario 8: Depuración de Problemas de Red

**Caso:** El sistema no puede conectarse al broker MQTT

```bash
# 1. Verificar conectividad básica
ping 10.150.253.2

# 2. Verificar que el puerto está abierto
nc -zv 10.150.253.2 1883

# Si falla:
# telnet 10.150.253.2 1883

# 3. Probar con mosquitto
mosquitto_pub -h 10.150.253.2 -p 1883 \
  -u mqtt-uleam -P 'Mqtt-Uleam2025$' \
  -t 'test' -m 'hello'

# 4. Ver logs del servicio para más detalles
sudo journalctl -u iot-sensor-system | grep MQTT

# 5. Verificar firewall
sudo iptables -L -n | grep 1883
```

---

### Escenario 9: Monitoreo del Sistema

**Caso:** Quieres crear un dashboard de monitoreo simple

```bash
# Crear script de monitoreo
nano monitor.sh
```

Contenido de `monitor.sh`:
```bash
#!/bin/bash

while true; do
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "  MONITOR DEL SISTEMA IoT - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Estado del servicio
    echo "📊 ESTADO DEL SERVICIO:"
    systemctl is-active --quiet iot-sensor-system && \
        echo "   ✅ Activo" || echo "   ❌ Inactivo"
    echo ""
    
    # Última lectura
    echo "📈 ÚLTIMA LECTURA:"
    tail -n 20 /var/log/iot_sensor_system.log | grep "Temperatura\|pH\|Oxígeno"
    echo ""
    
    # Uso de CPU y memoria
    echo "💻 RECURSOS:"
    ps aux | grep iot_sensor_system.py | grep -v grep | \
        awk '{printf "   CPU: %s%%  MEM: %s%%\n", $3, $4}'
    echo ""
    
    echo "Actualizando en 10 segundos... (Ctrl+C para salir)"
    sleep 10
done
```

```bash
# Dar permisos y ejecutar
chmod +x monitor.sh
./monitor.sh
```

---

### Escenario 10: Backup Automático de Datos

**Caso:** Quieres guardar un respaldo de los logs periódicamente

```bash
# Crear script de backup
sudo nano /usr/local/bin/backup_iot_logs.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="/home/pi/backups/iot_logs"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup del log
cp /var/log/iot_sensor_system.log "$BACKUP_DIR/log_$DATE.log"

# Comprimir logs antiguos (más de 7 días)
find $BACKUP_DIR -name "log_*.log" -mtime +7 -exec gzip {} \;

# Eliminar backups muy antiguos (más de 30 días)
find $BACKUP_DIR -name "log_*.log.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

```bash
# Dar permisos
sudo chmod +x /usr/local/bin/backup_iot_logs.sh

# Agregar a crontab (diario a las 23:00)
sudo crontab -e

# Agregar esta línea:
0 23 * * * /usr/local/bin/backup_iot_logs.sh >> /var/log/backup_iot.log 2>&1
```

---

## 🔧 COMANDOS ÚTILES PARA EL DÍA A DÍA

```bash
# Ver estado rápido
sudo systemctl status iot-sensor-system

# Reiniciar servicio
sudo systemctl restart iot-sensor-system

# Ver últimas 50 líneas de log
sudo journalctl -u iot-sensor-system -n 50

# Buscar errores en logs
sudo journalctl -u iot-sensor-system | grep -i error

# Ver logs de hoy
sudo journalctl -u iot-sensor-system --since today

# Ver logs entre fechas
sudo journalctl -u iot-sensor-system \
  --since "2025-10-28" --until "2025-10-30"

# Limpiar logs antiguos
sudo journalctl --vacuum-time=30d
```

---

## 📱 CREAR ALIAS PARA FACILIDAD DE USO

```bash
# Editar .bashrc
nano ~/.bashrc

# Agregar al final:
alias iot-start='sudo systemctl start iot-sensor-system'
alias iot-stop='sudo systemctl stop iot-sensor-system'
alias iot-restart='sudo systemctl restart iot-sensor-system'
alias iot-status='sudo systemctl status iot-sensor-system'
alias iot-logs='sudo journalctl -u iot-sensor-system -f'
alias iot-diag='python3 ~/iot_project/diagnostic.py'

# Recargar
source ~/.bashrc

# Ahora puedes usar:
iot-start
iot-status
iot-logs
```

---

## 🎯 TIPS Y MEJORES PRÁCTICAS

### 1. **Monitoreo Proactivo**
```bash
# Configurar alerta si el servicio se detiene
# Crear script de monitoreo
sudo nano /usr/local/bin/check_iot_service.sh
```

```bash
#!/bin/bash
if ! systemctl is-active --quiet iot-sensor-system; then
    echo "⚠️ Servicio IoT caído - $(date)" >> /var/log/iot_alerts.log
    sudo systemctl start iot-sensor-system
    echo "🔄 Servicio reiniciado" >> /var/log/iot_alerts.log
fi
```

```bash
# Agregar a crontab (cada 5 minutos)
*/5 * * * * /usr/local/bin/check_iot_service.sh
```

### 2. **Rotación de Logs**
```bash
# Crear configuración de logrotate
sudo nano /etc/logrotate.d/iot-sensor
```

```
/var/log/iot_sensor_system.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 pi pi
}
```

### 3. **Notificaciones por Email** (opcional)
```bash
# Instalar mailutils
sudo apt-get install mailutils

# Crear script de notificación
sudo nano /usr/local/bin/iot_notify.sh
```

```bash
#!/bin/bash
ERRORS=$(sudo journalctl -u iot-sensor-system --since "1 hour ago" | grep -i error | wc -l)

if [ $ERRORS -gt 5 ]; then
    echo "Se detectaron $ERRORS errores en la última hora" | \
    mail -s "⚠️ Alerta Sistema IoT" tu@email.com
fi
```

---

## 📊 INTERPRETACIÓN DE DATOS

### Valores Normales Esperados:

| Sensor | Rango Normal | Unidad |
|--------|-------------|--------|
| Temperatura | 15-35 | °C |
| pH | 6.5-8.5 | pH |
| Oxígeno Disuelto | 5-15 | mg/L |
| Potenciómetros | 0-3.3 | V |

### Señales de Alerta:

⚠️ **Temperatura:**
- < 10°C o > 40°C → Verificar sensor
- Variaciones > 5°C en 1 hora → Posible fallo

⚠️ **pH:**
- < 4 o > 10 → Verificar calibración
- Valor constante 7.0 → Posible sensor desconectado

⚠️ **Oxígeno Disuelto:**
- 0 mg/L → Sensor desconectado o mal calibrado
- > 20 mg/L → Posible error de sensor

---

¡Con esta guía tienes todo lo necesario para operar el sistema efectivamente! 🎉
