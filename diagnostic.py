#!/usr/bin/env python3
"""
Script de diagnóstico para el sistema de sensores IoT
Prueba cada sensor individualmente y reporta su estado
"""

import sys
import time
import glob
from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board

VREF = 3.3

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_status(sensor_name, status, details=""):
    """Imprime el estado de un sensor"""
    icon = "✅" if status else "❌"
    status_text = "OK" if status else "FALLO"
    print(f"{icon} {sensor_name}: {status_text}")
    if details:
        print(f"   └─ {details}")

def test_board():
    """Prueba la placa DFRobot"""
    print_header("1. PRUEBA DE PLACA DFROBOT")
    
    try:
        board = Board(1, 0x10)
        board.detecte()
        
        if board.begin() == board.STA_OK:
            print_status("Placa DFRobot", True, "Bus I2C 1, Dirección 0x10")
            board.set_adc_enable()
            return board
        else:
            print_status("Placa DFRobot", False, "No se pudo inicializar")
            return None
    except Exception as e:
        print_status("Placa DFRobot", False, f"Error: {e}")
        return None

def test_i2c():
    """Verifica dispositivos I2C"""
    print_header("2. DISPOSITIVOS I2C DETECTADOS")
    
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        if "10" in result.stdout:
            print_status("Dispositivo 0x10", True, "DFRobot Expansion Board detectado")
            return True
        else:
            print_status("Dispositivo 0x10", False, "No se detectó la placa")
            return False
    except Exception as e:
        print(f"❌ Error al ejecutar i2cdetect: {e}")
        print("   Intenta ejecutar manualmente: sudo i2cdetect -y 1")
        return False

def test_potentiometers(board):
    """Prueba los potenciómetros en A0 y A1"""
    print_header("3. PRUEBA DE POTENCIÓMETROS")
    
    if board is None:
        print("⚠️  Saltando prueba (placa no disponible)")
        return
    
    try:
        # Probar A0
        valor_a0 = board.get_adc_value(board.A0)
        voltaje_a0 = (valor_a0 / 4095.0) * VREF
        print_status("Potenciómetro A0", True, 
                    f"Valor ADC: {valor_a0}, Voltaje: {voltaje_a0:.3f}V")
        
        # Probar A1
        valor_a1 = board.get_adc_value(board.A1)
        voltaje_a1 = (valor_a1 / 4095.0) * VREF
        print_status("Potenciómetro A1", True, 
                    f"Valor ADC: {valor_a1}, Voltaje: {voltaje_a1:.3f}V")
        
        print("\n💡 Gira los potenciómetros y ejecuta de nuevo para ver cambios")
        
    except Exception as e:
        print_status("Potenciómetros", False, f"Error: {e}")

def test_ph_sensor(board):
    """Prueba el sensor de pH en A2"""
    print_header("4. PRUEBA DE SENSOR DE pH")
    
    if board is None:
        print("⚠️  Saltando prueba (placa no disponible)")
        return
    
    try:
        valor_ph = board.get_adc_value(board.A2)
        voltaje_ph = (valor_ph / 4095.0) * VREF
        ph = 7 + ((2.5 - voltaje_ph) / 0.18)
        
        print_status("Sensor pH A2", True, 
                    f"Valor ADC: {valor_ph}, Voltaje: {voltaje_ph:.3f}V, pH: {ph:.2f}")
        
        # Verificar rango razonable
        if 0 <= ph <= 14:
            print("   ✓ pH en rango válido (0-14)")
        else:
            print("   ⚠️  pH fuera de rango normal - verificar calibración")
            
    except Exception as e:
        print_status("Sensor pH", False, f"Error: {e}")

def test_do_sensor(board):
    """Prueba el sensor de oxígeno disuelto en A3"""
    print_header("5. PRUEBA DE SENSOR DE OXÍGENO DISUELTO")
    
    if board is None:
        print("⚠️  Saltando prueba (placa no disponible)")
        return
    
    try:
        valor_do = board.get_adc_value(board.A3)
        voltaje_do = (valor_do / 4095.0) * VREF
        mg_L = (voltaje_do / 3.0) * 20.0
        
        print_status("Sensor O2 A3", True, 
                    f"Valor ADC: {valor_do}, Voltaje: {voltaje_do:.3f}V, O2: {mg_L:.2f} mg/L")
        
        # Verificar rango típico
        if 0 <= mg_L <= 20:
            print("   ✓ Oxígeno en rango típico (0-20 mg/L)")
        else:
            print("   ⚠️  Lectura fuera de rango normal - verificar sensor")
            
    except Exception as e:
        print_status("Sensor O2", False, f"Error: {e}")

def test_ds18b20():
    """Prueba el sensor de temperatura DS18B20"""
    print_header("6. PRUEBA DE SENSOR DS18B20 (TEMPERATURA)")
    
    try:
        base_dir = '/sys/bus/w1/devices/'
        dispositivos = glob.glob(base_dir + '28*')
        
        if not dispositivos:
            print_status("Sensor DS18B20", False, 
                        "No se detectó. Verifica: 1-Wire habilitado, conexión física")
            print("\n   Para habilitar 1-Wire:")
            print("   1. sudo raspi-config")
            print("   2. Interface Options > 1-Wire > Enable")
            print("   3. sudo reboot")
            return
        
        device_file = dispositivos[0] + '/w1_slave'
        print_status("Sensor DS18B20", True, f"Detectado en {dispositivos[0]}")
        
        # Intentar leer temperatura
        with open(device_file, 'r') as f:
            lines = f.readlines()
        
        # Verificar lectura válida
        retry = 0
        while lines[0].strip()[-3:] != 'YES' and retry < 3:
            time.sleep(0.5)
            with open(device_file, 'r') as f:
                lines = f.readlines()
            retry += 1
        
        if lines[0].strip()[-3:] != 'YES':
            print_status("Lectura de temperatura", False, 
                        "No se obtienen datos válidos después de reintentos")
            return
        
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            print_status("Lectura de temperatura", True, 
                        f"Temperatura: {temp_c:.2f}°C")
            
            # Verificar rango razonable
            if -20 <= temp_c <= 60:
                print("   ✓ Temperatura en rango razonable")
            else:
                print("   ⚠️  Temperatura fuera de rango típico")
        else:
            print_status("Lectura de temperatura", False, 
                        "No se encontró el valor en la respuesta")
            
    except FileNotFoundError:
        print_status("Sensor DS18B20", False, 
                    "Archivo de dispositivo no encontrado")
    except Exception as e:
        print_status("Sensor DS18B20", False, f"Error: {e}")

def test_mqtt_connection():
    """Prueba la conexión MQTT"""
    print_header("7. PRUEBA DE CONEXIÓN MQTT")
    
    try:
        import socket
        from paho.mqtt.client import Client as MQTTClient
        
        BROKER = '10.150.253.2'
        PORT = 1883
        
        # Verificar conectividad de red al broker
        print("🔍 Verificando conectividad de red...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((BROKER, PORT))
        sock.close()
        
        if result == 0:
            print_status(f"Conectividad a {BROKER}:{PORT}", True, 
                        "Puerto accesible")
        else:
            print_status(f"Conectividad a {BROKER}:{PORT}", False, 
                        "No se puede alcanzar el broker")
            return
        
        # Intentar conexión MQTT
        print("\n🔍 Probando autenticación MQTT...")
        client = MQTTClient("diagnostic-test")
        client.username_pw_set('mqtt-uleam', 'Mqtt-Uleam2025$')
        
        connected = False
        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            connected = (rc == 0)
        
        client.on_connect = on_connect
        client.connect(BROKER, PORT, keepalive=10)
        client.loop_start()
        
        time.sleep(2)
        
        if connected:
            print_status("Autenticación MQTT", True, 
                        "Credenciales correctas")
            client.disconnect()
            client.loop_stop()
        else:
            print_status("Autenticación MQTT", False, 
                        "Verifica usuario/contraseña")
            
    except ImportError:
        print_status("Librería paho-mqtt", False, 
                    "No instalada. Ejecuta: pip3 install paho-mqtt")
    except Exception as e:
        print_status("Conexión MQTT", False, f"Error: {e}")

def print_summary():
    """Imprime un resumen y recomendaciones"""
    print_header("RESUMEN Y RECOMENDACIONES")
    
    print("""
📋 CHECKLIST DE VERIFICACIÓN:

Hardware:
 □ Todos los cables están bien conectados
 □ La placa DFRobot está alimentada correctamente
 □ Los sensores están conectados a los puertos correctos
 □ El DS18B20 tiene resistencia pull-up de 4.7kΩ

Configuración Raspberry Pi:
 □ I2C está habilitado (sudo raspi-config)
 □ 1-Wire está habilitado (sudo raspi-config)
 □ El usuario tiene permisos para I2C y GPIO

Red:
 □ Raspberry Pi tiene conectividad a internet
 □ Puede hacer ping al broker MQTT
 □ No hay firewall bloqueando el puerto 1883

Software:
 □ Python 3 está instalado
 □ Librería paho-mqtt está instalada
 □ Librería DFRobot está instalada

Si algún sensor falla:
1. Verifica las conexiones físicas
2. Revisa los logs: /var/log/iot_sensor_system.log
3. Ejecuta este diagnóstico de nuevo
4. Consulta el README.md para más detalles
    """)

def main():
    """Función principal"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         DIAGNÓSTICO DEL SISTEMA DE SENSORES IoT - ULEAM           ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Ejecutar todas las pruebas
    test_i2c()
    board = test_board()
    test_potentiometers(board)
    test_ph_sensor(board)
    test_do_sensor(board)
    test_ds18b20()
    test_mqtt_connection()
    print_summary()
    
    print("\n" + "="*70)
    print("✅ Diagnóstico completado")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnóstico interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado durante el diagnóstico: {e}")
        sys.exit(1)
