#!/usr/bin/env python3
"""
Script de prueba rápida del sistema IoT
Ejecuta el sistema con intervalo de 5 segundos para verificación
"""

import os
import sys

# Banner
print("""
╔══════════════════════════════════════════════════════════════╗
║         PRUEBA RÁPIDA - SISTEMA IOT ULEAM                    ║
║         Intervalo: 5 segundos (solo para pruebas)            ║
╚══════════════════════════════════════════════════════════════╝
""")

print("🔍 Iniciando en modo de prueba...")
print("⏱️  El sistema tomará muestras cada 5 segundos")
print("🛑 Presiona Ctrl+C para detener\n")

# Importar y ejecutar el sistema principal
try:
    # Agregar el directorio actual al path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Importar el módulo principal
    import iot_sensor_system
    
    # Ejecutar con intervalo de 5 segundos
    iot_sensor_system.main(sample_interval=5)
    
except KeyboardInterrupt:
    print("\n\n✅ Prueba detenida por el usuario")
    print("Si todo funcionó correctamente, puedes:")
    print("  1. Instalar el servicio: sudo ./iot_service_manager.sh install")
    print("  2. Configurar el intervalo deseado en el archivo .service")
    print("  3. Iniciar el servicio: sudo ./iot_service_manager.sh start\n")
    sys.exit(0)
    
except ImportError as e:
    print(f"\n❌ Error al importar el módulo: {e}")
    print("Asegúrate de que iot_sensor_system.py está en el mismo directorio\n")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error durante la prueba: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
