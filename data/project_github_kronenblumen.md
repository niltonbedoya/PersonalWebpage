# Proyecto GitHub: ERP Comercial y Control de Importaciones — Aplicación Móvil y de Escritorio

## Resumen del Proyecto
Aplicación móvil y de escritorio diseñada para la gestión operativa y comercial de importación de mercancías y neumáticos por contenedores, control de inventario en patio y almacén, ventas en mostrador (POS) y facturación. Permite sustituir totalmente el papel en la operativa diaria con una interfaz optimizada para tablets y teléfonos.

## Módulos y Capacidades del Sistema
- **Control de Entrada por Contenedor**: Registro y desglose de furgones de importación, asignación de lotes y clasificación por medida, condición e inspección técnica.
- **Visión por Computador y AI en Patio**: Servicio de visión por AI (`AiVisionService`) para conteo automatizado de unidades apiladas en furgones mediante captura fotográfica, y lectura óptica de códigos DOT y dimensiones en el flanco.
- **Punto de Venta (POS) Táctil**: Catálogo interactivo con doble nivel de filtros acumulativos (aro, ancho, perfil, tipo de vehículo y carga reforzada LT/C), emisión de recibos en impresoras térmicas e integración de códigos QR en comprobantes.
- **Módulo de Devoluciones y Cambios**: Gestión de reintegros de mercancía al stock disponible sin duplicar ventas brutas, con recálculo automático de balances económicos según diferencia de precio.
- **Cierre de Turno y Arqueo de Caja**: Cuadre de caja por turno con deducción de reembolsos, comprobante Z con firma digital en pantalla y código QR de auditoría.
- **Trazabilidad de Auditoría**: Flujo de estados inmutables: entrada por contenedor -> inventario -> venta/devolución -> arqueo de caja.

## Stack Tecnológico
- **Frontend / Móvil**: Flutter para interfaz táctil en tablets y dispositivos móviles.
- **Backend**: NestJS estructurado bajo arquitectura de Monolito Modular con controladores y servicios de dominio.
- **Base de Datos**: PostgreSQL / Supabase con esquemas relacionales y Row Level Security (RLS).
- **Metodología y Calidad**: TDD riguroso (Test-Driven Development) con suites de prueba automatizadas en Jest y pipeline de CI en GitHub Actions.
