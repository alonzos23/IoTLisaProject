#!/usr/bin/env python3
"""Lee el sensor DFRobot SEN0707 por RS485/Modbus RTU."""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import minimalmodbus
import serial.tools.list_ports


DEFAULT_SLAVE_ADDRESS = 1
DEFAULT_BAUDRATE = 4800
DEFAULT_TIMEOUT = 1.0
DEFAULT_INTERVAL = 2.0

REGISTER_EC = 0x0000
REGISTER_TEMPERATURE = 0x0001
REGISTER_SALINITY = 0x0002
REGISTER_TDS = 0x0003
REGISTER_DEVICE_ADDRESS = 0x07D0
REGISTER_DEVICE_BAUDRATE = 0x07D1

BAUDRATE_CODE_TO_VALUE = {
    0: 2400,
    1: 4800,
    2: 9600,
    3: 19200,
    4: 38400,
    5: 57600,
    6: 115200,
    7: 1200,
}


def auto_detect_port() -> str:
    for port in serial.tools.list_ports.comports():
        device_upper = port.device.upper()
        if "USB" in device_upper or "ACM" in device_upper:
            return port.device
    raise RuntimeError("No se detecto ningun puerto serie USB/ACM")


def create_instrument(port: str, address: int, baudrate: int, timeout: float) -> minimalmodbus.Instrument:
    instrument = minimalmodbus.Instrument(port, address)
    instrument.serial.baudrate = baudrate
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = timeout
    instrument.mode = minimalmodbus.MODE_RTU
    instrument.clear_buffers_before_each_transaction = True
    instrument.close_port_after_each_call = False
    return instrument


def read_measurements(instrument: minimalmodbus.Instrument) -> dict:
    registers = instrument.read_registers(REGISTER_EC, 4, functioncode=3)
    ec_us_cm = int(registers[0])
    temperature_c = int(registers[1]) / 10.0
    salinity_ppm = int(registers[2])
    tds_ppm = int(registers[3])

    now = datetime.now(timezone.utc)
    return {
        "timestamp": int(now.timestamp()),
        "dateTime": now.isoformat(),
        "ec_us_cm": ec_us_cm,
        "temperature_c": temperature_c,
        "salinity_ppm": salinity_ppm,
        "tds_ppm": tds_ppm,
    }


def read_device_info(instrument: minimalmodbus.Instrument) -> dict:
    address = instrument.read_register(REGISTER_DEVICE_ADDRESS, functioncode=3)
    baudrate_code = instrument.read_register(REGISTER_DEVICE_BAUDRATE, functioncode=3)
    return {
        "slave_address": address,
        "baudrate_code": baudrate_code,
        "baudrate": BAUDRATE_CODE_TO_VALUE.get(baudrate_code, "desconocido"),
    }


def print_human_reading(data: dict) -> None:
    print(f"[{data['dateTime']}] EC={data['ec_us_cm']} uS/cm | "
          f"Temp={data['temperature_c']:.1f} C | "
          f"Salinidad={data['salinity_ppm']} ppm | "
          f"TDS={data['tds_ppm']} ppm")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lectura del sensor EC RS485 DFRobot SEN0707")
    parser.add_argument("--port", help="Puerto serie, por ejemplo /dev/ttyUSB0")
    parser.add_argument("--address", type=int, default=DEFAULT_SLAVE_ADDRESS, help="Direccion Modbus del sensor")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="Baudrate del sensor")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Timeout de lectura en segundos")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Intervalo entre lecturas")
    parser.add_argument("--count", type=int, default=0, help="Cantidad de lecturas. 0 = infinito")
    parser.add_argument("--json", action="store_true", help="Imprime cada lectura como JSON")
    parser.add_argument("--device-info", action="store_true", help="Lee y muestra direccion y baudrate configurados")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        port = args.port or auto_detect_port()
        print(f"Usando puerto: {port}")
        instrument = create_instrument(port, args.address, args.baudrate, args.timeout)

        if args.device_info:
            info = read_device_info(instrument)
            print(json.dumps(info, ensure_ascii=True, indent=2))
            if args.count == 0:
                return 0

        reads_done = 0
        while args.count == 0 or reads_done < args.count:
            data = read_measurements(instrument)
            if args.json:
                print(json.dumps(data, ensure_ascii=True))
            else:
                print_human_reading(data)
            reads_done += 1
            if args.count == 0 or reads_done < args.count:
                time.sleep(args.interval)

        return 0
    except KeyboardInterrupt:
        print("Lectura interrumpida por el usuario")
        return 0
    except Exception as exc:
        print(f"Error al leer el sensor: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
