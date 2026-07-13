# 🚀 SISTEMA DE MONITOREO IoT - RASPBERRY PI
## Código Mejorado y Optimizado para ULEAM

---

## 📦 CONTENIDO DEL PAQUETE

Este paquete contiene todos los archivos necesarios para implementar un sistema profesional de monitoreo IoT en Raspberry Pi con gestión completa de sensores, manejo robusto de errores y control como servicio systemd.

### 📁 Archivos Incluidos:

#### 1. **Código Principal**
- **`iot_sensor_system.py`** (17 KB)
  - Script principal mejorado y optimizado
  - Frecuencia de muestreo configurable (default: 3600 segundos)
  - Manejo robusto de errores
  - Lecturas sincronizadas
  - Sistema de logging profesional
  - Reconexión automática MQTT

#### 2. **Gestión de Servicio**
- **`iot-sensor-system.service`** (516 bytes)
  - Archivo de servicio systemd
  - Configuración para inicio automático
  - Gestión de reintentos
  
- **`iot_service_manager.sh`** (7.5 KB)
  - Script de gestión completo
  - Comandos: install, start, stop, restart, status, enable, disable, logs
  - Interfaz amigable con colores

#### 3. **Herramientas de Diagnóstico**
- **`diagnostic.py`** (11 KB)
  - Script para probar cada sensor individualmente
  - Verifica conectividad I2C, 1-Wire y MQTT
  - Reporta estado de salud de cada componente

#### 4. **Documentación**
- **`README.md`** (7.3 KB)
  - Guía completa de instalación y uso
  - Requisitos y dependencias
  - Configuración detallada
  - Solución de problemas

- **`MEJORAS_IMPLEMENTADAS.md`** (8.7 KB)
  - Resumen completo de todas las mejoras
  - Comparativa antes vs después
  - Lista de problemas solucionados
  - Nuevas funcionalidades

- **`EJEMPLOS_DE_USO.md`** (12 KB)
  - 10 escenarios prácticos paso a paso
  - Comandos útiles para el día a día
  - Tips y mejores prácticas
  - Scripts auxiliares

---

## 🎯 INICIO RÁPIDO

### Opción A: Lectura Completa (Recomendado para primera vez)

1. **Lee primero:** `README.md` - Instalación y configuración completa
2. **Revisa:** `MEJORAS_IMPLEMENTADAS.md` - Qué se mejoró y por qué
3. **Consulta:** `EJEMPLOS_DE_USO.md` - Escenarios prácticos
4. **Ejecuta:** Los comandos de instalación

### Opción B: Instalación Rápida (Si tienes experiencia)

```bash
# 1. Copiar archivos al Raspberry Pi
scp *.py *.sh *.service pi@TU_RASPBERRY_IP:~/

# 2. En el Raspberry Pi
chmod +x iot_service_manager.sh iot_sensor_system.py diagnostic.py

# 3. Instalar
sudo ./iot_service_manager.sh install

# 4. Iniciar
sudo ./iot_service_manager.sh start

# 5. Verificar
sudo ./iot_service_manager.sh status
```

---

## 📊 CARACTERÍSTICAS PRINCIPALES

### ✅ Mejoras Implementadas:

| Característica | Estado |
|---------------|--------|
| Errores de sintaxis corregidos | ✅ 6/6 |
| Frecuencia configurable | ✅ Default 3600s |
| Manejo de errores robusto | ✅ Implementado |
| Lecturas sincronizadas | ✅ Implementado |
| Sistema de logging | ✅ Archivo + Consola |
| Prevención de cuelgues | ✅ Implementado |
| Servicio systemd | ✅ Completo |
| Scripts de gestión | ✅ 7 comandos |
| Diagnóstico automático | ✅ Implementado |
| Documentación completa | ✅ 3 documentos |

---

## 📖 GUÍA DE LECTURA RECOMENDADA

### Para Principiantes:
1. `README.md` → Instalación paso a paso
2. `EJEMPLOS_DE_USO.md` → Escenarios 1, 2 y 5
3. Ejecutar `diagnostic.py`

### Para Usuarios Intermedios:
1. `MEJORAS_IMPLEMENTADAS.md` → Entender qué cambió
2. `README.md` → Sección de configuración
3. `EJEMPLOS_DE_USO.md` → Escenarios 3, 4, 6, 7

### Para Usuarios Avanzados:
1. `MEJORAS_IMPLEMENTADAS.md` → Arquitectura del código
2. `iot_sensor_system.py` → Revisar el código
3. `EJEMPLOS_DE_USO.md` → Escenarios 8, 9, 10

---

## 🔍 ESTRUCTURA DEL SISTEMA

```
Sistema IoT ULEAM
│
├── 📄 iot_sensor_system.py          # Cerebro del sistema
│   ├── MQTTPublisher                # Gestión MQTT
│   ├── SensorManager                # Gestión de sensores
│   └── main()                       # Bucle principal
│
├── ⚙️ iot-sensor-system.service     # Configuración systemd
│
├── 🛠️ iot_service_manager.sh        # Control del servicio
│   ├── install                      # Instalación
│   ├── start/stop/restart           # Control básico
│   ├── enable/disable               # Auto-inicio
│   └── logs/status                  # Monitoreo
│
├── 🔍 diagnostic.py                 # Herramienta de pruebas
│   ├── test_board()                 # Prueba placa
│   ├── test_sensors()               # Prueba cada sensor
│   └── test_mqtt()                  # Prueba conectividad
│
└── 📚 Documentación
    ├── README.md                    # Guía principal
    ├── MEJORAS_IMPLEMENTADAS.md     # Resumen técnico
    └── EJEMPLOS_DE_USO.md           # Casos prácticos
```

---

## 🎓 CASOS DE USO PRINCIPALES

### 1. **Monitoreo Continuo** (Producción)
```bash
# Instalar y configurar con muestreo cada hora
sudo ./iot_service_manager.sh install
sudo ./iot_service_manager.sh enable
sudo ./iot_service_manager.sh start
```

### 2. **Pruebas y Desarrollo** (Testing)
```bash
# Ejecutar manualmente con muestreo rápido
python3 iot_sensor_system.py --interval 10
```

### 3. **Diagnóstico de Problemas**
```bash
# Ejecutar herramienta de diagnóstico
python3 diagnostic.py
```

### 4. **Monitoreo de Logs**
```bash
# Ver logs en tiempo real
sudo ./iot_service_manager.sh logs
```

---

## 🆘 RESOLUCIÓN RÁPIDA DE PROBLEMAS

| Problema | Solución Rápida | Documento |
|----------|----------------|-----------|
| Servicio no inicia | `python3 diagnostic.py` | README.md #diagnóstico |
| Sensor no responde | Ver logs con `iot_service_manager.sh logs` | EJEMPLOS_DE_USO.md #escenario-5 |
| Error de MQTT | Verificar conectividad de red | EJEMPLOS_DE_USO.md #escenario-8 |
| Cambiar frecuencia | Editar archivo .service | EJEMPLOS_DE_USO.md #escenario-3 |
| Ver datos enviados | `mosquitto_sub` al topic | EJEMPLOS_DE_USO.md #escenario-6 |

---

## 📞 CONTACTO Y SOPORTE

### Archivos de Log:
- **Sistema:** `/var/log/iot_sensor_system.log`
- **Journald:** `sudo journalctl -u iot-sensor-system`

### Comandos Útiles:
```bash
# Estado del servicio
sudo systemctl status iot-sensor-system

# Últimos logs
sudo journalctl -u iot-sensor-system -n 50

# Diagnóstico completo
python3 diagnostic.py
```

---

## 📝 NOTAS IMPORTANTES

### ⚡ Antes de Empezar:
1. ✅ Verificar que I2C está habilitado
2. ✅ Verificar que 1-Wire está habilitado
3. ✅ Instalar dependencias Python (paho-mqtt, DFRobot)
4. ✅ Verificar conexiones de sensores

### 🎯 Después de Instalar:
1. ✅ Ejecutar `diagnostic.py` para verificar todo
2. ✅ Probar manualmente antes de instalar servicio
3. ✅ Configurar frecuencia de muestreo deseada
4. ✅ Habilitar inicio automático

### 🔒 Seguridad:
- Los logs pueden contener información sensible
- Cambiar credenciales MQTT en producción
- Limitar acceso SSH al Raspberry Pi
- Hacer backups regulares de la configuración

---

## 🎉 ¡LISTO PARA PRODUCCIÓN!

Este sistema ha sido diseñado y probado para:
- ✅ **Alta disponibilidad** - Continúa operando si un sensor falla
- ✅ **Fácil gestión** - Scripts intuitivos para todas las operaciones
- ✅ **Observabilidad** - Logs detallados y herramientas de diagnóstico
- ✅ **Configurabilidad** - Parámetros ajustables según necesidades
- ✅ **Documentación completa** - Guías para todos los niveles

---

## 📚 ORDEN DE LECTURA SUGERIDO

```
1. LEEME_PRIMERO.md (este archivo) ← ESTÁS AQUÍ
   └─ Panorama general del sistema
      
2. README.md
   └─ Instalación y configuración detallada
      
3. diagnostic.py (ejecutar)
   └─ Verificar que todo funciona
      
4. MEJORAS_IMPLEMENTADAS.md
   └─ Entender qué se mejoró
      
5. EJEMPLOS_DE_USO.md
   └─ Casos prácticos y tips
      
6. iot_sensor_system.py (revisar código)
   └─ Código fuente documentado
```

---

## 🚀 COMANDOS ESENCIALES

```bash
# Instalación (primera vez)
sudo ./iot_service_manager.sh install

# Control diario
sudo ./iot_service_manager.sh start
sudo ./iot_service_manager.sh stop
sudo ./iot_service_manager.sh restart
sudo ./iot_service_manager.sh status

# Monitoreo
sudo ./iot_service_manager.sh logs
tail -f /var/log/iot_sensor_system.log

# Diagnóstico
python3 diagnostic.py

# Pruebas
python3 iot_sensor_system.py --interval 10
```

---

**Versión:** 1.0  
**Fecha:** Enero 2026
**Institución:** ULEAM  
**Estado:** ✅ Listo para Producción

---

### 💡 ¿Necesitas Ayuda?

1. **Primero:** Lee el `README.md` completo
2. **Segundo:** Ejecuta `diagnostic.py`
3. **Tercero:** Revisa `EJEMPLOS_DE_USO.md` para tu caso
4. **Cuarto:** Consulta los logs del sistema

¡Buena suerte con tu sistema de monitoreo IoT! 🎊
