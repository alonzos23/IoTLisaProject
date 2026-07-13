# ✅ GUÍA DE VERIFICACIÓN - DESPUÉS DE LA CORRECCIÓN

## 🎯 Objetivo
Verificar que el sistema funciona correctamente después de corregir el error de permisos.

---

## 📝 CHECKLIST DE VERIFICACIÓN

### ✅ Paso 1: Verificar Archivos Descargados

```bash
# Listar archivos en el directorio actual
ls -lh

# Deberías ver:
# - iot_sensor_system.py
# - diagnostic.py
# - test_quick.py (nuevo)
# - iot_service_manager.sh
# - iot-sensor-system.service
# - Documentación (.md)
```

**Estado:** ⬜ Completado

---

### ✅ Paso 2: Dar Permisos de Ejecución

```bash
chmod +x iot_sensor_system.py
chmod +x diagnostic.py
chmod +x test_quick.py
chmod +x iot_service_manager.sh
```

**Estado:** ⬜ Completado

---

### ✅ Paso 3: Ejecutar Diagnóstico Básico

```bash
python3 diagnostic.py
```

**Qué verificar:**
- ✅ Placa DFRobot detectada
- ✅ Dispositivos I2C visibles
- ✅ Sensores respondiendo
- ✅ Conectividad MQTT

**Resultado esperado:**
```
✅ Placa DFRobot: OK
✅ Sensor DS18B20: OK  
✅ Potenciómetro A0: OK
✅ Potenciómetro A1: OK
✅ Sensor pH A2: OK
✅ Sensor O2 A3: OK
✅ Conectividad a 10.150.253.2:1883: OK
```

**Estado:** ⬜ Completado

---

### ✅ Paso 4: Prueba Rápida (5 segundos)

```bash
python3 test_quick.py
```

**Qué verificar:**
1. El programa inicia sin errores
2. Aparece el mensaje: "📝 Archivo de log: ..."
3. Se muestran las lecturas de sensores
4. Los datos se envían por MQTT
5. Espera 5 segundos entre lecturas

**Ejemplo de salida correcta:**
```
╔══════════════════════════════════════════════════════════════╗
║         PRUEBA RÁPIDA - SISTEMA IOT ULEAM                    ║
║         Intervalo: 5 segundos (solo para pruebas)            ║
╚══════════════════════════════════════════════════════════════╝

🔍 Iniciando en modo de prueba...
⏱️  El sistema tomará muestras cada 5 segundos
🛑 Presiona Ctrl+C para detener

2025-10-30 15:30:00 - INFO - 📝 Archivo de log: /home/usuario/iot_logs/iot_sensor_system.log
2025-10-30 15:30:00 - INFO - 🚀 Iniciando sistema de monitoreo IoT
2025-10-30 15:30:00 - INFO - ⏱ Intervalo de muestreo: 5 segundos
2025-10-30 15:30:01 - INFO - ✅ Placa iniciada correctamente
2025-10-30 15:30:01 - INFO - 🔍 Buscando sensor DS18B20...
2025-10-30 15:30:01 - INFO - ✅ Sensor detectado: /sys/bus/w1/devices/28-xxxx
2025-10-30 15:30:01 - INFO - 🔌 Conectando a broker MQTT 10.150.253.2:1883...
2025-10-30 15:30:02 - INFO - ✅ Conectado exitosamente al broker MQTT

============================================================
📊 LECTURAS DE SENSORES
============================================================
2025-10-30 15:30:03 - INFO - 🎛 Potenciómetro 1 (A0): 1.65 V
2025-10-30 15:30:03 - INFO - 🎛 Potenciómetro 2 (A1): 2.10 V
2025-10-30 15:30:03 - INFO - 🧪 Sensor pH (A2): pH estimado 7.20
2025-10-30 15:30:03 - INFO - 🌊 Oxígeno disuelto (A3): 8.50 mg/L
2025-10-30 15:30:03 - INFO - 🌡 Temperatura: 25.5 °C
============================================================

2025-10-30 15:30:03 - INFO - 📦 Enviando datos: {"Sensor": "ULEAMCENTRAL02", ...}
2025-10-30 15:30:03 - INFO - 😴 Esperando 4.8 segundos hasta el próximo muestreo...
```

**Dejar correr por 30 segundos (6 ciclos) y luego presionar Ctrl+C**

**Estado:** ⬜ Completado

---

### ✅ Paso 5: Verificar Archivo de Log

```bash
# Ver dónde se guardó el log
ls -lh ~/iot_logs/

# Ver contenido del log
cat ~/iot_logs/iot_sensor_system.log

# O ver en tiempo real
tail -f ~/iot_logs/iot_sensor_system.log
```

**Qué verificar:**
- ✅ El archivo existe
- ✅ Contiene los registros de las lecturas
- ✅ No hay errores críticos

**Estado:** ⬜ Completado

---

### ✅ Paso 6: Prueba con Intervalo Normal

```bash
# Ejecutar con intervalo de 10 segundos
python3 iot_sensor_system.py --interval 10
```

**Dejar correr por 1 minuto y verificar que funciona correctamente**

**Estado:** ⬜ Completado

---

### ✅ Paso 7: Instalación del Servicio (Opcional - Para Producción)

```bash
# Solo si todos los pasos anteriores funcionaron
sudo ./iot_service_manager.sh install
```

**Qué hace:**
- Crea `/home/pi/iot_sensors/`
- Copia el script Python
- Instala el servicio systemd
- Crea `/var/log/iot_sensor_system.log` con permisos correctos

**Estado:** ⬜ Completado

---

### ✅ Paso 8: Iniciar Servicio (Si instalaste en Paso 7)

```bash
sudo ./iot_service_manager.sh start
```

**Verificar estado:**
```bash
sudo ./iot_service_manager.sh status
```

**Estado:** ⬜ Completado

---

### ✅ Paso 9: Monitoreo del Servicio (Si instalaste)

```bash
# Ver logs en tiempo real
sudo ./iot_service_manager.sh logs

# O con journalctl
sudo journalctl -u iot-sensor-system -f
```

**Dejar corriendo por 5 minutos y verificar:**
- ✅ Sin errores
- ✅ Datos enviándose correctamente
- ✅ Sensores leyendo valores

**Estado:** ⬜ Completado

---

## 🎯 RESUMEN DE ESTADOS

Marca con ✅ cada paso completado:

```
[ ] Paso 1: Archivos verificados
[ ] Paso 2: Permisos configurados
[ ] Paso 3: Diagnóstico ejecutado sin errores
[ ] Paso 4: Prueba rápida exitosa (30 segundos)
[ ] Paso 5: Archivo de log creado correctamente
[ ] Paso 6: Prueba con intervalo normal exitosa
[ ] Paso 7: Servicio instalado (opcional)
[ ] Paso 8: Servicio iniciado y funcionando (opcional)
[ ] Paso 9: Monitoreo exitoso (opcional)
```

---

## ✅ CRITERIOS DE ÉXITO

El sistema funciona correctamente si:

1. ✅ **No hay errores de permisos** - El programa inicia sin problemas
2. ✅ **Los sensores leen datos** - Se muestran valores de temperatura, pH, etc.
3. ✅ **MQTT conecta** - Mensaje "Conectado exitosamente al broker MQTT"
4. ✅ **Los logs se guardan** - Archivo de log se crea y se actualiza
5. ✅ **El sistema es estable** - Corre sin colgarse por varios minutos

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Problema: Sensor no detectado

```bash
# Verificar I2C
sudo i2cdetect -y 1

# Verificar 1-Wire
ls /sys/bus/w1/devices/
```

**Solución:** Verifica conexiones físicas y habilitación en `raspi-config`

---

### Problema: No conecta a MQTT

```bash
# Verificar conectividad
ping 10.150.253.2

# Verificar puerto
nc -zv 10.150.253.2 1883
```

**Solución:** Verifica red y credenciales MQTT

---

### Problema: Valores de sensores incorrectos

**Solución:** 
- Calibrar sensores
- Verificar rangos de voltaje
- Consultar hojas de datos de sensores

---

## 📊 REGISTRO DE PRUEBAS

### Información del Sistema:
```bash
# Hardware
Raspberry Pi: _____________
Sistema Operativo: _____________
Python Version: _____________

# Fecha de prueba: _____________
# Hora de inicio: _____________
# Hora de finalización: _____________
```

### Resultados:
```
Diagnóstico: [ ] OK  [ ] Falló
Prueba rápida: [ ] OK  [ ] Falló
Instalación servicio: [ ] OK  [ ] Falló  [ ] No aplicado
```

### Observaciones:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎉 ¡FELICITACIONES!

Si completaste todos los pasos marcados con ✅, tu sistema está:

- ✅ **Funcionando correctamente**
- ✅ **Sin errores de permisos**
- ✅ **Listo para uso en producción**
- ✅ **Monitoreando sensores exitosamente**

---

## 📞 SIGUIENTE PASO

Según tu caso de uso:

### Para Desarrollo/Pruebas:
```bash
# Ejecutar manualmente cuando necesites
python3 iot_sensor_system.py --interval 60
```

### Para Producción:
```bash
# Habilitar inicio automático
sudo ./iot_service_manager.sh enable

# El sistema ahora iniciará automáticamente al encender el Raspberry Pi
```

---

¿Todo funcionó? ¡Excelente! 🎊  
¿Algún problema? Consulta `SOLUCION_PERMISOS.md` o `EJEMPLOS_DE_USO.md`
