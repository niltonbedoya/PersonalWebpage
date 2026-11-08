# Proyecto GitHub: Traductor Simultáneo en Tiempo Real

## Resumen del Proyecto
Aplicación de traducción y transcripción de voz continua de baja latencia diseñada para eventos técnicos, conferencias multilingües y reuniones de ingeniería de alta precisión.

## Capacidades y Flujo Operativo
- **Escucha y Traducción Continua**: Captura de señal de audio en directo desde micrófono, reconocimiento de habla y traducción de baja latencia entre múltiples pares de idiomas.
- **Síntesis de Voz (TTS)**: Reproducción de la traducción resultante con voz sintética sincronizada en tiempo real.
- **Registro Multipropósito**: Exportación de la sesión transcrita y traducida simultáneamente en formatos `TXT`, `PDF`, `JSON` y archivo de audio `WAV` con marcas de tiempo.
- **Monitor en Vivo**: Interfaz visual con visualización en dos columnas de frases originales y frases traducidas alineadas.
- **Vocabularios por Dominio Técnico y Phrase Lists**: Ingesta de listas de frases y glosarios especializados de ingeniería electrónica, maquinaria industrial y desarrollo de software para evitar traducciones erróneas de jerga técnica.
- **Perfiles de Acento**: Calibración para perfiles de habla en inglés con acentos regionales (francés, alemán, italiano).
- **Herramienta de Revisión de Vocabulario (`vocab_review.py`)**: Módulo para auditar sesiones pasadas, recortar clips de audio, escuchar segmentos dudosos y añadir automáticamente términos al vocabulario técnico.

## Stack Tecnológico
- Python 3.11+ con interfaces de usuario de escritorio.
- Motores de procesamiento de señal de voz, reconocimiento y síntesis de voz neuronal (TTS).
- Pipelines de exportación de documentos (ReportLab para PDF, serialización JSON estructurada).
- Scripts de automatización y empaquetado para distribución en entornos Windows sin dependencias externas.
