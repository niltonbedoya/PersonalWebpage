# MPM — Impresoras de serigrafia de pasta de soldar (AccuFlex, Momentum)

## Alcance y aplicacion
Documento tecnico de referencia para las impresoras de serigrafia de pasta de soldar de la marca MPM (ITW EAE), utilizadas en lineas de ensamblaje SMT para el deposito controlado de pasta de soldar sobre placas de circuito impreso. Cubre los modelos AccuFlex y Momentum, alineacion por vision y control reologico de la pasta. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Funcion principal
- Deposito de pasta de soldar sobre las pastillas de soldadura de la PCB mediante una plantilla (stencil) y una rasqueta (squeegee).
- Control del volumen, la forma y la posicion de cada deposito de pasta para garantizar una soldadura correcta en el posterior proceso de colocacion y refusion.
- Aplicacion en lineas de alta mezcla y produccion en gran volumen, con cambio rapido de plantilla y receta de producto.

## Modelos AccuFlex y Momentum
- AccuFlex: plataforma flexible de impresion de alta precision para placas de tamano variable, con alineacion por vision y control de parametros de impresion en tiempo real.
- Momentum: sistema de impresion de alto rendimiento disenado para produccion continua, con capacidades de alimentacion automatica de placas y recuperacion de errores sin parada de linea.

## Metodo de impresion por serigrafia
1. Colocacion de la placa sobre el soporte de impresion (pallet o sistema de sujecion por vacio).
2. Alineacion de la plantilla de acero sobre la placa mediante sistema de vision que registra marcas de registro (fiducials).
3. Deposito de pasta de soldar sobre la plantilla y barrido con rasqueta para forzar el paso de la pasta a travez de los aberturas de la plantilla hacia las pastillas de la PCB.
4. Elevacion de la plantilla y liberacion controlada de los depositos de pasta sobre la placa.
5. Inspeccion optica opcional de los depositos antes del avance de la placa a la estacion de colocacion.

## Parametros clave de impresion
- Presion de rasqueta: fuerza aplicada sobre la pasta, ajustada segun la reologia de la pasta y el diseno de la plantilla.
- Velocidad de rasqueta: ritmo de barrido, influye en el volumen de pasta depositado y en el tiempo de ciclo.
- Distancia de separacion (snap-off): distancia entre la plantilla y la placa tras el paso de la rasqueta, afecta a la liberacion de la pasta.
- Angulo de rasqueta: inclinacion de la rasqueta respecto a la plantilla, optimizada para cada tipo de pasta y plantilla.
- Frecuencia de limpieza de plantilla: intervalo de limpieza automatica para evitar acumulacion de pasta y defectos de puente o deposito insuficiente.

## Alineacion por vision
- Camaras que detectan marcas de registro en la PCB y en la plantilla para calcular el desplazamiento y corregir la posicion antes de la impresion.
- Correccion de distorsion y de expansion termica de la placa y de la plantilla.
- Verificacion de presencia y posicion de los depositos despues de la impresion, con rechazo automatico de placas fuera de tolerancia.

## Control reologico de la pasta de soldar
- La pasta debe mantener una viscosidad adecuada durante la impresion para evitar goteo o depositos incompletos.
- Parametros de control: tiempo de vida en la plantilla (open time), recuperacion de viscosidad tras el mezclado, comportamiento sin colapso (slump) despues del deposito.
- Monitoreo de temperatura y humedad del entorno de impresion, que afectan el comportamiento de la pasta.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.