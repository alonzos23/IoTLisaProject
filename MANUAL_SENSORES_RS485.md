# Manual de Uso y Cuidado de Sensores RS485 Nuevos

## Alcance

Este documento cubre los sensores nuevos trabajados en esta etapa:

- `SEN0707`: conductividad, salinidad y TDS
- `SEN0710`: turbidez

No cubre en detalle los sensores antiguos del proyecto.

## Reglas generales

- usar siempre la alimentacion correcta del fabricante
- no alimentar estos sensores directamente desde el USB de la Raspberry Pi
- verificar polaridad y cableado antes de conectar
- no dejar residuos de tierra, sal o sedimento pegados despues de usarlos

## Cableado comun

Ambos sensores usan:

- `Brown`: `VCC`
- `Black`: `GND`
- `Yellow`: `485-A`
- `Blue`: `485-B`

## Uso en el mismo bus RS485

Se pueden conectar ambos sensores al mismo adaptador `USB-RS485` si:

- comparten `A`
- comparten `B`
- comparten `GND`
- tienen direcciones Modbus diferentes

Configuracion recomendada:

- `SEN0707 = slave 1`
- `SEN0710 = slave 2`

## Sensor SEN0707

### Para que sirve

Mide:

- conductividad `EC`
- salinidad
- `TDS`
- temperatura interna de compensacion

### Buenas practicas de uso

- sumergir correctamente la zona sensora
- esperar estabilizacion antes de confiar en la lectura
- evitar burbujas en la punta
- si se hace una prueba con agua muy salada, luego enjuagar bien

### Limpieza

Si se uso en agua con tierra, sales o suciedad:

1. enjuagar con agua limpia
2. retirar residuos sin raspar
3. dejar escurrir
4. secar superficialmente por fuera con paño suave o microfibra

Evitar:

- raspar la superficie sensora
- usar cepillos duros
- usar calor fuerte para secar
- guardar con costras de sal

### Secado y guardado

- dejar secar al aire esta bien
- se puede secar superficialmente con paño suave
- guardarlo limpio y protegido

## Sensor SEN0710

### Para que sirve

Mide:

- turbidez `NTU`
- temperatura

### Antes de usar

- quitar la cubierta negra protectora antes de medir

### Buenas practicas de uso

- sumergirlo correctamente en la muestra
- evitar golpes en la zona optica
- no rayar ni frotar fuerte la ventana de medicion

### Limpieza

Si se uso en agua con tierra, lodo o sedimentos:

1. enjuagar con agua limpia
2. si quedan residuos, limpiar muy suavemente con microfibra humeda
3. dejar secar al aire o secar por fuera con paño suave

Evitar:

- cepillos duros
- abrasivos
- alcoholes o quimicos agresivos
- frotar fuerte la zona optica

### Sensibilidad

Es un sensor optico, por lo que:

- residuos en la ventana alteran la lectura
- rayones o suciedad persistente pueden afectar la medicion

## Si se usan en agua con tierra

Si cualquiera de los dos sensores se usa en agua con tierra:

1. no guardarlos sucios
2. enjuagar inmediatamente despues de la prueba
3. retirar residuos visibles
4. secar superficialmente
5. guardarlos protegidos

## Si se usan en agua con sal

Especialmente para el `SEN0707`:

1. enjuagar con agua limpia despues de la medicion
2. no dejar residuos salinos secos pegados
3. revisar que la zona sensora quede limpia antes de guardarlo

## Que no hacer

- no dejarlos chocando entre si o contra superficies duras
- no invertir `A` y `B` sin verificar
- no compartir direccion Modbus entre ambos en el mismo bus
- no usar fuentes de alimentacion inestables
- no guardar el sensor con barro o sales pegadas

## Pruebas recomendadas

### SEN0707

```bash
python3 rs485_ec_sensor.py --port /dev/ttyUSB0 --address 1 --json --count 5 --interval 2
```

### SEN0710

```bash
python3 rs485_turbidity_sensor.py --port /dev/ttyUSB0 --address 2 --json --count 5 --interval 2
```

## Configuracion recomendada final

- `SEN0707`: direccion `1`, baudrate `4800`
- `SEN0710`: direccion `2`, baudrate `4800`

## Recomendacion final

Siempre que se vaya a hacer una medicion seria:

1. revisar limpieza del sensor
2. revisar cableado
3. verificar direccion Modbus correcta
4. hacer una lectura corta de prueba
5. solo despues usar el sistema principal y Node-RED
