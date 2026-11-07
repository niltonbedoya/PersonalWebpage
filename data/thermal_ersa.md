# Ersa — Sistemas termicos: soldadura selectiva, por ola y refusion por conveccion

## Alcance y aplicacion
Documento tecnico de referencia para los sistemas de soldadura y procesos termicos de la marca Ersa, utilizados en ensamblaje electronico SMT y THT. Cubre soldadura selectiva (mini-wave y multi-dip), soldadura por ola (wave soldering) y hornos de refusion por conveccion. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Soldadura selectiva
- Funcion: soldadura de componentes THT y de terminaciones selectivas en placas con componentes mixtos, aplicando soldadura solo en zonas determinadas sin afectar componentes sensibles al calor cercanos.
- Metodo mini-wave: generacion de una onda de soldadura localizada de pequeno diametro que se posiciona sobre las terminaciones a soldar, controlada por movimiento CNC de la placa o de la boquilla.
- Metodo multi-dip: inmersion sucesiva de varias terminaciones en una onda de soldadura estatica, adecuado para placas con patrones de soldadura repetitivos.
- Aplicacion tipica: ensamblajes mixtos SMT/THT donde componentes ya montados no pueden exponerse al calor de una ola completa o de un horno de refusion.
- Parametros clave: temperatura de la ola, tiempo de inmersion, altura de la ola, velocidad de avance de la placa, flujo de flujo (flux) aplicado previamente.

## Soldadura por ola (wave soldering)
- Funcion: soldadura masiva de componentes THT pasando la placa sobre una ola de soldadura fundida que humecta las terminaciones y los orificios metalizados.
- Metodo: la placa se desplaza sobre una ola de estaño-aleacion mantenida a temperatura controlada; precalentamiento previo y aplicacion de flujo antes del contacto con la ola.
- Fases del proceso: aplicacion de flujo (fluxing), precalentamiento de la placa, contacto con la ola de soldadura, enfriamiento.
- Parametros clave: temperatura de la ola, velocidad de transporte de la placa, tiempo de precalentamiento, temperatura maxima de la placa, angulo de inclinacion de la ola.
- Control de calidad: inspeccion visual y optica despues de la ola para detectar puentes, soldadura insuficiente y defectos de humectacion.

## Horno de refusion por conveccion
- Funcion: fundicion controlada de la pasta de soldar depositada en pastillas SMT para formar uniones electricas y mecanicas fiables.
- Metodo: la placa avanza por zonas de temperatura controlada mediante aire caliente en recirculacion, siguiendo un perfil termico programado.
- Zonas del horno: precalentamiento, zona de remojo (soak), zona de refusion (reflow), zona de enfriamiento.
- Parametros clave: temperatura maxima de pico (peak temperature), tiempo sobre liquidus (TAL), ritmo de ascenso y descenso de temperatura, tiempo total del proceso.
- Aplicacion tipica: soldadura de componentes SMT despues de la serigrafia de pasta y el colocacion de componentes.

## Perfil termico y control de proceso
- El perfil termico debe optimizarse para cada producto segun la masa termica de la placa, el tipo de componente y la aleacion de soldadura.
- Monitorizacion mediante sensores de temperatura colocados en placas de prueba que recorren el horno, generando una curva de temperatura frente al tiempo.
- Analisis de la curva para verificar cumplimiento de los limites de temperatura de componentes y de los requisitos de la aleacion de soldadura.

## Seguridad termica
- Equipos con zonas de alta temperatura protegidas por barreras fisicas y sensores de puerta que detienen el proceso ante apertura no autorizada.
- Sistemas de extraccion de humos y vapores de flux para mantener la calidad del aire en el area de trabajo.
- Equipamiento de proteccion individual para operadores que manipulen placas calientes o componentes de la maquina en temperatura.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.