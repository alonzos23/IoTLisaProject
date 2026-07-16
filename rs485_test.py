#!/usr/bin/env python3
import time
import minimalmodbus
import serial.tools.list_ports

print("🔍 Iniciando prueba de sensores RS485...\n")

# ================= CONFIGURACIÓN =================
BAUDRATE = 9600
TIMEOUT = 1

def find_rs485_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB" in port.device.upper() or "ACM" in port.device.upper():
            print(f"✅ Puerto RS485 detectado: {port.device}")
            return port.device
    print("⚠️ Usando /dev/ttyUSB0 por defecto")
    return "/dev/ttyUSB0"

port = find_rs485_port()

try:
    # Sensor de Turbidez
    turb = minimalmodbus.Instrument(port, slaveaddress=1)
    turb.serial.baudrate = BAUDRATE
    turb.serial.timeout = TIMEOUT
    turb.serial.parity = minimalmodbus.serial.PARITY_NONE

    # Sensor de Salinidad / Conductividad
    sal = minimalmodbus.Instrument(port, slaveaddress=2)
    sal.serial.baudrate = BAUDRATE
    sal.serial.timeout = TIMEOUT
    sal.serial.parity = minimalmodbus.serial.PARITY_NONE

    print("✅ Conexiones listas. Iniciando lecturas...\n")
    print("="*70)

    while True:
        try:
            turbidity = turb.read_register(0, number_of_decimals=1, functioncode=3)
            print(f"🌊 Turbidez           → {turbidity:.1f} NTU")

            conductivity = sal.read_register(0, number_of_decimals=1, functioncode=3)
            print(f"💧 Conductividad/Salinidad → {conductivity:.1f} µS/cm")

        except Exception as e:
            print(f"❌ Error de lectura: {e}")

        print("-" * 70)
        time.sleep(5)

except Exception as e:
    print(f"❌ Error general: {e}")
