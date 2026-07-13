# ⚠️ SOLUCIÓN AL ERROR DE PERMISOS

## Problema
```
PermissionError: [Errno 13] Permission denied: '/var/log/iot_sensor_system.log'
```

## ✅ Soluciones (Elige una opción)

---

### 🎯 **OPCIÓN 1: Ejecución Manual (SIN permisos de root)**

El código ya está **corregido** para manejar esto automáticamente:

```bash
# Simplemente ejecuta el script
python3 iot_sensor_system.py

# El log se guardará automáticamente en:
# ~/iot_logs/iot_sensor_system.log
```

**✅ Ventaja:** No necesitas permisos de root  
**ℹ️ Ubicación del log:** `~/iot_logs/iot_sensor_system.log`

---

### 🎯 **OPCIÓN 2: Ejecutar con sudo (CON permisos de root)**

```bash
# Ejecutar como root
sudo python3 iot_sensor_system.py

# El log se guardará en:
# /var/log/iot_sensor_system.log
```

**✅ Ventaja:** Log en ubicación estándar del sistema  
**ℹ️ Ubicación del log:** `/var/log/iot_sensor_system.log`

---

### 🎯 **OPCIÓN 3: Crear archivo de log con permisos (Recomendado para servicio)**

```bash
# Crear el archivo de log con permisos correctos
sudo touch /var/log/iot_sensor_system.log
sudo chown $USER:$USER /var/log/iot_sensor_system.log
sudo chmod 644 /var/log/iot_sensor_system.log

# Ahora ejecuta sin sudo
python3 iot_sensor_system.py
```

**✅ Ventaja:** Mejor práctica, funciona como usuario normal y como servicio

---

### 🎯 **OPCIÓN 4: Instalación Completa del Servicio**

```bash
# Usar el script de instalación (esto configura TODO correctamente)
chmod +x iot_service_manager.sh
sudo ./iot_service_manager.sh install

# Esto automáticamente:
# - Crea el directorio de instalación
# - Configura el archivo de log con permisos correctos
# - Instala el servicio systemd
# - Prepara todo para producción

# Luego inicia el servicio
sudo ./iot_service_manager.sh start
```

**✅ Ventaja:** Configuración profesional completa  
**🎯 Recomendado:** Para uso en producción

---

## 🔍 Verificar Dónde se Guarda el Log

Cuando ejecutes el programa, verás un mensaje al inicio indicando dónde se guardó el log:

```
2025-10-30 15:30:00 - INFO - 📝 Archivo de log: /home/usuario/iot_logs/iot_sensor_system.log
```

---

## 📊 Ver los Logs

### Si usas ejecución manual:
```bash
# Ver log en tiempo real (usuario normal)
tail -f ~/iot_logs/iot_sensor_system.log

# Ver últimas 50 líneas
tail -n 50 ~/iot_logs/iot_sensor_system.log
```

### Si usas el servicio systemd:
```bash
# Ver logs del servicio
sudo journalctl -u iot-sensor-system -f

# O usar el script de gestión
sudo ./iot_service_manager.sh logs
```

---

## 🚀 INICIO RÁPIDO (Solución Inmediata)

```bash
# El código YA ESTÁ CORREGIDO - solo ejecuta:
python3 iot_sensor_system.py

# ¡Eso es todo! El log se guardará automáticamente en tu home
```

---

## 🎓 Explicación Técnica

El código ahora incluye una función inteligente que:

1. **Intenta** crear el log en `/var/log/` (ubicación estándar)
2. **Si falla** (sin permisos), automáticamente crea el log en `~/iot_logs/`
3. **Informa** al usuario dónde se guardó el archivo

Código implementado:
```python
def get_log_file_path():
    """Obtiene la ruta del archivo de log según permisos disponibles"""
    var_log_path = '/var/log/iot_sensor_system.log'
    try:
        with open(var_log_path, 'a') as f:
            pass
        return var_log_path
    except PermissionError:
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, 'iot_logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'iot_sensor_system.log')
```

---

## ✅ Resumen

| Método | Comando | Ubicación Log | Permisos Requeridos |
|--------|---------|---------------|---------------------|
| **Ejecución simple** | `python3 iot_sensor_system.py` | `~/iot_logs/` | Ninguno ⭐ |
| **Con sudo** | `sudo python3 iot_sensor_system.py` | `/var/log/` | Root |
| **Pre-configurado** | Crear archivo primero | `/var/log/` | Una vez como root |
| **Servicio completo** | `sudo ./iot_service_manager.sh install` | `/var/log/` | Root |

**Recomendación:** Usa la **Ejecución simple** para pruebas y el **Servicio completo** para producción.

---

¡El problema está resuelto! 🎉
