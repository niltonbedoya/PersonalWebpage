# Parmi — 3D SPI, 3D AOI y PCI para inspeccion de barnizado

## Alcance y aplicacion
Documento tecnico de referencia para los sistemas de inspeccion de la marca Parmi, utilizados en lineas de ensamblaje SMT/THT. Cubre inspeccion de pasta de soldar (SPI), inspeccion optica automática de componentes y soldadura (AOI) e inspeccion de barnizado conformal (PCI). Contenido tecnico sanitizado sin datos de clientes ni credenciales.

## 3D SPI — Inspeccion de pasta de soldar
- Funcion: verificacion de volumen, area, altura y posicion de depositos de pasta de soldar antes del colocacion de componentes.
- Metodo: escaneo 3D estructurado de luz que reconstruye la topografia de cada deposito sobre la pastilla de soldadura.
- Parametros clave: volumen de pasta, altura maxima, area de contacto, offset lateral respecto al pad, forma del deposito.
- Umbrales de aceptacion: desviacion de volumen +/- 15 % respecto al valor nominal; altura dentro del rango de proceso definido; no puentes entre pads adyacentes.
- Aplicacion tipica: control de calidad previo al reflow en lineas de alta mezcla y bajo volumen, y en produccion de gran volumen con trazas de proceso.

## 3D AOI — Inspeccion optica automatica de componentes y soldadura
- Funcion: deteccion de defectos de colocacion de componentes, soldadura insuficiente, puentes, componentes faltantes, inversiones de polaridad y elevacion de terminales (tombstoning).
- Metodo: camaras multiespectrales con proyeccion 3D que generan un mapa de alturas de la placa y comparan contra una placa de referencia (golden board) o datos CAD.
- Defectos detectables: desplazamiento (shift), rotacion (skew), elevacion (lift), puente de soldadura (bridge), soldadura insuficiente (insufficient solder), componente ausente (missing component), componente erroneo (wrong component).
- Resolucion minima: depende de la configuracion de optica, tipicamente capaz de resolver componentes 0201 y mas pequeños con camaras de alta resolucion.
- Velocidad de inspeccion: expresada en cm2 por segundo, variable segun la densidad de componentes y el umbral de defecto configurado.

## PCI — Inspeccion de barnizado conformal
- Funcion: verificacion de cobertura, espesor y uniformidad del barnizado conformal aplicado sobre ensamblajes electronicos.
- Metodo: inspeccion optica con iluminacion UV y blanca, con medicion de espesor mediante sensor de altura, para detectar zonas sin cobertura, burbujas y espesor fuera de tolerancia.
- Parametros clave: espesor de pelicula (micras), cobertura porcentual de la superficie objetivo, presencia de burbujas o grietas, adherencia del material.
- Aplicacion: proteccion de ensamblajes expuestos a humedad, polvo y agentes quimicos en entornos industriales y automotrices.

## Flujo de control de calidad
El flujo tipico en una linea SMT combina los tres sistemas en secuencia: SPI despues de la serigrafia, AOI despues del colocacion y despues del reflow, y PCI despues de la aplicacion de barnizado conformal cuando este sea requerido. Los resultados de cada estacion se registran en el historial de trazas de la placa para analisis de tendencia y acciones correctivas.

## Limitaciones del alcance
Este documento no cubre maquinas de insercion Pick & Place, fuera del alcance definido por la spec del proyecto. No se incluyen nombres de clientes, numeros de serie, direcciones de correo electronico, credenciales ni claves de API.
