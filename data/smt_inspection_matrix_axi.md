# Matrix — Inspeccion por Rayos X en linea (AXI)

## Alcance y aplicacion
Documento tecnico de referencia para los sistemas de inspeccion automatica por Rayos X (AXI) de la marca Matrix, utilizados en lineas de ensamblaje electronico SMT. Cubre la inspeccion no destructiva de uniones de soldadura ocultas bajo componentes de montaje en superficie, como BGA, QFN, QFP y otros encapsulados con terminaciones no visibles. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Funcion principal
- Inspeccion de uniones de soldadura ocultas bajo el cuerpo del componente donde la inspeccion optica 2D o 3D no puede alcanzar.
- Deteccion de defectos internos como puentes de soldadura, soldadura insuficiente, vaciados (voiding), desplazamiento de componente y faltante de bola de soldadura en BGA.
- Verificacion de integridad de uniones en componentes de terminacion oculta y de alta densidad de interconexion.

## Metodo de inspeccion
- Emision de rayos X desde una fuente direccionada hacia la placa, con un detector plano del lado opuesto que captura la imagen de transmision.
- Reconstruccion de la imagen en 2D o 3D (tomografia computada opcional) que muestra la distribucion de material de soldadura y la posicion relativa de las terminaciones del componente.
- Diferenciacion de materiales segun su densidad atomica: el estaño y el plomo de la soldadura absorben rayos X de forma distinta a la resina del componente y al substrato de la placa, generando contraste en la imagen.
- Angulo de incidencia configurable (inspeccion oblique) para visualizar uniones laterales y paredes de via en componentes QFN y similares.

## Defectos detectables
- Puente de soldadura entre bolas adyacentes o entre bola y pad vecino.
- Soldadura insuficiente o falta de humectacion en una o varias bolas de BGA.
- Vaciados (voiding) dentro de la union de soldadura, expresados como porcentaje del area total de la union.
- Desplazamiento lateral del componente respecto al patron de pads (component shift).
- Bola de soldadura ausente (missing ball).
- Componentes inclinados o elevados (tilt, tombstoning).
- Grietas en la union de soldadura o en el substrato cercano a la zona soldada.

## Parametros de configuracion
- Voltaje y corriente del tubo de rayos X, ajustados segun el espesor del substrato y el material de los componentes.
- Tiempo de exposicion y numero de frames promedios, que afectan al ruido de la imagen y al tiempo de ciclo de inspeccion.
- Magnificacion optica y resolucion del detector, determinadas por el tamano de caracteristica a inspeccionar (por ejemplo diametro de bola de BGA).
- Umbrales de aceptacion de vaciados y de area de soldadura, definidos por ingenieria de calidad segun el producto.

## Seguridad radiologica
- Equipo blindado con puertas de seguridad y sensores de presencia que detienen la emision de rayos X cuando la camara esta abierta.
- Niveles de radiacion fuera del equipo por debajo de los limites normativos para areas de trabajo, verificados periodicamente por servicio de proteccion radiologica.
- Operadores entrenados y equipamiento de monitorizacion personal cuando proceda segun la normativa local.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.