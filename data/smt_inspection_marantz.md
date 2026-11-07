# Marantz — Inspeccion optica 2D SMD y THT pre y post-reflow

## Alcance y aplicacion
Documento tecnico de referencia para los sistemas de inspeccion optica 2D de la marca Marantz, utilizados en lineas de ensamblaje electronico SMT y THT. Cubre inspeccion pre-reflow y post-reflow de componentes montados en superficie y de tecnologia de agujero atraves. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Inspeccion 2D pre-reflow
- Funcion: verificacion de presencia, posicion y orientacion de componentes SMD y THT despues del colocacion y antes del proceso de refusion por calor.
- Metodo: iluminacion sincronizada y camaras de alta resolucion que capturan imagenes bidimensionales de la placa y comparan regiones de interes contra una imagen de referencia o modelo CAD.
- Defectos detectables: componente ausente, componente desalineado, componente invertido, componente rotado, terminal elevada, presencia de cuerpo estranho sobre la placa.
- Aplicacion tipica: deteccion temprana de errores de colocacion antes de que la placa pase por el horno de refusion, reduciendo desperdicio de material y tiempo de reprocesamiento.

## Inspeccion 2D post-reflow
- Funcion: verificacion de calidad de las uniones de soldadura despues del proceso de refusion, deteccion de puentes, soldadura insuficiente y componentes desplazados por el calor.
- Metodo: analisis de imagen 2D con algoritmo de procesamiento de senales que evalua la forma, el brillo y el contorno de cada junta de soldadura y de cada componente.
- Defectos detectables: puente de soldadura entre pads adyacentes, soldadura insuficiente (unión incompleta), exceso de soldadura, componente tombstoned, componente desalineado despues del reflow, pista levantada.
- Aplicacion tipica: control final de calidad antes de que el ensamblaje avance a las estaciones siguientes de la linea de produccion.

## Diferencias entre inspeccion SMD y THT
- SMD: componentes montados sobre la superficie de la placa, inspeccion focada en pads de soldadura superficiales y cuerpos de componentes de bajo perfil.
- THT: componentes con terminales que atraviesan la placa, inspeccion focada en la soldadura por el lado opuesto de la placa y en la integridad del orificio metalizado.
- Los sistemas 2D de Marantz admiten configuracion de recetas independientes por tipo de componente y por familia de placa, permitiendo cambio rapido de producto en lineas de alta mezcla.

## Parametros de configuracion
- Resolucion de camara: seleccionable segun el tamano minimo de componente a inspeccionar (por ejemplo 0402, 0603, 0805 en metrica imperial).
- Iluminacion: coaxial, oblique o de campo oscuro segun el tipo de refliccion requerida para destacar defectos de soldadura.
- Umbral de aceptacion: definido por ingenieria de calidad en funcion de los requisitos del producto y del nivel de riesgo aceptable.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.