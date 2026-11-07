# Metricas de ingeniería y notas de metodologia

## Alcance y aplicacion
Documento de referencia sobre metricas de ingeniería y notas de metodologia para procesos industriales SMT/THT y proyectos de software. Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## Metricas de procesos industriales SMT/THT
- Rendimiento de primera pasada (First Pass Yield - FPY): porcentaje de placas que pasan todas las estaciones de inspeccion sin requerir reproceso. FPY = (placas aprobadas en primera pasada / placas totales producidas) x 100.
- Tasa de defectos por millones de oportunidades (DPMO): metrica de calidad que normaliza la cantidad de defectos frente al numero de oportunidades de defecto en una placa. DPMO = (numero de defectos / (numero de unidades x oportunidades por unidad)) x 1,000,000.
- Tiempo medio entre fallas (MTBF): intervalo medio entre fallas consecutivas de un equipo de linea, usado para planificacion de mantenimiento preventivo.
- Tiempo medio de reparacion (MTTR): tiempo medio necesario para restaurar un equipo despues de una falla, incluyendo diagnostico y reparacion.
- Eficiencia global del equipo (OEE): producto de disponibilidad, rendimiento y calidad. OEE = disponibilidad x rendimiento x calidad. Mide el aprovechamiento real de los equipos de produccion.
- Volumen de pasta depositado: metrica de control de serigrafia que verifica que cada deposito esta dentro del rango de volumen aceptable, reduciendo puentes y soldadura insuficiente.
- Vaciados en uniones BGA (voiding): porcentaje del area de una union de soldadura ocupada por vacios, medido por inspeccion por Rayos X. Umbrales de aceptacion definidos por producto.

## Metricas de proyectos de software (casos de estudio anonimizados)
- Tiempo medio de primera respuesta: intervalo entre la creacion de un ticket y la primera intervencion de un tecnico, medido por prioridad y categoria.
- Tiempo medio de resolucion: intervalo entre apertura y cierre de un ticket, desagregado por categoria y prioridad.
- Porcentaje de cumplimiento de SLA: tickets resueltos dentro del tiempo comprometido sobre el total de tickets.
- Rotacion de inventario: numero de veces que el inventario de un articulo se repondra en un periodo, para casos de logistica.
- Latencia de extremo a extremo en pipeline de traduccion: tiempo transcurrido entre la captura de un segmento de audio y la disponibilidad del subtitulo traducido, medido en milisegundos.
- Tasa de disponibilidad del sistema: porcentaje de tiempo que un servicio permanece operativo dentro de un periodo de medicion.

## Notas de metodologia de ingeniería
- Definicion de indicadores antes de iniciar la medicion: cada metrica debe tener un objetivo, una fuente de datos y una frecuencia de registro clara.
- Trazabilidad de datos: los registros de medicion deben conservar el contexto (fecha, operador, equipo, producto) para permitir analisis de raiz de problemas.
- Analisis de tendencia: las metricas se revisan periodicamente para detectar desviaciones graduales y aplicar acciones correctivas antes de que afecten la calidad.
- Validacion de procesos: antes de introducir un cambio en una linea de produccion o en un software, se ejecuta una validacion con datos de prueba y se comparan los resultados contra la linea base.
- Documentacion de decisiones de diseño: las decisiones arquitectonicas y los umbrales de aceptacion se registran con su justificacion para futura consulta y auditoria.

## Seguridad y anonimizacion en metrica
- Los valores de metrica presentados en este documento son illustrative o sinteticos, sin correspondencia con operaciones reales de clientes.
- No se incluyen nombres de empresas, direcciones de correo electronico, numeros de telefono, credenciales ni identificadores personales.
- Los casos de estudio de software usan entidades ficticias y datos generados para el caso.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.