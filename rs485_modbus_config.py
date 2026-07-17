#!/usr/bin/env python3
"""Herramienta para leer o cambiar direccion/baudrate Modbus de sensores RS485."""

import argparse
import json
import sys
import time

from rs485_ec_sensor import BAUDRATE_CODE_TO_VALUE, auto_detect_port, create_instrument


REGISTER_DEVICE_ADDRESS = 0x07D0
REGISTER_DEVICE_BAUDRATE = 0x07D1

BAUDRATE_VALUE_TO_CODE = {value: code for code, value in BAUDRATE_CODE_TO_VALUE.items()}


def read_config(instrument) -> dict:
    address = instrument.read_register(REGISTER_DEVICE_ADDRESS, functioncode=3)
    baudrate_code = instrument.read_register(REGISTER_DEVICE_BAUDRATE, functioncode=3)
    return {
        'slave_address': address,
        'baudrate_code': baudrate_code,
        'baudrate': BAUDRATE_CODE_TO_VALUE.get(baudrate_code, 'desconocido'),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Leer o cambiar configuracion Modbus RS485')
    parser.add_argument('--port', help='Puerto serie, por ejemplo /dev/ttyUSB0')
    parser.add_argument('--current-address', type=int, default=1, help='Direccion actual del sensor')
    parser.add_argument('--baudrate', type=int, default=4800, help='Baudrate actual del sensor')
    parser.add_argument('--timeout', type=float, default=1.0, help='Timeout de lectura en segundos')
    parser.add_argument('--new-address', type=int, help='Nueva direccion Modbus (1-254)')
    parser.add_argument('--new-baudrate', type=int, choices=sorted(BAUDRATE_VALUE_TO_CODE), help='Nuevo baudrate Modbus')
    parser.add_argument('--json', action='store_true', help='Salida en JSON')
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        port = args.port or auto_detect_port()
        print(f'Usando puerto: {port}')
        instrument = create_instrument(port, args.current_address, args.baudrate, args.timeout)

        before = read_config(instrument)
        if args.json:
            print(json.dumps({'before': before}, ensure_ascii=True, indent=2))
        else:
            print(f"Configuracion actual: slave={before['slave_address']}, baudrate={before['baudrate']}")

        if args.new_address is None and args.new_baudrate is None:
            return 0

        if args.new_address is not None:
            if not 1 <= args.new_address <= 254:
                raise ValueError('La nueva direccion debe estar entre 1 y 254')
            instrument.write_register(REGISTER_DEVICE_ADDRESS, args.new_address, functioncode=6)
            print(f'Direccion cambiada a {args.new_address}')

        if args.new_baudrate is not None:
            baudrate_code = BAUDRATE_VALUE_TO_CODE[args.new_baudrate]
            instrument.write_register(REGISTER_DEVICE_BAUDRATE, baudrate_code, functioncode=6)
            print(f'Baudrate cambiado a {args.new_baudrate}')

        # Algunos sensores requieren reabrir el puerto con la nueva configuracion.
        time.sleep(1)
        verify_address = args.new_address if args.new_address is not None else args.current_address
        verify_baudrate = args.new_baudrate if args.new_baudrate is not None else args.baudrate
        verify_instrument = create_instrument(port, verify_address, verify_baudrate, args.timeout)
        after = read_config(verify_instrument)

        if args.json:
            print(json.dumps({'after': after}, ensure_ascii=True, indent=2))
        else:
            print(f"Configuracion verificada: slave={after['slave_address']}, baudrate={after['baudrate']}")
        return 0
    except KeyboardInterrupt:
        print('Operacion interrumpida por el usuario')
        return 0
    except Exception as exc:
        print(f'Error al configurar el sensor: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
