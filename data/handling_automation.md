# Handling y automatizacion — Cargadores, descargadores, buffers, transportadores y diagnostico de PLC

## Alcance y aplicacion
Documento tecnico de referencia sobre equipos de manipulacion y automatizacion en lineas de ensamblaje electronico SMT/THT. Cubre cargadores (loaders), descargadores (unloaders), buffers, cintas transportadoras y sistemas de diagnostico de PLC. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Cargadores (loaders)
- Funcion: alimentar placas de circuito impreso (PCB) al inicio de la linea de produccion, apiladas o individualmente, hacia la primera estacion de proceso.
- Metodo: elevacion de placas desde un paleta o estante mediante mecanismo de transporte (correa, cadena o sistema de vacuo) y entrega a la cinta transportadora de la linea.
- Caracteristicas: ajuste de ancho de placa, sensores de presencia de placa, control de velocidad de alimentacion y apilado ordenado de placas vacias despues del proceso.

## Descargadores (unloaders)
- Funcion: recibir placas al final de la linea y apilarlas o colocarlas en una paleta de salida de forma ordenada.
- Metodo: recogida de placas de la cinta transportadora y deposito en una pila de salida o en un estante, con control de alineacion y deteccion de placas dobles o faltantes.
- Caracteristicas: ajuste de ancho, sensor de fin de pila, senal de linea llena y interface de senales con el resto de equipos.

## Buffers (almacenes intermedios)
- Funcion: almacenar temporalmente placas entre estaciones de proceso para desacoplar estaciones con tiempos de ciclo diferentes y evitar paradas en cadena.
- Metodo: almacenamiento vertical u horizontal de placas en ranuras o estantes, con entrada y salida controladas por el sistema de transporte de la linea.
- Tipos: buffer de accumulation (almacena placas hasta que la estacion siguiente esta libre) y buffer de sequenciacion (mantiene el orden de las placas para trazabilidad).
- Ventajas: permite que una estacion de inspeccion lenta no detenga el resto de la linea, y absorbe variaciones en los tiempos de proceso.

## Cintas transportadoras (conveyors)
- Funcion: transporte de placas entre estaciones de proceso con posicionamiento repetible y control de velocidad.
- Metodo: cintas, cadenas o rodillos que moven la placa en una direccion definida, con paradas precisas en cada estacion y senales de presencia de placa.
- Caracteristicas: ancho ajustable para diferentes tamanos de placa, control de velocidad variable, sensores opticos o inductivos de presencia de placa, y interface de senales para sincronizacion con equipos de proceso.
- Aplicacion en hornos de refusion, soldadura por ola, estaciones de inspeccion y zonas de reproceso.

## Diagnostico de PLC
- Funcion: programacion, monitoreo y diagnostico de los controladores logicos programables (PLC) que gobiernan los equipos de la linea de automatizacion.
- Metodo: conexion al PLC mediante puerto de comunicacion (serie, Ethernet o bus de campo) para leer el estado de entradas y salidas, el valor de registros y temporizadores, y el historial de alarmas.
- Elementos diagnosticados: estado de sensores (presencia de placa, fin de carrera, fotoelectricos), estado de actuadores (motores, electrovalvulas, cilindros neumaticos), tiempos de ciclo de cada estacion, interbloqueos de seguridad y mensajes de alarma.
- Alarmas tipicas: placa no detectada, estacion bloqueada, error de comunicacion, sensor fuera de rango, parada de emergencia activada, fin de pila en descargador.
- Herramientas: software de programación del PLC, paneles operador (HMI) y equipos de diagnostico portatiles para lectura de errores en campo.

## Integracion de equipos en la linea
- Los equipos de handling se sincronizan mediante senales de entrada/salida (I/O) o mediante bus de campo, asegurando que cada estacion procese una placa solo cuando la estacion anterior haya terminado y la siguiente este lista.
- El sistema de control central coordina el flujo de placas, gestiona los buffers y registra eventos de produccion para trazabilidad y analisis de eficiencia global del equipo (OEE).

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.