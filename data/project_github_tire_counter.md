# Proyecto GitHub: Tire Counter Monorepo

## Resumen del Proyecto
Sistema integral de clasificación, conteo y despacho de neumáticos desarrollado por Nilton Bedoya como monorepo TypeScript. Implementa una arquitectura offline-first con máquina de estados finitos (FSM) de lotes, compresión WebP, validación OpenXML (.xlsx) y sincronización con Supabase.

## Arquitectura y Monorepo
- `packages/core-contracts`: Contratos tipados con Zod, FSM de estados de lote, esquemas i18n y repositorio híbrido offline-first.
- `apps/receptor-desktop`: Estación de recepción y validación de despachos construida con Fastify y React.
- `tools/mcp-servers`: 4 servidores basados en Model Context Protocol (MCP) para testing y auditoría automatizada:
  - `mcp-sqlite-inspector`: Auditoría de DDL y esquemas SQLite locales, consulta de estado de contenedores y aislamiento de bóveda.
  - `mcp-image-qa`: Validación de calidad de imágenes WebP (dimensiones <= 1280px, peso < 150KB, verificación de compresión).
  - `mcp-openxml-validator`: Validación estructural de manifiestos y archivos Excel (.xlsx) de despacho contra datos de SQLite.
  - `mcp-fs-sandbox`: Monitoreo de almacenamiento seguro, purga atómica y control de bloqueos de archivo.

## Flujo de Despacho (FSM)
1. ACTIVO: El operario cuenta y clasifica neumáticos.
2. BLOQUEADO_EN_BOVEDA: Bloqueo de UI e inmutabilidad de la bóveda de datos.
3. DESPACHADO_PENDIENTE_ACK: Generación de paquete comprimido .zip (Excel .xlsx + imágenes WebP) con hash criptográfico SHA-256.
4. CONFIRMADO_EN_DESTINO: Validación y confirmación del recibo por parte del supervisor en destino.
5. PURGADO: Purga física y atómica de imágenes y datos temporales para liberar almacenamiento.

## Stack Tecnológico
- TypeScript 5.9+ (modo estricto).
- Fastify (backend de alto rendimiento en receptor de escritorio).
- React (frontend interactivo para operarios y supervisores).
- SQLite (persistencia transaccional local) + Supabase/PostgreSQL (sincronización cloud).
- ExcelJS + JSZip (generación y validación de manifiestos OpenXML).
- Zod 3.24+ (validación rigurosa de esquemas en tiempo de ejecución).
- Vitest (suite de pruebas unitarias y de integración).
- Model Context Protocol (MCP) para integración de herramientas de auditoría.
