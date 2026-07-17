#!/usr/bin/env python3
"""Lee el sensor DFRobot SEN0710 por RS485/Modbus RTU."""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

from rs485_ec_sensor import BAUDRATE_CODE_TO_VALUE, auto_detect_port, create_instrument


DEFAULT_SLAVE_ADDRESS = 1
DEFAULT_BAUDRATE = 4800
DEFAULT_TIMEOUT = 1.0
DEFAULT_INTERVAL = 2.0

REGISTER_TURBIDITY = 0x0000
REGISTER_TEMPERATURE = 0x0001
REGISTER_DEVICE_ADDRESS = 0x07D0
REGISTER_DEVICE_BAUDRATE = 0x07D1


def read_measurements(instrument) -> dict:
    registers = instrument.read_registers(REGISTER_TURBIDITY, 2, functioncode=3)
    turbidity_ntu = int(registers[0]) / 10.0
    temperature_c = int(registers[1]) / 10.0

    now = datetime.now(timezone.utc)
    return {
        'timestamp': int(now.timestamp()),
        'dateTime': now.isoformat(),
        'turbidity_ntu': turbidity_ntu,
        'temperature_c': temperature_c,
    }


def read_device_info(instrument) -> dict:
    address = instrument.read_register(REGISTER_DEVICE_ADDRESS, functioncode=3)
    baudrate_code = instrument.read_register(REGISTER_DEVICE_BAUDRATE, functioncode=3)
    return {
        'slave_address': address,
        'baudrate_code': baudrate_code,
        'baudrate': BAUDRATE_CODE_TO_VALUE.get(baudrate_code, 'desconocido'),
    }


def print_human_reading(data: dict) -> None:
    print(
        f"[{data['dateTime']}] Turbidez={data['turbidity_ntu']:.1f} NTU | "
        f"Temp={data['temperature_c']:.1f} C"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Lectura del sensor de turbidez RS485 DFRobot SEN0710')
    parser.add_argument('--port', help='Puerto serie, por ejemplo /dev/ttyUSB0')
    parser.add_argument('--address', type=int, default=DEFAULT_SLAVE_ADDRESS, help='Direccion Modbus del sensor')
    parser.add_argument('--baudrate', type=int, default=DEFAULT_BAUDRATE, help='Baudrate del sensor')
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help='Timeout de lectura en segundos')
    parser.add_argument('--interval', type=float, default=DEFAULT_INTERVAL, help='Intervalo entre lecturas')
    parser.add_argument('--count', type=int, default=0, help='Cantidad de lecturas. 0 = infinito')
    parser.add_argument('--json', action='store_true', help='Imprime cada lectura como JSON')
    parser.add_argument('--device-info', action='store_true', help='Lee y muestra direccion y baudrate configurados')
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        port = args.port or auto_detect_port()
        print(f'Usando puerto: {port}')
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
        print('Lectura interrumpida por el usuario')
        return 0
    except Exception as exc:
        print(f'Error al leer el sensor: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
