# Proyecto GitHub: CardioNutri — Asistente Clínico & Nutricional Inteligente

## Resumen del Proyecto
Aplicación móvil nativa para Android desarrollada por Nilton Bedoya con React Native y Expo SDK, diseñada para el seguimiento integral de la salud cardiovascular, adherencia farmacológica, nutrición de precisión guiada por modelos de visión multimodal con AI y sincronización de actividad física con relojes inteligentes y sensores deportivos mediante Health Connect.

## Características Principales

### 1. Panel Clínico Semanal (HomeScreen)
- Monitorización de 7 días con 4 tarjetas compactas y gráficos vectoriales SVG matemáticamente calibrados:
  - **Evolución Hídrica**: Seguimiento diario de ingesta de agua frente a metas personalizadas (2.0L - 2.2L).
  - **Pasos Diarios**: Registro de actividad física frente a objetivos clínicos (meta 6.000 pasos).
  - **Frecuencia Cardíaca**: Pulso en reposo, actual y rango mín-máx en tiempo real.
  - **Tensión Arterial**: Traza dual de presión sistólica y diastólica con semáforo médico oficial (guías ESH/ESC y ARA-II <130/80 mmHg).
- Diseño responsivo en cuadrícula 2x2 optimizado para pantallas de 360dp de ancho lógico.
- Métricas 100% reales sin simulación sintética: estados limpios cuando no hay mediciones recientes.

### 2. Sincronización con Sensores y Wearables (Health Connect)
- Integración oficial con la API de Health Connect en Android para sincronizar de forma transparente pasos (`Steps`) y frecuencia cardíaca (`HeartRate` y `RestingHeartRate`) desde relojes deportivos y pulseras de actividad.
- Sincronización automática en segundo plano al iniciar la app.

### 3. Módulo de Salud y Adherencia Terapéutica
- Registro estructurado de tomas de tensión (sistólica, diastólica, pulso) con clasificación automática (Óptima, Elevada, Hipertensión Grado 1/2, Crisis).
- Control matinal de adherencia farmacológica en un toque.
- Monitor dinámico de colesterol y analíticas de sangre con extracción inteligente por visión multimodal.

### 4. Inteligencia Artificial Multimodal en Nutrición
- Análisis de cartas de restaurantes y menús mediante fotografía con modelos de visión.
- Detección y veto clínico riguroso de platos por exceso de sodio (hipertensión), purinas (ácido úrico) o grasas saturadas.
- Planificador semanal de comidas con adaptación de raciones para adultos y niños, y generador de recetas anti-desperdicio según ingredientes de la despensa.

### 5. Chat Clínico Contextual 360°
- Asistente médico conversacional que razona integrando el historial completo del usuario: pasos reales, pulso, tomas de tensión, medicación activa y analíticas recientes.

## Stack Tecnológico
- **Framework Móvil**: React Native con Expo SDK.
- **Gráficos**: React Native SVG para renderizado vectorial ultraligero de curvas y barras.
- **Sensores de Salud**: Health Connect API nativa.
- **Modelos de Visión**: Modelos de AI multimodal para análisis de imágenes médicas y menús.
- **Persistencia**: AsyncStorage y base de datos local bajo arquitectura offline-first.
- **Validación de Datos**: Zod (Schema Driven Development) para esquemas médicos estrictos.
- **Testing**: Jest y React Native Testing Library con cobertura completa de pruebas unitarias.
