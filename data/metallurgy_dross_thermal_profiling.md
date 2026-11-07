# Metalurgia y materiales — Control de dross y perfilado termico

## Alcance y aplicacion
Documento tecnico de referencia sobre control de escoria (dross) en procesos de soldadura por ola y selectiva, y perfilado termico de hornos de refusion (Ramp-to-Soak, Time Above Liquidus - TAL). Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Control de dross (escoria) en soldadura por ola y selectiva
- Definicion: el dross es la capa de oxidos y aleacion solidificada que se forma en la superficie de la ola de soldadura fundida por exposicion al aire y al calor.
- Origen: oxidacion del estaño y de otros componentes de la aleacion al contacto con el oxigeno del ambiente, acelerada por altas temperaturas y por agitacion de la ola.
- Impacto en el proceso: el dross acumulado reduce la calidad de la humectacion, genera puentes y soldadura insuficiente, y consume aleacion valiosa que pasa a residuo.
- Medidas de control:
  * Remocion mecanica periodica de la escoria superficial de la ola con herramientas adecuadas.
  * Uso de atmosfera inerte (nitrogeno, N2) sobre el crisol y la ola para reducir la oxidacion y la formacion de dross.
  * Control de temperatura de la ola dentro del rango recomendado; temperaturas excesivas aceleran la formacion de dross.
  * Adicion controlada de aleacion fresca para reponer el estaño consumido y mantener la composicion del baño.
  * Uso de agentes reductores de dross aprobados, segun la aleacion y el equipo.
- Gestion de residuos: el dross retirado contiene aleacion recuperable que puede refinarse; gestionar como residuo industrial segun normativa local.

## Perfilado termico de hornos de refusion
- Definicion: el perfil termico es la curva de temperatura de una placa o de un sensor de temperatura a lo largo del tiempo mientras recorre el horno de refusion.
- Objetivo: fundir la pasta de soldar de forma controlada, alcanzando una temperatura suficiente para la humectacion sin dañar componentes ni la placa.

## Ramp-to-Soak (calentamiento con remojo)
- Estrategia de perfil con una fase de calentamiento gradual (rampa) seguida de una zona de temperatura estable o quasi-estable (remojo/soak) antes de la refusion.
- Fases:
  1. Precalentamiento: ascenso controlado de temperatura desde ambiente hasta la zona de remojo, evitando choques termicos y permitiendo la evaporacion de solventes del flux.
  2. Remojo (soak): mantenimiento en un rango de temperatura intermedio (tipicamente 150-200 °C) durante un tiempo definido, para igualar la temperatura de todos los componentes y activar el flux de forma uniforme.
  3. Refusion: ascenso rapido a la temperatura de pico por encima del punto de fusion de la aleacion, fundiendo la pasta y formando las uniones.
  4. Enfriamiento: descenso controlado para solidificar las uniones sin generar tensiones termicas excesivas.
- Ventajas: reduce variaciones de temperatura entre componentes de diferentes masas termicas, mejora la reproducibilidad del proceso y minimiza defectos como el tombstoning.

## Time Above Liquidus (TAL)
- Definicion: tiempo durante el cual la temperatura de la unión de soldadura se mantiene por encima de la temperatura liquida (liquidus) de la aleacion, es decir, en estado fundido.
- Importancia: un TAL insuficiente produce uniones frias o humectacion incompleta; un TAL excesivo puede dañar componentes sensibles al calor y acelerar el crecimiento de metaluras intermetalicas.
- Rangos tipicos: depende de la aleacion. Para SAC305, valores comunes entre 30 y 90 segundos sobre los 217 °C aproximadamente, segun el diseno de la placa y los requisitos del producto.
- Parametros relacionados: temperatura de pico (peak temperature), tiempo total por encima de umbrales de temperatura, ritmo de enfriamiento.

## Medicion y verificacion del perfil
- Uso de sensores de temperatura (termocuplas) fijados en puntos representativos de placas de prueba que recorren el horno.
- Registro de la curva temperatura-tiempo y comparacion contra el perfil de referencia y contra los limites de temperatura de los componentes mas sensibles.
- Ajuste de zonas de temperatura y de velocidad de transporte del horno para llevar el perfil medido dentro del perfil objetivo.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.